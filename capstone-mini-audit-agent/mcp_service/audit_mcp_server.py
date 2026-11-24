"""
audit_mcp_server.py — Model Context Protocol (MCP) Server for the Capstone
Exposes tools and resources to the LangGraph agent:
1. ocr_invoice: OpenCV preprocessing + OCR extraction
2. check_ledger_anomalies: Pandas ledger duplicate & structuring detection
3. search_compliance_policy: In-memory RAG over SOX 404 policies
4. submit_audit_findings: Official workpaper recording
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List
from mcp.server.mcpserver import MCPServer

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.ocr_engine import extract_invoice_fields
from core.ledger_analyzer import check_invoice_against_ledger
from core.policy_rag import retrieve_policy_context, DEFAULT_POLICY_PATH

server = MCPServer(
    name="CapstoneMiniAuditMCPServer",
    version="1.0.0",
    description="Enterprise Forensic Audit MCP Server exposing OCR, Ledger analysis, and Policy RAG"
)


# ==============================================================================
# 1. MCP TOOLS
# ==============================================================================

@server.tool(
    name="ocr_invoice",
    description="Preprocesses an invoice image with OpenCV and extracts structured financial fields (vendor, invoice_number, date, amount, PO number)."
)
def ocr_invoice(image_path: str) -> Dict[str, Any]:
    """Runs OpenCV preprocessing + OCR field extraction."""
    return extract_invoice_fields(image_path)


@server.tool(
    name="check_ledger_anomalies",
    description="Uses pandas to cross-reference an extracted invoice against general ledger records to detect duplicate submissions and threshold structuring."
)
def check_ledger_anomalies(
    ledger_csv_path: str,
    vendor: str,
    amount: float,
    invoice_id: str = ""
) -> Dict[str, Any]:
    """Scans ledger CSV for duplicates and structuring."""
    return check_invoice_against_ledger(
        ledger_csv_path=ledger_csv_path,
        vendor=vendor,
        amount=amount,
        invoice_id=invoice_id
    )


@server.tool(
    name="search_compliance_policy",
    description="Performs semantic vector search across internal accounting controls (SOX 404 / AP-POL-2026) to retrieve governing standards and violation codes."
)
def search_compliance_policy(query: str) -> List[Dict[str, Any]]:
    """Retrieves relevant compliance policy clauses."""
    return retrieve_policy_context(query=query, top_k=2)


@server.tool(
    name="submit_audit_findings",
    description="Commits the final verified audit exception into official audit workpapers after human approval."
)
def submit_audit_findings(
    invoice_id: str,
    vendor: str,
    amount: float,
    violation_code: str,
    severity: str,
    rationale: str,
    auditor_action: str
) -> Dict[str, Any]:
    """Logs the final approved audit exception record."""
    return {
        "status": "COMMITTED_TO_WORKPAPERS",
        "invoice_id": invoice_id,
        "vendor": vendor,
        "amount": amount,
        "violation_code": violation_code,
        "severity": severity,
        "rationale": rationale,
        "auditor_action": auditor_action
    }


# ==============================================================================
# 2. MCP RESOURCE
# ==============================================================================

@server.resource(
    uri="policy://sox404/standards",
    name="Corporate Accounts Payable Internal Controls Standard",
    description="The complete authoritative compliance policy document (SOX 404 / AP-POL-2026).",
    mime_type="text/markdown"
)
def get_compliance_policy_resource() -> str:
    """Returns the compliance policy markdown text."""
    with open(DEFAULT_POLICY_PATH, "r", encoding="utf-8") as f:
        return f.read()


def main():
    transport = "stdio"
    if "--http" in sys.argv:
        transport = "streamable-http"
    server.run(transport=transport)


if __name__ == "__main__":
    main()
