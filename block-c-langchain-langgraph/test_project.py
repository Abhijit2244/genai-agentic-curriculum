"""
Automated Test Verification for Block C: LangChain & LangGraph Mastery Project
"""

import unittest
from importlib import import_module
from langchain_core.messages import HumanMessage


def extract_text(content) -> str:
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        return "".join(part.get("text", "") for part in content if isinstance(part, dict))
    return str(content)


class TestLangChainLangGraph(unittest.TestCase):
    def test_01_lcel_structured_output(self):
        mod1 = import_module("01_langchain_lcel_chains")
        analysis = mod1.run_structured_output_chain_demo()
        self.assertIsNotNone(analysis)
        self.assertEqual(analysis.__class__.__name__, "IncidentAnalysis")
        self.assertTrue(len(analysis.remediation_steps) >= 1)

    def test_02_react_agent_execution(self):
        mod2 = import_module("02_langgraph_react_agent")
        result = mod2.run_react_agent_demo()
        self.assertIsNotNone(result)
        # Should calculate total for enterprise (250/hr * 3.5 hrs = 875)
        self.assertTrue("875" in result or "credit" in result.lower())

    def test_03_memory_persistence(self):
        mod3 = import_module("03_memory_and_human_in_the_loop")
        app = mod3.build_persisted_agent()
        thread_cfg = {"configurable": {"thread_id": "test_thread_unique_42"}}
        
        # Turn 1
        app.invoke({"messages": [HumanMessage(content="My secret server name is 'TITAN-X'")]}, config=thread_cfg)
        
        # Turn 2: Query memory
        res2 = app.invoke({"messages": [HumanMessage(content="What is my secret server name?")]}, config=thread_cfg)
        reply = extract_text(res2["messages"][-1].content)
        self.assertIn("TITAN-X", reply)

    def test_04_hitl_breakpoint(self):
        mod3 = import_module("03_memory_and_human_in_the_loop")
        app = mod3.build_persisted_agent()
        cfg = {"configurable": {"thread_id": "hitl_test_thread"}}
        
        # Invoke dangerous action
        app.invoke(
            {"messages": [HumanMessage(content="Failover cluster 'db-test' to 'us-west-1'")]},
            config=cfg
        )
        snapshot = app.get_state(cfg)
        # Assert that execution suspended at the tool node
        self.assertIn("tools", snapshot.next)
        
        # Resume with approval
        res = app.invoke(None, config=cfg)
        final_text = extract_text(res["messages"][-1].content)
        self.assertTrue("Cluster" in final_text or "db-test" in final_text or "failover" in final_text.lower())

    def test_05_multi_agent_supervisor(self):
        mod4 = import_module("04_multi_agent_supervisor")
        report = mod4.run_multi_agent_demo()
        self.assertIsNotNone(report)
        self.assertTrue(len(report) > 50)


if __name__ == "__main__":
    unittest.main()
