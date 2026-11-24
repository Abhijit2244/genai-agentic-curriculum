"""
generate_test_invoices.py — Generates test ledger CSV, compliance policy, and visual invoice images.
Uses PIL to render realistic invoice graphics for the OpenCV + OCR pipeline.
"""

import csv
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

DATA_DIR = Path(__file__).resolve().parent
LEDGER_CSV_PATH = DATA_DIR / "ledger.csv"
POLICY_MD_PATH = DATA_DIR / "compliance_policy.md"
CYBER_INVOICE_PNG = DATA_DIR / "invoice_cybershield_dup.png"
APEX_INVOICE_PNG = DATA_DIR / "invoice_apex_structuring.png"


LEDGER_ROWS = [
    {"transaction_id": "TXN-2026-001", "invoice_id": "INV-2026-001", "date": "2026-03-01", "vendor": "CloudMatrix Systems", "amount": 24500.00, "po_number": "PO-2026-101", "approval_status": "APPROVED", "authorized_by": "VP_ENGINEERING", "description": "Monthly Kubernetes & Cloud Hosting"},
    {"transaction_id": "TXN-2026-002", "invoice_id": "INV-2026-002", "date": "2026-03-03", "vendor": "Metropolis Legal LLP", "amount": 18200.00, "po_number": "PO-2026-105", "approval_status": "APPROVED", "authorized_by": "GENERAL_COUNSEL", "description": "Q1 IP & Regulatory Advisory"},
    
    # Existing duplicate candidate in ledger
    {"transaction_id": "TXN-2026-003", "invoice_id": "INV-2026-003", "date": "2026-03-05", "vendor": "CyberShield Solutions", "amount": 14250.00, "po_number": "PO-2026-112", "approval_status": "APPROVED", "authorized_by": "DIR_INFOSEC", "description": "Endpoint Threat Protection Renewal Inv-90211"},

    # Existing structuring candidate in ledger
    {"transaction_id": "TXN-2026-006", "invoice_id": "INV-2026-006", "date": "2026-03-22", "vendor": "Apex Cloud Holdings", "amount": 49950.00, "po_number": "PO-2026-130", "approval_status": "APPROVED", "authorized_by": "VP_ENGINEERING", "description": "GPU Cluster Allocation Tranche A"},

    # Unauthorized weekend wire in ledger
    {"transaction_id": "TXN-2026-008", "invoice_id": "INV-2026-008", "date": "2026-03-14", "vendor": "Starlight Offshore Ltd", "amount": 78500.00, "po_number": "PO-2026-125", "approval_status": "APPROVED", "authorized_by": "DIR_OPERATIONS", "description": "Urgent Freight Dispatch & Clearance"},

    # Missing PO anomaly in ledger
    {"transaction_id": "TXN-2026-010", "invoice_id": "INV-2026-010", "date": "2026-03-29", "vendor": "Nexus Global Advisory", "amount": 38000.00, "po_number": "NONE", "approval_status": "AUTO_RELEASED", "authorized_by": "UNKNOWN", "description": "Ad-hoc Offshore Staff Augmentation"}
]

POLICY_MD_CONTENT = """# Corporate Accounts Payable & Financial Controls Standard (SOX 404 / AP-POL-2026)

## Mandatory Control Standards for Invoice Verification

### Standard 1: Dual Authorization Threshold ($50,000+)
- **Clause**: Any disbursement or invoice with a total value equal to or exceeding **$50,000.00 USD** requires mandatory dual-authorization:
  1. Departmental Executive (VP level or higher).
  2. Chief Financial Officer (CFO) or Corporate Treasurer.
- **Violation Code**: `AP-AUTH-01`.

### Standard 2: Prohibition of Invoice Structuring / Smurfing
- **Clause**: Splitting a single purchase commitment or scope of work into multiple sub-invoices (e.g., adjacent transactions of $49,950 and $49,990 within a 14-day window) to circumvent the $50,000 CFO dual-authorization ceiling is strictly prohibited.
- **Violation Code**: `AP-STRUCT-02`.

### Standard 3: Automated Duplicate Invoice Quarantine (72-Hour Window)
- **Clause**: The Accounts Payable system must verify that no prior invoice shares the same **Vendor Name** and **Amount** within a **72-hour window**.
- **Rule**: Duplicate submissions must be immediately placed into quarantine with payment frozen pending senior auditor certification.
- **Violation Code**: `AP-DUP-03`.

### Standard 4: Three-Way Match Mandate for Invoices > $10,000
- **Clause**: All vendor disbursements exceeding **$10,000.00 USD** must possess an approved Purchase Order (`po_number != 'NONE'`).
- **Violation Code**: `AP-PO-04`.

### Standard 5: Non-Business Day Wire Transfers
- **Clause**: Any wire transfer executed on a Saturday, Sunday, or Federal Banking Holiday requires written emergency CFO pre-authorization.
- **Violation Code**: `AP-WIRE-05`.
"""


def generate_invoice_image(
    output_path: Path,
    vendor_name: str,
    invoice_num: str,
    invoice_date: str,
    po_num: str,
    amount_str: str,
    description: str
):
    """Draws a clean, realistic corporate invoice image using Pillow."""
    width, height = 800, 1000
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Header Banner
    draw.rectangle([(0, 0), (width, 100)], fill=(30, 58, 138))  # Dark Blue
    draw.text((40, 35), vendor_name.upper(), fill=(255, 255, 255))
    draw.text((600, 35), "INVOICE", fill=(255, 255, 255))

    # Meta Details Box
    draw.rectangle([(40, 140), (760, 240)], outline=(203, 213, 225), width=2)
    draw.text((60, 160), f"Invoice Number: {invoice_num}", fill=(15, 23, 42))
    draw.text((60, 195), f"Invoice Date:   {invoice_date}", fill=(15, 23, 42))
    draw.text((450, 160), f"PO Number:      {po_num}", fill=(15, 23, 42))
    draw.text((450, 195), f"Payment Terms:  Net 30 (ACH)", fill=(15, 23, 42))

    # Bill To
    draw.text((40, 270), "BILL TO:", fill=(100, 116, 139))
    draw.text((40, 295), "Acme Corporation — Corporate Accounts Payable", fill=(15, 23, 42))
    draw.text((40, 320), "100 Innovation Way, Suite 400, San Francisco, CA 94105", fill=(71, 85, 105))

    # Line Items Table Header
    draw.rectangle([(40, 380), (760, 420)], fill=(241, 245, 249))
    draw.text((60, 392), "DESCRIPTION", fill=(51, 65, 85))
    draw.text((500, 392), "QTY", fill=(51, 65, 85))
    draw.text((650, 392), "AMOUNT", fill=(51, 65, 85))

    # Line Item 1
    draw.line([(40, 480), (760, 480)], fill=(226, 232, 240), width=1)
    draw.text((60, 440), description, fill=(15, 23, 42))
    draw.text((510, 440), "1", fill=(15, 23, 42))
    draw.text((650, 440), amount_str, fill=(15, 23, 42))

    # Total Box
    draw.rectangle([(450, 520), (760, 600)], fill=(248, 250, 252), outline=(203, 213, 225))
    draw.text((470, 535), "Subtotal:", fill=(100, 116, 139))
    draw.text((650, 535), amount_str, fill=(100, 116, 139))
    draw.text((470, 565), "TOTAL DUE:", fill=(15, 23, 42))
    draw.text((630, 565), f"{amount_str} USD", fill=(15, 23, 42))

    # Footer Notice
    draw.text((40, 920), "Remit payment to: Corporate Accounts Payable Department", fill=(148, 163, 184))
    draw.text((40, 945), "Electronic ACH / Wire Routing: 121000358 | Account: 884920194", fill=(148, 163, 184))

    img.save(output_path, "PNG")
    print(f"Generated Invoice Image: {output_path}")


def generate_all():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Write ledger CSV
    with open(LEDGER_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(LEDGER_ROWS[0].keys()))
        writer.writeheader()
        writer.writerows(LEDGER_ROWS)
    print(f"Generated Ledger CSV: {LEDGER_CSV_PATH} ({len(LEDGER_ROWS)} rows)")

    # 2. Write policy markdown
    with open(POLICY_MD_PATH, "w", encoding="utf-8") as f:
        f.write(POLICY_MD_CONTENT.strip())
    print(f"Generated Policy Standard: {POLICY_MD_PATH}")

    # 3. Generate Duplicate Invoice Image (CyberShield INV-2026-004)
    generate_invoice_image(
        output_path=CYBER_INVOICE_PNG,
        vendor_name="CyberShield Solutions Inc.",
        invoice_num="INV-2026-004",
        invoice_date="2026-03-05",
        po_num="PO-2026-112",
        amount_str="$14,250.00",
        description="Endpoint Threat Protection License Annual Renewal (Inv-90211)"
    )

    # 4. Generate Structuring Invoice Image (Apex Cloud INV-2026-007)
    generate_invoice_image(
        output_path=APEX_INVOICE_PNG,
        vendor_name="Apex Cloud Holdings Ltd.",
        invoice_num="INV-2026-007",
        invoice_date="2026-03-23",
        po_num="PO-2026-131",
        amount_str="$49,990.00",
        description="High-Density GPU Cluster Allocation Phase B"
    )


if __name__ == "__main__":
    generate_all()
