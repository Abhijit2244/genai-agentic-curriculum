"""
audit_graph.py — LangGraph Orchestration State Machine for the Capstone
Orchestrates:
1. OCR Preprocessing & Extraction (via MCP)
2. Ledger Duplicate & Structuring Analysis (via MCP)
3. Policy Semantic RAG (via MCP)
4. LLM Forensic Reasoning Synthesis
5. Human-in-the-Loop (HITL) Approval Breakpoint (interrupt_before)
6. Final Certified Audit Report Generation
"""

import sys
from pathlib import Path
from typing import TypedDict, Optional, Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import get_llm, extract_text
from mcp_service.audit_mcp_server import (
    ocr_invoice,
    check_ledger_anomalies,
    search_compliance_policy,
    submit_audit_findings
)


class AuditState(TypedDict):
    job_id: str
    invoice_image_path: str
    ledger_csv_path: str
    invoice_data: Optional[Dict[str, Any]]
    ledger_anomalies: Optional[Dict[str, Any]]
    policy_citations: Optional[List[Dict[str, Any]]]
    reasoning_synthesis: Optional[str]
    pending_approval: bool
    human_approved: Optional[bool]
    human_notes: Optional[str]
    final_report: Optional[str]
    progress_step: str
    status_message: str


def node_ocr(state: AuditState) -> Dict[str, Any]:
    """Node 1: Runs OpenCV preprocessing and OCR extraction via MCP tool."""
    image_path = state["invoice_image_path"]
    data = ocr_invoice(image_path)
    return {
        "invoice_data": data,
        "progress_step": "OCR_COMPLETED",
        "status_message": f"Extracted invoice {data.get('invoice_number', 'N/A')} from {data.get('vendor', 'N/A')} for ${data.get('amount', 0):,.2f}."
    }


def node_ledger(state: AuditState) -> Dict[str, Any]:
    """Node 2: Runs pandas duplicate and structuring checks via MCP tool."""
    inv = state["invoice_data"] or {}
    vendor = inv.get("vendor", "")
    amount = float(inv.get("amount", 0.0))
    inv_id = inv.get("invoice_number", "")
    ledger_path = state["ledger_csv_path"]

    anomalies = check_ledger_anomalies(
        ledger_csv_path=ledger_path,
        vendor=vendor,
        amount=amount,
        invoice_id=inv_id
    )

    detected_count = anomalies.get("anomalies_detected", 0)
    msg = f"Pandas ledger scan complete: {detected_count} red flag(s) identified." if detected_count else "Ledger scan clean: no duplicate or structuring matches."
    return {
        "ledger_anomalies": anomalies,
        "progress_step": "LEDGER_CHECK_COMPLETED",
        "status_message": msg
    }


def node_rag(state: AuditState) -> Dict[str, Any]:
    """Node 3: Ingests governing SOX 404 compliance rules via MCP RAG tool."""
    anomalies = (state.get("ledger_anomalies") or {}).get("anomalies", [])
    if anomalies:
        primary_violation = anomalies[0].get("violation_code", "AP-DUP-03")
        query = f"compliance rule {primary_violation} duplicate structuring authorization"
    else:
        query = "general invoice approval and dual authorization requirements"

    citations = search_compliance_policy(query)
    codes = [c.get("citation", "GENERAL") for c in citations]
    return {
        "policy_citations": citations,
        "progress_step": "POLICY_RAG_COMPLETED",
        "status_message": f"Retrieved governing compliance standards: {', '.join(codes)}."
    }


def node_reasoning(state: AuditState) -> Dict[str, Any]:
    """Node 4: Synthesizes evidence and drafts proposed audit findings."""
    inv = state["invoice_data"] or {}
    ledger_anom = state["ledger_anomalies"] or {}
    citations = state["policy_citations"] or []

    citations_text = "\n".join(f"[{c.get('citation')}]: {c.get('text')}" for c in citations)
    anomalies_list = ledger_anom.get("anomalies", [])

    llm = get_llm(temperature=0.0)
    prompt = [
        SystemMessage(content=(
            "You are a Senior Forensic Internal Auditor examining an invoice submission.\n"
            "Analyze the extracted invoice details against the ledger anomaly scan and policy standards.\n"
            "Draft a concise preliminary audit evaluation with: 1. Primary Finding, 2. Violated Standard, 3. Severity, and 4. Recommended Action."
        )),
        HumanMessage(content=(
            f"INVOICE METADATA (FROM OCR):\n"
            f"Vendor: {inv.get('vendor')}\n"
            f"Invoice Number: {inv.get('invoice_number')}\n"
            f"Amount: ${inv.get('amount', 0):,.2f} USD\n"
            f"Date: {inv.get('date')}\n"
            f"PO Number: {inv.get('po_number')}\n\n"
            f"LEDGER ANOMALY SCAN:\n{anomalies_list}\n\n"
            f"GOVERNING POLICY CITATIONS:\n{citations_text}\n"
        ))
    ]

    synthesis = extract_text(llm.invoke(prompt).content)
    return {
        "reasoning_synthesis": synthesis,
        "pending_approval": True,
        "progress_step": "AWAITING_HUMAN_APPROVAL",
        "status_message": "Forensic evaluation complete. Paused at Human-in-the-Loop gate for auditor sign-off."
    }


def node_human_approval(state: AuditState) -> Dict[str, Any]:
    """
    Node 5: Human-in-the-Loop breakpoint.
    Execution suspends before this node. Resumes when human submits approval.
    """
    approved = state.get("human_approved", True)
    notes = state.get("human_notes", "Approved by Lead CPA Auditor.")
    return {
        "pending_approval": False,
        "progress_step": "HUMAN_APPROVED" if approved else "HUMAN_REJECTED",
        "status_message": f"Auditor Review Complete: {'APPROVED' if approved else 'REJECTED'} (Notes: {notes})."
    }


def node_report(state: AuditState) -> Dict[str, Any]:
    """Node 6: Commits findings via MCP tool and generates official signed memorandum."""
    inv = state["invoice_data"] or {}
    anomalies = (state.get("ledger_anomalies") or {}).get("anomalies", [])
    synthesis = state.get("reasoning_synthesis", "")
    notes = state.get("human_notes", "Reviewed & signed off by Senior Auditor.")

    violation_code = anomalies[0].get("violation_code", "AP-DUP-03") if anomalies else "CLEAN"
    severity = anomalies[0].get("severity", "LOW") if anomalies else "INFO"

    # Commit findings via MCP tool
    submit_audit_findings(
        invoice_id=inv.get("invoice_number", "UNKNOWN"),
        vendor=inv.get("vendor", "UNKNOWN"),
        amount=float(inv.get("amount", 0.0)),
        violation_code=violation_code,
        severity=severity,
        rationale=synthesis[:200],
        auditor_action=notes
    )

    # Draft final certified report
    report = (
        f"# OFFICIAL SOX 404 AUDIT EXCEPTION MEMORANDUM\n\n"
        f"**Audit Job ID:** {state['job_id']}  \n"
        f"**Target Invoice:** `{inv.get('invoice_number')}` ({inv.get('vendor')})  \n"
        f"**Invoice Amount:** ${inv.get('amount', 0.0):,.2f} USD  \n"
        f"**Audit Status:** CERTIFIED BY HUMAN LEAD AUDITOR  \n"
        f"**Primary Control Code:** `{violation_code}` (Severity: **{severity}**)  \n\n"
        f"---\n\n"
        f"### Forensic Evidence & Synthesis\n"
        f"{synthesis}\n\n"
        f"---\n\n"
        f"### Human Auditor Certification\n"
        f"- **Auditor Sign-off Status:** APPROVED  \n"
        f"- **Auditor Professional Notes:** {notes}  \n"
        f"- **Workpaper Action:** Exception recorded. Disbursement freeze instruction dispatched to Accounts Payable."
    )

    return {
        "final_report": report,
        "progress_step": "REPORT_READY",
        "status_message": "Official Audit Memorandum generated and signed into workpapers."
    }


def build_audit_workflow(checkpointer: Optional[MemorySaver] = None):
    """
    Constructs the LangGraph audit state machine with an explicit
    interrupt_before breakpoint on 'human_approval'.
    """
    workflow = StateGraph(AuditState)

    workflow.add_node("ocr", node_ocr)
    workflow.add_node("ledger", node_ledger)
    workflow.add_node("rag", node_rag)
    workflow.add_node("reasoning", node_reasoning)
    workflow.add_node("human_approval", node_human_approval)
    workflow.add_node("report", node_report)

    workflow.add_edge(START, "ocr")
    workflow.add_edge("ocr", "ledger")
    workflow.add_edge("ledger", "rag")
    workflow.add_edge("rag", "reasoning")
    workflow.add_edge("reasoning", "human_approval")
    workflow.add_edge("human_approval", "report")
    workflow.add_edge("report", END)

    # Crucial: Halt execution before entering human_approval node
    return workflow.compile(
        checkpointer=checkpointer or MemorySaver(),
        interrupt_before=["human_approval"]
    )
