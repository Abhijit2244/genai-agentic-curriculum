"""
Audit Exception Flagging Tool for Block D: Agentic AI
Enables an auditor agent to record formal internal control exceptions in workpapers.
"""

from datetime import datetime
from typing import List, Dict, Any
from langchain_core.tools import tool

# Global in-memory audit exception registry
_FLAGGED_ANOMALIES: List[Dict[str, Any]] = []


def get_flagged_anomalies() -> List[Dict[str, Any]]:
    """Returns the list of currently recorded audit anomalies."""
    return list(_FLAGGED_ANOMALIES)


def reset_anomalies():
    """Clears the registry for fresh test runs."""
    global _FLAGGED_ANOMALIES
    _FLAGGED_ANOMALIES.clear()


@tool
def flag_anomaly(
    transaction_id: str,
    policy_violation_code: str,
    severity: str,
    rationale: str,
    recommended_action: str,
) -> str:
    """
    Log an official audit exception and flag a suspicious transaction in the audit workpapers.
    
    Args:
        transaction_id: The unique ID of the anomalous transaction (e.g., 'TXN-2026-008').
        policy_violation_code: The violated policy control ID (e.g., 'POL-IC-01', 'POL-IC-02', 'POL-IC-03').
        severity: Risk level ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW').
        rationale: Forensic justification explaining why this transaction violates internal controls.
        recommended_action: Recommended remediation (e.g., 'Freeze disbursement', 'Escalate to Audit Committee', 'Demand CFO sign-off').
        
    Returns:
        A formal Audit Exception Record confirming entry into the audit workpapers.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    exception_record = {
        "exception_id": f"EXC-{len(_FLAGGED_ANOMALIES) + 1:04d}",
        "timestamp": timestamp,
        "transaction_id": transaction_id.strip().upper(),
        "policy_violation_code": policy_violation_code.strip().upper(),
        "severity": severity.strip().upper(),
        "rationale": rationale.strip(),
        "recommended_action": recommended_action.strip(),
    }
    _FLAGGED_ANOMALIES.append(exception_record)

    output = (
        f"=====================================================\n"
        f"  OFFICIAL AUDIT WORKPAPER EXCEPTION RECORDED\n"
        f"=====================================================\n"
        f"- **Exception ID**: {exception_record['exception_id']}\n"
        f"- **Timestamp**: {exception_record['timestamp']}\n"
        f"- **Transaction ID**: {exception_record['transaction_id']}\n"
        f"- **Control Code**: {exception_record['policy_violation_code']}\n"
        f"- **Severity Level**: {exception_record['severity']}\n"
        f"- **Forensic Rationale**: {exception_record['rationale']}\n"
        f"- **Remediation**: {exception_record['recommended_action']}\n"
        f"Status: LOGGED IN WORKPAPERS. PENDING SENIOR AUDITOR REVIEW.\n"
        f"====================================================="
    )
    return output
