"""
01_agent_architectures.py — Chatbot vs. Workflow vs. Autonomous Agent
Demonstrates the three paradigms of AI engineering and explains autonomy levels 0-5.
"""

from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from config import get_llm, extract_text


def run_level_1_chatbot(user_query: str) -> str:
    """
    Level 1: Chatbot (Stateless / Single-Turn Text In -> Text Out)
    No tools, no memory, no external grounding. Subject to hallucinations and frozen weights.
    """
    print("\n--- [LEVEL 1: CHATBOT] ---")
    llm = get_llm(temperature=0.3)
    prompt = [
        SystemMessage(content="You are a corporate accounting assistant."),
        HumanMessage(content=user_query),
    ]
    response = llm.invoke(prompt)
    output = extract_text(response.content)
    print(f"Chatbot Output:\n{output[:350]}...")
    return output


def run_level_2_deterministic_workflow(vendor_name: str) -> Dict[str, Any]:
    """
    Level 2: Deterministic Workflow (Hardcoded DAG Pipeline)
    Fixed steps: Step A -> Step B -> Step C.
    The code, NOT the LLM, decides the sequence of tool execution.
    """
    print("\n--- [LEVEL 2: DETERMINISTIC WORKFLOW (DAG)] ---")
    try:
        from tools import query_ledger_csv, search_policy
    except ImportError:
        from .tools import query_ledger_csv, search_policy

    # Step 1: Deterministic data lookup via code
    print(f"[Workflow Step 1]: Executing fixed ledger query for vendor '{vendor_name}'...")
    ledger_data = query_ledger_csv.invoke({"vendor": vendor_name, "limit": 5})

    # Step 2: Deterministic policy lookup via code
    print("[Workflow Step 2]: Fetching dual authorization policy...")
    policy_data = search_policy.invoke({"query": "dual authorization threshold 50000", "top_k": 1})

    # Step 3: LLM performs constrained synthesis over the pre-fetched data
    print("[Workflow Step 3]: Calling LLM to summarize findings...")
    llm = get_llm(temperature=0.0)
    prompt = [
        SystemMessage(content="You are a compliance reporting assistant. Summarize the provided data."),
        HumanMessage(content=f"Ledger Data:\n{ledger_data}\n\nPolicy Reference:\n{policy_data}\n\nProvide a 2-sentence summary.")
    ]
    summary = extract_text(llm.invoke(prompt).content)
    print(f"Workflow Summary:\n{summary}")
    return {"ledger": ledger_data, "policy": policy_data, "summary": summary}


def explain_autonomy_levels():
    """Prints the 6 levels of AI Autonomy (0 to 5) for systems engineering."""
    print("\n" + "=" * 70)
    print("                     LEVELS OF AI AUTONOMY (0 - 5)")
    print("=" * 70)
    levels = [
        ("Level 0: No AI (Deterministic)", "Static procedural code, regex, hardcoded SQL rules."),
        ("Level 1: Conversational Chatbot", "Single LLM call; text generation without tools or external perception."),
        ("Level 2: Directed DAG Workflow", "Code directs tool calls; LLM only formats or classifies intermediate data."),
        ("Level 3: Autonomous ReAct Agent", "LLM dynamically selects tools, observes outputs, loops, and self-corrects."),
        ("Level 4: Multi-Agent Collaboration", "Specialized agents (Planner, Coder, Reviewer) coordinate via supervisor/swarm."),
        ("Level 5: Fully Autonomous Swarm", "Self-directing agents with dynamic goal discovery, code generation, and deployment."),
    ]
    for lvl, desc in levels:
        print(f"  • {lvl:<35}: {desc}")
    print("=" * 70)


def main():
    print("===================================================================")
    print("  BLOCK D — AGENT ARCHITECTURES: CHATBOT vs WORKFLOW vs AGENT")
    print("===================================================================")
    
    explain_autonomy_levels()

    # 1. Chatbot test
    run_level_1_chatbot("Did we have any suspicious wire transfers to Starlight Offshore Ltd in March 2026?")

    # 2. Workflow test
    run_level_2_deterministic_workflow("Apex Cloud")


if __name__ == "__main__":
    main()
