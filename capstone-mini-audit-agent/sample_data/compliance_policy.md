# Corporate Accounts Payable & Financial Controls Standard (SOX 404 / AP-POL-2026)

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