"""
main.py — Master Runner for Block D: Agentic AI
Runs all demonstrations covering:
1. Chatbot vs Workflow vs Autonomous Agent & Autonomy Levels (0-5)
2. LangGraph ReAct Audit Agent (query_ledger_csv, search_policy, flag_anomaly)
3. Human-in-the-Loop (HITL) Audit Approval Gate (Professional Skepticism)
4. Multi-Agent Team with Supervisor Pattern (Forensic Auditor & Policy Specialist)
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def run_all_demos():
    import importlib
    print("=" * 80)
    print("      BLOCK D: AGENTIC AI & AUDIT GOVERNANCE — MASTER DEMONSTRATION")
    print("=" * 80)

    # 1. Agent Architectures
    print("\n\n>>> RUNNING DEMO 1: AGENT ARCHITECTURES & AUTONOMY LEVELS")
    arch_mod = importlib.import_module("01_agent_architectures")
    arch_mod.main()

    # 2. LangGraph Audit Agent
    print("\n\n>>> RUNNING DEMO 2: LANGGRAPH AUTONOMOUS AUDIT AGENT (3 TOOLS)")
    agent_mod = importlib.import_module("02_langgraph_audit_agent")
    agent_mod.main()

    # 3. Human in the loop
    print("\n\n>>> RUNNING DEMO 3: HUMAN-IN-THE-LOOP AUDIT APPROVAL GATE")
    hitl_mod = importlib.import_module("03_human_in_the_loop_audit")
    hitl_mod.main()

    # 4. Multi-Agent Team
    print("\n\n>>> RUNNING DEMO 4: MULTI-AGENT SUPERVISOR AUDIT TEAM")
    multi_mod = importlib.import_module("04_multi_agent_audit_team")
    multi_mod.main()

    print("\n\n" + "=" * 80)
    print("  ALL BLOCK D DEMONSTRATIONS COMPLETED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    run_all_demos()
