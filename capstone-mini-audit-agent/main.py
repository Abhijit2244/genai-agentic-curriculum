"""
main.py — Main Entrypoint for Capstone: Mini Audit Agent
Starts the FastAPI application (hosting the React UI & SSE streaming endpoints)
or runs an automated end-to-end audit demonstration in CLI mode.

Usage:
    python main.py             # Starts FastAPI server on http://127.0.0.1:8000
    python main.py --demo      # Runs CLI simulation of the entire LangGraph audit loop
"""

import sys
import os
import argparse
import uvicorn
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import API_KEY, HOST, PORT
from agent.audit_graph import build_audit_workflow
from langgraph.checkpoint.memory import MemorySaver


BANNER = r"""
================================================================================
   ______ ___    ____  _____ ______ ____  _   ______   ___   __  ______  ________
  / ____//   |  / __ \/ ___//_  __// __ \/ | / / ____/  /   | / / / / __ \/  _/_  __/
 / /    / /| | / /_/ /\__ \  / /  / / / /  |/ / __/    / /| |/ / / / / / // /  / /   
/ /___ / ___ |/ ____/___/ / / /  / /_/ / /|  / /___   / ___ / /_/ / /_/ // /  / /    
\____//_/  |_/_/    /____/ /_/   \____/_/ |_/_____/  /_/  |_\____/_____/___/ /_/     
                   MINI AUDIT AGENT — ENTERPRISE SOX 404 EDITION
================================================================================
"""


def run_cli_demo():
    print(BANNER)
    print(">>> RUNNING AUTOMATED CLI FORENSIC AUDIT DEMO")
    print("-" * 80)

    sample_invoice = str(PROJECT_ROOT / "sample_data" / "invoice_cybershield_dup.png")
    sample_ledger = str(PROJECT_ROOT / "sample_data" / "ledger.csv")

    if not Path(sample_invoice).exists() or not Path(sample_ledger).exists():
        print(f"[!] Sample files missing. Generating test invoices now...")
        from sample_data.generate_test_invoices import generate_data
        generate_data()

    print(f"[*] Invoice Target: {sample_invoice}")
    print(f"[*] Ledger Data:    {sample_ledger}")
    print("-" * 80)

    job_id = "cli-demo-audit-job-001"
    checkpointer = MemorySaver()
    workflow = build_audit_workflow(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": job_id}}

    initial_state = {
        "job_id": job_id,
        "invoice_image_path": sample_invoice,
        "ledger_csv_path": sample_ledger,
        "invoice_data": None,
        "ledger_anomalies": None,
        "policy_citations": None,
        "reasoning_synthesis": None,
        "pending_approval": False,
        "human_approved": None,
        "human_notes": None,
        "final_report": None,
        "progress_step": "STARTED",
        "status_message": "Initializing CLI audit job..."
    }

    print("\n[Step 1-4] Executing LangGraph nodes: OCR -> Ledger Checks -> Policy RAG -> LLM Synthesis...")
    workflow.invoke(initial_state, config=config)

    snapshot = workflow.get_state(config)
    print(f"\n[Step 5] Reached Breakpoint!")
    print(f"  -> Next Node:       {snapshot.next}")
    print(f"  -> Progress State:  {snapshot.values.get('progress_step')}")
    print(f"  -> Extracted Vendor: {snapshot.values.get('invoice_data', {}).get('vendor')}")
    print(f"  -> Invoice Amount:   ${snapshot.values.get('invoice_data', {}).get('amount')}")
    print(f"  -> Anomalies Found:  {snapshot.values.get('ledger_anomalies', {}).get('anomalies_detected')}")
    for a in snapshot.values.get('ledger_anomalies', {}).get('anomalies', []):
        print(f"     * [{a.get('violation_code')}] {a.get('title')} (Severity: {a.get('severity')})")

    print("\n[Step 6] Simulating Auditor Human-in-the-Loop Sign-Off...")
    workflow.update_state(
        config,
        {
            "human_approved": True,
            "human_notes": "Auditor Sign-off (CLI Demo): Confirmed duplicate transaction AP-DUP-03. Payment freeze issued."
        }
    )

    print("\n[Step 7] Resuming graph execution to generate formal signed memorandum...")
    workflow.invoke(None, config=config)

    final_snapshot = workflow.get_state(config)
    print("\n" + "=" * 80)
    print("FINAL OFFICIAL AUDIT REPORT MEMORANDUM:")
    print("=" * 80)
    print(final_snapshot.values.get("final_report", "No report generated."))
    print("=" * 80)
    print("\n[✓] CLI Demo Completed Successfully!")


def start_server():
    print(BANNER)
    print(f"  Web Application:   http://{HOST}:{PORT}/")
    print(f"  API Documentation: http://{HOST}:{PORT}/docs")
    print(f"  Sample Files:      {PROJECT_ROOT / 'sample_data'}")
    print("=" * 80)
    print("Starting Uvicorn Server. Press CTRL+C to stop.\n")
    uvicorn.run("backend.app:app", host=HOST, port=PORT, reload=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mini Audit Agent — Capstone System")
    parser.add_argument("--demo", action="store_true", help="Run automated CLI demonstration of the audit loop")
    args = parser.parse_args()

    if args.demo:
        run_cli_demo()
    else:
        start_server()
