# Corporate Accounts Payable & Invoice Verification Policy (AP-POL-2026)

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