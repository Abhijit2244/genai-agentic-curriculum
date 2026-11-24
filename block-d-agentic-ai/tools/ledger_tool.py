"""
Ledger Query Tool for Block D: Agentic AI
Uses pandas to query, slice, and filter general ledger transactions.
"""

from pathlib import Path
from typing import Optional
import pandas as pd
from langchain_core.tools import tool

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
LEDGER_CSV_PATH = DATA_DIR / "general_ledger_2026.csv"


def load_ledger_df() -> pd.DataFrame:
    """Loads or generates the ledger DataFrame."""
    if not LEDGER_CSV_PATH.exists():
        try:
            from data.generate_ledger_data import generate_ledger_csv
        except ImportError:
            from ..data.generate_ledger_data import generate_ledger_csv
        generate_ledger_csv(LEDGER_CSV_PATH)
    return pd.read_csv(LEDGER_CSV_PATH)


@tool
def query_ledger_csv(
    vendor: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    po_number: Optional[str] = None,
    approval_status: Optional[str] = None,
    authorized_by: Optional[str] = None,
    limit: int = 15,
) -> str:
    """
    Query and filter transactions from the General Ledger CSV using pandas.
    
    Args:
        vendor: Filter by vendor name (case-insensitive partial match).
        min_amount: Minimum transaction amount in USD.
        max_amount: Maximum transaction amount in USD.
        po_number: Filter by Purchase Order number, or 'NONE' for missing POs.
        approval_status: Filter by approval status ('APPROVED', 'PENDING', 'AUTO_RELEASED').
        authorized_by: Filter by authorizer title (e.g. 'CFO', 'DIR_OPERATIONS', 'UNKNOWN').
        limit: Maximum number of rows to return (default: 15).
        
    Returns:
        A Markdown table of matched transactions with aggregate summary statistics.
    """
    df = load_ledger_df()
    filtered = df.copy()

    if vendor:
        filtered = filtered[filtered["vendor"].str.contains(vendor, case=False, na=False)]
    if min_amount is not None:
        filtered = filtered[filtered["amount"] >= min_amount]
    if max_amount is not None:
        filtered = filtered[filtered["amount"] <= max_amount]
    if po_number:
        if po_number.upper() == "NONE":
            filtered = filtered[filtered["po_number"].str.upper() == "NONE"]
        else:
            filtered = filtered[filtered["po_number"].str.contains(po_number, case=False, na=False)]
    if approval_status:
        filtered = filtered[filtered["approval_status"].str.upper() == approval_status.upper()]
    if authorized_by:
        filtered = filtered[filtered["authorized_by"].str.contains(authorized_by, case=False, na=False)]

    if filtered.empty:
        return "No transactions matched the specified filter criteria in general_ledger_2026.csv."

    total_count = len(filtered)
    total_amount = filtered["amount"].sum()
    avg_amount = filtered["amount"].mean()
    max_val = filtered["amount"].max()

    display_df = filtered.head(limit)

    summary_header = (
        f"### Ledger Query Results ({total_count} matching rows found, showing top {len(display_df)}):\n"
        f"- **Total Spend**: ${total_amount:,.2f} USD\n"
        f"- **Average Amount**: ${avg_amount:,.2f} USD\n"
        f"- **Max Transaction**: ${max_val:,.2f} USD\n\n"
    )

    # Format as clean markdown table without requiring optional tabulate package
    cols = ["transaction_id", "date", "vendor", "amount", "approval_status", "po_number", "authorized_by", "description"]
    header_line = "| " + " | ".join(cols) + " |"
    separator_line = "| " + " | ".join(["---"] * len(cols)) + " |"
    row_lines = []
    for _, row in display_df[cols].iterrows():
        row_lines.append("| " + " | ".join(str(row[c]) for c in cols) + " |")
    table_md = "\n".join([header_line, separator_line] + row_lines)

    return summary_header + table_md
