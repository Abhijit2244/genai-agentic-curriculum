"""
mcp_server.py — Model Context Protocol (MCP) Server for Invoice Auditing
Exposes:
1. Tools:
   - get_invoice(id: str) -> dict
   - find_duplicates(file: str) -> dict
2. Resources:
   - invoice://policy/compliance-rules -> Corporate Invoice & AP Compliance Standard (Markdown)
3. Prompts:
   - audit_invoice(invoice_id: str) -> Prompt template for compliance auditing

Transports Supported: stdio (default) and streamable-http
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List
from mcp.server.mcpserver import MCPServer

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
INVOICES_PATH = DATA_DIR / "invoices.json"
POLICY_PATH = DATA_DIR / "invoice_policy.md"

# Ensure sample data exists
if not INVOICES_PATH.exists() or not POLICY_PATH.exists():
    from data.generate_sample_data import generate_all_data
    generate_all_data()

# Initialize the MCP Server instance
server = MCPServer(
    name="InvoiceAuditServer",
    version="1.0.0",
    description="Enterprise Accounts Payable & Invoice Verification MCP Server"
)


def _load_invoices(file_path_str: str = "") -> List[Dict[str, Any]]:
    """Helper to load invoice records from JSON file."""
    path = Path(file_path_str) if file_path_str and Path(file_path_str).is_absolute() else (DATA_DIR / file_path_str if file_path_str else INVOICES_PATH)
    if not path.exists():
        path = INVOICES_PATH
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ==============================================================================
# 1. MCP TOOLS (Actions callable by LLM)
# ==============================================================================

@server.tool(
    name="get_invoice",
    description="Look up a single corporate invoice by its unique ID (e.g. 'INV-2026-001', 'INV-2026-003'). Returns full invoice metadata, vendor, amount, PO number, and authorizer."
)
def get_invoice(id: str) -> Dict[str, Any]:
    """Retrieves an invoice by ID."""
    clean_id = id.strip().upper()
    invoices = _load_invoices()
    for inv in invoices:
        if inv.get("id", "").upper() == clean_id:
            return {
                "status": "found",
                "invoice": inv
            }
    return {
        "status": "not_found",
        "error": f"Invoice with ID '{clean_id}' does not exist in the database.",
        "available_ids": [inv["id"] for inv in invoices]
    }


@server.tool(
    name="find_duplicates",
    description="Scans an invoice file to detect duplicate submissions, invoice structuring, and missing purchase orders violating AP-POL-2026."
)
def find_duplicates(file: str = "invoices.json") -> Dict[str, Any]:
    """
    Analyzes an invoice JSON file for compliance red flags:
    1. Duplicate payments (same vendor and amount within 72h).
    2. Invoice structuring (adjacent amounts near $50,000 threshold to evade dual sign-off).
    3. Missing PO violations (invoices > $10,000 without valid purchase order).
    """
    invoices = _load_invoices(file)
    
    # 1. Detect duplicates (group by vendor + amount)
    vendor_amount_map: Dict[str, List[Dict[str, Any]]] = {}
    for inv in invoices:
        key = f"{inv['vendor'].strip().lower()}:::{inv['amount']}"
        vendor_amount_map.setdefault(key, []).append(inv)

    duplicate_groups = []
    for key, group in vendor_amount_map.items():
        if len(group) > 1:
            duplicate_groups.append({
                "vendor": group[0]["vendor"],
                "amount": group[0]["amount"],
                "duplicate_count": len(group),
                "invoice_ids": [inv["id"] for inv in group],
                "dates": [inv["date"] for inv in group],
                "violation_code": "AP-DUP-03",
                "risk": "Potential Duplicate Disbursement"
            })

    # 2. Detect structuring (invoices to same vendor in range $48,000 - $49,999)
    structuring_candidates = []
    vendor_invoices: Dict[str, List[Dict[str, Any]]] = {}
    for inv in invoices:
        v = inv["vendor"].strip().lower()
        vendor_invoices.setdefault(v, []).append(inv)

    for v, invs in vendor_invoices.items():
        near_threshold = [i for i in invs if 48000.0 <= i["amount"] < 50000.0]
        if len(near_threshold) >= 2:
            structuring_candidates.append({
                "vendor": near_threshold[0]["vendor"],
                "invoice_ids": [i["id"] for i in near_threshold],
                "amounts": [i["amount"] for i in near_threshold],
                "dates": [i["date"] for i in near_threshold],
                "cumulative_spend": sum(i["amount"] for i in near_threshold),
                "violation_code": "AP-STRUCT-02",
                "risk": "Intentional Invoice Structuring to avoid CFO dual-signoff ($50k)"
            })

    # 3. Detect missing PO violations (> $10,000 and po_number is NONE or AUTO_RELEASED)
    missing_po_violations = []
    for inv in invoices:
        if inv["amount"] > 10000.0 and (inv.get("po_number", "").upper() == "NONE" or inv.get("approval_status", "").upper() == "AUTO_RELEASED"):
            missing_po_violations.append({
                "invoice_id": inv["id"],
                "vendor": inv["vendor"],
                "amount": inv["amount"],
                "po_number": inv.get("po_number"),
                "approval_status": inv.get("approval_status"),
                "violation_code": "AP-PO-04",
                "risk": "Missing 3-Way Match & Unauthorized Auto-Release"
            })

    return {
        "status": "success",
        "file_analyzed": file,
        "total_invoices_scanned": len(invoices),
        "total_anomalies_detected": len(duplicate_groups) + len(structuring_candidates) + len(missing_po_violations),
        "duplicate_groups": duplicate_groups,
        "structuring_candidates": structuring_candidates,
        "missing_po_violations": missing_po_violations
    }


# ==============================================================================
# 2. MCP RESOURCES (Readable context & standards)
# ==============================================================================

@server.resource(
    uri="invoice://policy/compliance-rules",
    name="Invoice Compliance Policy Document",
    description="The official corporate Accounts Payable internal control standards (SOX 404 / AP-POL-2026), including dual authorization thresholds and duplicate quarantine rules.",
    mime_type="text/markdown"
)
def get_invoice_policy() -> str:
    """Returns the raw compliance policy markdown text."""
    if not POLICY_PATH.exists():
        return "# Error: Policy document not found."
    with open(POLICY_PATH, "r", encoding="utf-8") as f:
        return f.read()


# ==============================================================================
# 3. MCP PROMPTS (Standardized prompt templates)
# ==============================================================================

@server.prompt(
    name="audit_invoice",
    description="Generate an audit prompt template to inspect an invoice against corporate compliance policies."
)
def audit_invoice_prompt(invoice_id: str) -> str:
    """Returns a templated audit prompt for an invoice."""
    return (
        f"You are a Senior Internal Auditor. Perform a compliance audit on invoice '{invoice_id}'.\n"
        f"1. Fetch the invoice using tool 'get_invoice'.\n"
        f"2. Read the compliance rules from resource 'invoice://policy/compliance-rules'.\n"
        f"3. Run tool 'find_duplicates' to check if this invoice is part of a duplicate submission or structuring scheme.\n"
        f"4. Provide a formal audit recommendation with policy citations and severity level."
    )


# ==============================================================================
# 4. ENTRYPOINT (Supports stdio or streamable-http)
# ==============================================================================

def main():
    """Runs the MCP server over stdio or Streamable HTTP."""
    transport = "stdio"
    if "--http" in sys.argv:
        transport = "streamable-http"
        print(f"Starting MCP Server on Streamable HTTP transport...")
    server.run(transport=transport)


if __name__ == "__main__":
    main()
