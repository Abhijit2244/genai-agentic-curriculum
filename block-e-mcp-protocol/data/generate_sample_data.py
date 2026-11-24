"""
Generates sample invoice data and compliance policy markdown for Block E (MCP).
Exposed via MCP Tools (get_invoice, find_duplicates) and MCP Resources (invoice_policy.md).
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
INVOICES_JSON_PATH = DATA_DIR / "invoices.json"
POLICY_MD_PATH = DATA_DIR / "invoice_policy.md"

SAMPLE_INVOICES = [
    {
        "id": "INV-2026-001",
        "vendor": "CloudMatrix Systems",
        "amount": 24500.00,
        "currency": "USD",
        "date": "2026-03-01",
        "po_number": "PO-2026-101",
        "approval_status": "APPROVED",
        "authorized_by": "VP_ENGINEERING",
        "description": "Monthly Kubernetes & Cloud Hosting Infrastructure",
        "payment_method": "ACH"
    },
    {
        "id": "INV-2026-002",
        "vendor": "Metropolis Legal LLP",
        "amount": 18200.00,
        "currency": "USD",
        "date": "2026-03-03",
        "po_number": "PO-2026-105",
        "approval_status": "APPROVED",
        "authorized_by": "GENERAL_COUNSEL",
        "description": "Q1 Regulatory Filings & IP Advisory",
        "payment_method": "WIRE"
    },
    # DUPLICATE PAIR 1 (Identical vendor, amount, date, and description)
    {
        "id": "INV-2026-003",
        "vendor": "CyberShield Solutions",
        "amount": 14250.00,
        "currency": "USD",
        "date": "2026-03-05",
        "po_number": "PO-2026-112",
        "approval_status": "APPROVED",
        "authorized_by": "DIR_INFOSEC",
        "description": "Endpoint Threat Protection License Annual Renewal (Inv-90211)",
        "payment_method": "ACH"
    },
    {
        "id": "INV-2026-004",
        "vendor": "CyberShield Solutions",
        "amount": 14250.00,
        "currency": "USD",
        "date": "2026-03-05",
        "po_number": "PO-2026-112",
        "approval_status": "APPROVED",
        "authorized_by": "DIR_INFOSEC",
        "description": "Endpoint Threat Protection License Annual Renewal (Inv-90211) [Duplicate Submission]",
        "payment_method": "ACH"
    },
    # ANOMALY: Unauthorized Weekend Wire to Offshore Vendor
    {
        "id": "INV-2026-005",
        "vendor": "Starlight Offshore Ltd",
        "amount": 78500.00,
        "currency": "USD",
        "date": "2026-03-14",  # Saturday
        "po_number": "PO-2026-125",
        "approval_status": "APPROVED",
        "authorized_by": "DIR_OPERATIONS",  # Missing CFO emergency sign-off!
        "description": "Urgent Freight Dispatch & Customs Fast-Track",
        "payment_method": "INTERNATIONAL_WIRE"
    },
    # STRUCTURING PAIR (Two invoices just under $50,000 threshold to avoid CFO dual-signoff)
    {
        "id": "INV-2026-006",
        "vendor": "Apex Cloud Holdings",
        "amount": 49950.00,
        "currency": "USD",
        "date": "2026-03-22",
        "po_number": "PO-2026-130",
        "approval_status": "APPROVED",
        "authorized_by": "VP_ENGINEERING",
        "description": "High-Density GPU Cluster Allocation Phase A",
        "payment_method": "ACH"
    },
    {
        "id": "INV-2026-007",
        "vendor": "Apex Cloud Holdings",
        "amount": 49990.00,
        "currency": "USD",
        "date": "2026-03-23",
        "po_number": "PO-2026-131",
        "approval_status": "APPROVED",
        "authorized_by": "VP_ENGINEERING",
        "description": "High-Density GPU Cluster Allocation Phase B",
        "payment_method": "ACH"
    },
    # DUPLICATE PAIR 2 (Same vendor and amount, submitted 24h apart with different invoice IDs)
    {
        "id": "INV-2026-008",
        "vendor": "Omnicom Media Agency",
        "amount": 32000.00,
        "currency": "USD",
        "date": "2026-03-27",
        "po_number": "PO-2026-140",
        "approval_status": "APPROVED",
        "authorized_by": "CMO",
        "description": "Spring Enterprise Brand Campaign Media Placement",
        "payment_method": "WIRE"
    },
    {
        "id": "INV-2026-009",
        "vendor": "Omnicom Media Agency",
        "amount": 32000.00,
        "currency": "USD",
        "date": "2026-03-28",
        "po_number": "PO-2026-140",
        "approval_status": "PENDING",
        "authorized_by": "CMO",
        "description": "Spring Enterprise Brand Campaign Media Placement (Re-bill)",
        "payment_method": "WIRE"
    },
    # ANOMALY: Missing PO and Auto-Released over $10,000
    {
        "id": "INV-2026-010",
        "vendor": "Nexus Global Advisory",
        "amount": 38000.00,
        "currency": "USD",
        "date": "2026-03-29",
        "po_number": "NONE",
        "approval_status": "AUTO_RELEASED",
        "authorized_by": "SYSTEM_AUTO",
        "description": "Ad-hoc Offshore Engineering Augmentation",
        "payment_method": "ACH"
    }
]

POLICY_MD_CONTENT = """# Corporate Accounts Payable & Invoice Verification Policy (AP-POL-2026)

## Mandatory Control Standards for Invoice Processing & Payment

### Standard 1: Dual Authorization Threshold ($50,000+)
- **Clause**: All disbursements exceeding or equal to **$50,000.00 USD** require mandatory dual-authorization.
- **Approvers**: Must include both the Department VP and the Chief Financial Officer (CFO) or Corporate Treasurer.
- **Violation Code**: `AP-AUTH-01`.

### Standard 2: Prohibition of Invoice Structuring / Smurfing
- **Clause**: Splitting or slicing purchase commitments into adjacent sub-invoices (e.g., consecutive amounts such as $49,950 and $49,990) to circumvent the $50,000 CFO approval ceiling is strictly prohibited under SOX 404.
- **Violation Code**: `AP-STRUCT-02`.

### Standard 3: Automated Duplicate Invoice Quarantine
- **Clause**: Accounts Payable processing must verify that no prior invoice shares the same **Vendor Name** and **Amount** within a **72-hour window**.
- **Rule**: Any matching candidate invoice must be placed into quarantine with payment held until certified by an independent auditor.
- **Violation Code**: `AP-DUP-03`.

### Standard 4: Three-Way Match Mandate for Invoices > $10,000
- **Clause**: All vendor disbursements exceeding **$10,000.00 USD** must possess an approved Purchase Order (`po_number != 'NONE'`).
- **Rule**: Auto-release or payments without verified PO represent a high-severity internal control failure.
- **Violation Code**: `AP-PO-04`.

### Standard 5: Non-Business Day Wire Transfers
- **Clause**: Any wire transfer scheduled or dispatched on a Saturday, Sunday, or Federal Banking Holiday requires written emergency CFO sign-off prior to execution.
- **Violation Code**: `AP-WIRE-05`.
"""


def generate_all_data():
    """Writes invoices.json and invoice_policy.md."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(INVOICES_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(SAMPLE_INVOICES, f, indent=2)
    print(f"Generated Invoices Database: {INVOICES_JSON_PATH} ({len(SAMPLE_INVOICES)} records)")

    with open(POLICY_MD_PATH, "w", encoding="utf-8") as f:
        f.write(POLICY_MD_CONTENT.strip())
    print(f"Generated Invoice Policy Document: {POLICY_MD_PATH}")


if __name__ == "__main__":
    generate_all_data()
