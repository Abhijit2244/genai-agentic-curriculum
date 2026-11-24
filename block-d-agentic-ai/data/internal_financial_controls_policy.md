# Enterprise Internal Financial Controls & Audit Standard (FIN-CTRL-2026)

## Section 1: Overview & Auditor Responsibilities
This document establishes mandatory internal accounting controls pursuant to Sarbanes-Oxley (SOX) Section 404, COSO Internal Control Framework, and AICPA SSAE-18 standards. 
Independent auditors and forensic automated agents must exercise professional skepticism. Agents assist auditors in evidence gathering, but final audit opinions and disciplinary actions require human auditor review and sign-off.

---

## Section 2: Policy Clauses & Control Mandates

### POL-IC-01: Dual Authorization Threshold ($50,000+)
- **Scope**: All corporate disbursements, ACH transfers, wire transfers, and vendor payments.
- **Requirement**: Any disbursement with an aggregate value equal to or exceeding **$50,000.00 USD** requires mandatory dual-authorization:
  1. Departmental Executive (VP level or higher).
  2. Chief Financial Officer (CFO) or Corporate Treasurer.
- **Audit Rule**: Authorizations granted solely by Directors or Managers for amounts >= $50,000 are invalid and constitute a severe control deficiency.

### POL-IC-02: Prohibition of Transaction Splitting / Structuring
- **Scope**: All purchase requisitions, software licenses, consulting retainers, and cloud capacity allocations.
- **Requirement**: Splitting, fragmenting, or structuring single commercial deliverables into multiple sub-invoices or tranches (e.g., adjacent transactions of $49,950 and $49,990 within a 14-day window) to circumvent the $50,000 CFO dual-authorization ceiling is strictly prohibited.
- **Audit Rule**: Grouped transactions to the same vendor totaling >= $50,000 without CFO sign-off must be flagged as intentional structuring (Red Flag: Fraud / Circumvention of Controls).

### POL-IC-03: Weekend & Non-Business-Day Wire Transfers
- **Scope**: International and domestic wire disbursements.
- **Requirement**: Any wire transfer executed on non-business days (Saturdays, Sundays, or Federal banking holidays) requires explicit emergency written authorization signed by the CFO.
- **Audit Rule**: Weekend wires authorized solely by Operations or IT Directors (e.g., DIR_OPERATIONS) violate banking controls and must be flagged for immediate freeze and transaction recall.

### POL-IC-04: Duplicate Payment Controls & Deduplication
- **Scope**: Accounts Payable (AP) invoice processing.
- **Requirement**: All ERP payment pipelines must enforce a 72-hour duplicate detection check based on Vendor ID, Invoice Number, and Transaction Amount.
- **Audit Rule**: Payments exhibiting identical amounts to the same vendor on the same date or within 72 hours must be flagged as Duplicate Disbursements (Control Failure: AP-DUP-04).

### POL-IC-05: Three-Way Matching & Purchase Order Mandate ($10,000+)
- **Scope**: All vendor procurement and professional services disbursements.
- **Requirement**: Disbursements exceeding **$10,000.00 USD** must possess a verifiable three-way match:
  1. Approved Purchase Order (PO).
  2. Verified Vendor Invoice.
  3. Formal Receiving Report / Acceptance Sign-off.
- **Audit Rule**: Any disbursement > $10,000 with `po_number = 'NONE'` or released via `AUTO_RELEASED` status represents a Critical Breakdown in Procurement Authorization (Control Failure: PROC-PO-05).