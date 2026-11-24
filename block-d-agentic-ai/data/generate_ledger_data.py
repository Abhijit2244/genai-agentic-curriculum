"""
Generates a realistic corporate General Ledger CSV dataset for auditing.
Includes legitimate corporate transactions and subtle financial/compliance anomalies.
"""

import csv
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
LEDGER_CSV_PATH = DATA_DIR / "general_ledger_2026.csv"


TRANSACTIONS = [
    # Legitimate Transactions
    {"transaction_id": "TXN-2026-001", "date": "2026-03-02", "account_id": "6010", "account_name": "Facilities & Office", "vendor": "Metropolis Real Estate", "amount": 25000.00, "currency": "USD", "description": "Monthly HQ Office Lease", "approval_status": "APPROVED", "po_number": "PO-2026-011", "authorized_by": "VP_FINANCE"},
    {"transaction_id": "TXN-2026-002", "date": "2026-03-03", "account_id": "6020", "account_name": "Cloud Infrastructure", "vendor": "Google Cloud EMEA", "amount": 34120.50, "currency": "USD", "description": "Monthly Compute & BigQuery Usage", "approval_status": "APPROVED", "po_number": "PO-2026-014", "authorized_by": "VP_ENGINEERING"},
    
    # Anomaly 1: Duplicate Payment (Same vendor, same amount, same day)
    {"transaction_id": "TXN-2026-003", "date": "2026-03-05", "account_id": "6040", "account_name": "Security Software", "vendor": "CyberShield Solutions", "amount": 14250.00, "currency": "USD", "description": "Annual Endpoint Protection License Inv-90211", "approval_status": "APPROVED", "po_number": "PO-2026-022", "authorized_by": "DIR_INFOSEC"},
    {"transaction_id": "TXN-2026-004", "date": "2026-03-05", "account_id": "6040", "account_name": "Security Software", "vendor": "CyberShield Solutions", "amount": 14250.00, "currency": "USD", "description": "Annual Endpoint Protection License Inv-90211 (Duplicate)", "approval_status": "APPROVED", "po_number": "PO-2026-022", "authorized_by": "DIR_INFOSEC"},

    {"transaction_id": "TXN-2026-005", "date": "2026-03-08", "account_id": "6050", "account_name": "Legal & Regulatory", "vendor": "Sullivan & Sterling LLP", "amount": 18500.00, "currency": "USD", "description": "Patent Filing and IP Advisory", "approval_status": "APPROVED", "po_number": "PO-2026-035", "authorized_by": "GENERAL_COUNSEL"},
    {"transaction_id": "TXN-2026-006", "date": "2026-03-10", "account_id": "6020", "account_name": "Cloud Infrastructure", "vendor": "Datadog Observability", "amount": 8400.00, "currency": "USD", "description": "APM and Log Ingestion Subscription", "approval_status": "APPROVED", "po_number": "PO-2026-039", "authorized_by": "DEV_LEAD"},
    {"transaction_id": "TXN-2026-007", "date": "2026-03-12", "account_id": "6030", "account_name": "Consulting & Advisory", "vendor": "Deloitte Advisory", "amount": 62000.00, "currency": "USD", "description": "Q1 Internal Controls Readiness Review", "approval_status": "APPROVED", "po_number": "PO-2026-042", "authorized_by": "CFO"},

    # Anomaly 2: Weekend Wire Transfer without CFO Authorization (Saturday wire)
    {"transaction_id": "TXN-2026-008", "date": "2026-03-14", "account_id": "6070", "account_name": "International Logistics", "vendor": "Starlight Offshore Ltd", "amount": 78500.00, "currency": "USD", "description": "Urgent Expedited Freight Clearance", "approval_status": "APPROVED", "po_number": "PO-2026-045", "authorized_by": "DIR_OPERATIONS"},

    {"transaction_id": "TXN-2026-009", "date": "2026-03-16", "account_id": "6010", "account_name": "Facilities & Office", "vendor": "Global Cleaners Inc", "amount": 3200.00, "currency": "USD", "description": "Janitorial and Sanitization Services", "approval_status": "APPROVED", "po_number": "PO-2026-048", "authorized_by": "OFFICE_MGR"},
    {"transaction_id": "TXN-2026-010", "date": "2026-03-17", "account_id": "6060", "account_name": "Marketing & PR", "vendor": "Omnicom Media", "amount": 42000.00, "currency": "USD", "description": "Spring Product Launch Ad Campaign", "approval_status": "APPROVED", "po_number": "PO-2026-051", "authorized_by": "CMO"},
    {"transaction_id": "TXN-2026-011", "date": "2026-03-18", "account_id": "6020", "account_name": "Cloud Infrastructure", "vendor": "Snowflake Inc", "amount": 16500.00, "currency": "USD", "description": "Data Warehouse Credit Consumption", "approval_status": "APPROVED", "po_number": "PO-2026-055", "authorized_by": "VP_DATA"},
    {"transaction_id": "TXN-2026-012", "date": "2026-03-19", "account_id": "6080", "account_name": "HR & Recruiting", "vendor": "Robert Half Tech", "amount": 9500.00, "currency": "USD", "description": "Contract Staffing Contingency Fee", "approval_status": "APPROVED", "po_number": "PO-2026-058", "authorized_by": "HR_DIRECTOR"},
    {"transaction_id": "TXN-2026-013", "date": "2026-03-20", "account_id": "6040", "account_name": "Security Software", "vendor": "Okta Identity", "amount": 11200.00, "currency": "USD", "description": "Workforce Identity MFA Enterprise", "approval_status": "APPROVED", "po_number": "PO-2026-061", "authorized_by": "DIR_INFOSEC"},

    # Anomaly 3: Structuring / Threshold Circumvention (Two transactions just under $50,000 threshold to avoid CFO dual-signoff)
    {"transaction_id": "TXN-2026-014", "date": "2026-03-22", "account_id": "6020", "account_name": "Cloud Infrastructure", "vendor": "Apex Cloud Holdings", "amount": 49950.00, "currency": "USD", "description": "GPU Cluster Reservation Tranche A", "approval_status": "APPROVED", "po_number": "PO-2026-065", "authorized_by": "VP_ENGINEERING"},
    {"transaction_id": "TXN-2026-015", "date": "2026-03-23", "account_id": "6020", "account_name": "Cloud Infrastructure", "vendor": "Apex Cloud Holdings", "amount": 49990.00, "currency": "USD", "description": "GPU Cluster Reservation Tranche B", "approval_status": "APPROVED", "po_number": "PO-2026-066", "authorized_by": "VP_ENGINEERING"},

    {"transaction_id": "TXN-2026-016", "date": "2026-03-24", "account_id": "6010", "account_name": "Facilities & Office", "vendor": "Cisco Systems", "amount": 28400.00, "currency": "USD", "description": "Core Switch Network Hardware Upgrade", "approval_status": "APPROVED", "po_number": "PO-2026-070", "authorized_by": "VP_IT"},
    {"transaction_id": "TXN-2026-017", "date": "2026-03-25", "account_id": "6050", "account_name": "Legal & Regulatory", "vendor": "Baker McKenzie", "amount": 21000.00, "currency": "USD", "description": "International Tax Structuring Advisory", "approval_status": "APPROVED", "po_number": "PO-2026-074", "authorized_by": "GENERAL_COUNSEL"},
    {"transaction_id": "TXN-2026-018", "date": "2026-03-26", "account_id": "6030", "account_name": "Consulting & Advisory", "vendor": "McKinsey & Co", "amount": 125000.00, "currency": "USD", "description": "Strategic Growth Initiative Phase II", "approval_status": "APPROVED", "po_number": "PO-2026-078", "authorized_by": "CFO"},
    {"transaction_id": "TXN-2026-019", "date": "2026-03-27", "account_id": "6060", "account_name": "Marketing & PR", "vendor": "HubSpot Marketing", "amount": 7600.00, "currency": "USD", "description": "Enterprise Marketing Hub Seats", "approval_status": "APPROVED", "po_number": "PO-2026-081", "authorized_by": "CMO"},
    {"transaction_id": "TXN-2026-020", "date": "2026-03-28", "account_id": "6080", "account_name": "HR & Recruiting", "vendor": "LinkedIn Enterprise", "amount": 15400.00, "currency": "USD", "description": "Recruiter Corporate Subscriptions", "approval_status": "APPROVED", "po_number": "PO-2026-085", "authorized_by": "HR_DIRECTOR"},

    # Anomaly 4: Unapproved Vendor Disbursement with Missing PO and Auto-Release
    {"transaction_id": "TXN-2026-021", "date": "2026-03-29", "account_id": "6030", "account_name": "Consulting & Advisory", "vendor": "Nexus Global Advisory", "amount": 38000.00, "currency": "USD", "description": "Ad-hoc Offshore Staff Augmentation", "approval_status": "AUTO_RELEASED", "po_number": "NONE", "authorized_by": "UNKNOWN"},

    {"transaction_id": "TXN-2026-022", "date": "2026-03-30", "account_id": "6010", "account_name": "Facilities & Office", "vendor": "Pacific Gas & Electric", "amount": 4820.00, "currency": "USD", "description": "HQ Utility and Power Grid Services", "approval_status": "APPROVED", "po_number": "PO-2026-089", "authorized_by": "OFFICE_MGR"},
    {"transaction_id": "TXN-2026-023", "date": "2026-03-30", "account_id": "6040", "account_name": "Security Software", "vendor": "CrowdStrike Falcon", "amount": 27500.00, "currency": "USD", "description": "Threat Hunting & Incident Response Retainer", "approval_status": "APPROVED", "po_number": "PO-2026-092", "authorized_by": "DIR_INFOSEC"},
    {"transaction_id": "TXN-2026-024", "date": "2026-03-31", "account_id": "6020", "account_name": "Cloud Infrastructure", "vendor": "Amazon Web Services", "amount": 48750.00, "currency": "USD", "description": "Production S3, RDS, and EKS Cluster Compute", "approval_status": "APPROVED", "po_number": "PO-2026-096", "authorized_by": "VP_ENGINEERING"},
    {"transaction_id": "TXN-2026-025", "date": "2026-03-31", "account_id": "6070", "account_name": "International Logistics", "vendor": "FedEx Corporate Logistics", "amount": 5400.00, "currency": "USD", "description": "Global Hardware Shipment Dispatch", "approval_status": "APPROVED", "po_number": "PO-2026-099", "authorized_by": "DIR_OPERATIONS"},
]


def generate_ledger_csv(output_path: Path = LEDGER_CSV_PATH) -> Path:
    """Generates the general ledger CSV file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(TRANSACTIONS[0].keys())
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(TRANSACTIONS)
    print(f"Generated General Ledger CSV: {output_path} ({len(TRANSACTIONS)} rows)")
    return output_path


if __name__ == "__main__":
    generate_ledger_csv()
