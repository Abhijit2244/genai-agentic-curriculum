"""
test_project.py — Automated Unit Test Suite for Block D: Agentic AI
Validates tools, graph compilation, state transitions, and HITL breakpoints.
"""

import unittest
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import importlib
from tools import query_ledger_csv, search_policy, flag_anomaly, get_flagged_anomalies, reset_anomalies

agent_mod = importlib.import_module("02_langgraph_audit_agent")
build_audit_agent = agent_mod.build_audit_agent

hitl_mod = importlib.import_module("03_human_in_the_loop_audit")
build_hitl_audit_agent = hitl_mod.build_hitl_audit_agent

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver


class TestBlockDAgenticAI(unittest.TestCase):

    def setUp(self):
        reset_anomalies()

    def test_01_ledger_query_tool(self):
        """Test pandas querying over general_ledger_2026.csv."""
        # Query vendor Apex
        res = query_ledger_csv.invoke({"vendor": "Apex", "limit": 5})
        self.assertIn("Apex Cloud Holdings", res)
        self.assertIn("TXN-2026-014", res)
        self.assertIn("49950", res)
        self.assertIn("49990", res)

        # Query missing PO
        res_no_po = query_ledger_csv.invoke({"po_number": "NONE"})
        self.assertIn("Nexus Global Advisory", res_no_po)
        self.assertIn("AUTO_RELEASED", res_no_po)

    def test_02_policy_rag_tool(self):
        """Test semantic retrieval over internal financial controls."""
        res = search_policy.invoke({"query": "dual authorization threshold 50000", "top_k": 1})
        self.assertIn("POL-IC-01", res)
        self.assertIn("50,000", res)

        res_structuring = search_policy.invoke({"query": "transaction splitting structuring", "top_k": 1})
        self.assertIn("POL-IC-02", res_structuring)

    def test_03_flag_anomaly_tool(self):
        """Test logging audit exceptions into workpapers."""
        res = flag_anomaly.invoke({
            "transaction_id": "TXN-2026-008",
            "policy_violation_code": "POL-IC-03",
            "severity": "CRITICAL",
            "rationale": "Unauthorized Saturday wire transfer to offshore entity without CFO sign-off.",
            "recommended_action": "Freeze wire and escalate to audit committee."
        })
        self.assertIn("OFFICIAL AUDIT WORKPAPER EXCEPTION RECORDED", res)
        self.assertIn("TXN-2026-008", res)
        self.assertIn("POL-IC-03", res)

        anomalies = get_flagged_anomalies()
        self.assertEqual(len(anomalies), 1)
        self.assertEqual(anomalies[0]["severity"], "CRITICAL")
        self.assertEqual(anomalies[0]["transaction_id"], "TXN-2026-008")

    def test_04_langgraph_agent_compilation(self):
        """Test compiling the LangGraph audit agent state machine."""
        app = build_audit_agent()
        self.assertIsNotNone(app)
        # Check node names
        self.assertIn("agent", app.nodes)
        self.assertIn("tools", app.nodes)

    def test_05_hitl_breakpoint(self):
        """Test that HITL agent interrupts execution before tool node."""
        checkpointer = MemorySaver()
        app = build_hitl_audit_agent(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": "test-hitl-thread-1"}}

        # Start execution
        app.invoke(
            {"messages": [HumanMessage(content="Look up transactions for vendor 'Apex Cloud Holdings'.")]},
            config=config
        )

        # Inspect state at breakpoint
        snapshot = app.get_state(config)
        self.assertEqual(snapshot.next, ("tools",))
        last_msg = snapshot.values["messages"][-1]
        self.assertTrue(len(last_msg.tool_calls) > 0)
        self.assertEqual(last_msg.tool_calls[0]["name"], "query_ledger_csv")


if __name__ == "__main__":
    unittest.main()
