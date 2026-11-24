"""
02_langgraph_audit_agent.py — LangGraph Autonomous Financial Audit Agent
Implements a state machine agent equipped with 3 tools:
1. query_ledger_csv (pandas ledger querying)
2. search_policy (in-memory RAG over SOX 404 policies)
3. flag_anomaly (audit workpaper exception logging)

Uses LangGraph StateGraph, ToolNode, and MemorySaver checkpointer.
"""

from typing import TypedDict, Annotated, Sequence, Optional
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from config import get_llm, extract_text
try:
    from tools import query_ledger_csv, search_policy, flag_anomaly
except ImportError:
    from .tools import query_ledger_csv, search_policy, flag_anomaly


# Define Graph State Schema
class AuditAgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


SYSTEM_PROMPT = """You are an elite Senior Forensic Auditor and Internal Controls Compliance Agent.
Your mandate is to examine general ledger transactions, cross-reference them against internal compliance policies (SOX 404 / SSAE-18), and flag violations.

AVAILABLE TOOLS:
1. query_ledger_csv: Use this to search and inspect financial transactions using pandas filters (vendor, min_amount, max_amount, po_number, etc.).
2. search_policy: Use this to retrieve relevant internal control clauses, authorization thresholds, and compliance rules.
3. flag_anomaly: Use this to formally log an official audit exception in workpapers when a clear policy violation is discovered.

INVESTIGATION METHODOLOGY:
1. Inspect the relevant ledger transactions using query_ledger_csv.
2. Cross-reference questionable transactions against internal control policies using search_policy.
3. If a policy violation exists (e.g. structuring, unauthorized weekend wire, duplicate payment, missing PO), invoke flag_anomaly with exact transaction ID, policy code, severity, and rationale.
4. Provide a clear, professional summary of your forensic findings to the lead auditor.
"""


def build_audit_agent(checkpointer: Optional[MemorySaver] = None):
    """Compiles and returns the LangGraph Audit Agent state machine."""
    tools = [query_ledger_csv, search_policy, flag_anomaly]
    model = get_llm(temperature=0.0).bind_tools(tools)

    def agent_node(state: AuditAgentState):
        """Executes LLM reasoning with bound tools."""
        messages = state["messages"]
        response = model.invoke(messages)
        return {"messages": [response]}

    def should_continue(state: AuditAgentState) -> str:
        """Determines whether to execute tools or finish."""
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END

    tool_node = ToolNode(tools=tools, handle_tool_errors=True)

    workflow = StateGraph(AuditAgentState)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)

    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    workflow.add_edge("tools", "agent")

    return workflow.compile(checkpointer=checkpointer or MemorySaver())


def run_audit_investigation(user_query: str, thread_id: str = "audit-session-001") -> str:
    """Executes a forensic investigation session with state tracking."""
    print(f"\n{'='*70}")
    print(f"  STARTING FORENSIC AUDIT INVESTIGATION [Thread: {thread_id}]")
    print(f"  Query: {user_query}")
    print(f"{'='*70}\n")

    checkpointer = MemorySaver()
    app = build_audit_agent(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": thread_id}}

    initial_messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_query),
    ]

    # Stream graph execution
    step_num = 1
    final_output = ""
    for event in app.stream({"messages": initial_messages}, config=config, stream_mode="updates"):
        for node_name, state_update in event.items():
            print(f"--- [Step {step_num}: Node '{node_name}'] ---")
            messages = state_update.get("messages", [])
            for msg in messages:
                if isinstance(msg, AIMessage):
                    if msg.tool_calls:
                        for tc in msg.tool_calls:
                            print(f"  [Tool Call]: {tc['name']}({tc['args']})")
                    else:
                        text = extract_text(msg.content)
                        print(f"  [Agent Synthesis]:\n{text}\n")
                        final_output = text
                elif msg.type == "tool":
                    print(f"  [Tool Output ({msg.name})]: {msg.content[:200]}...\n")
            step_num += 1

    return final_output


def main():
    print("===================================================================")
    print("  BLOCK D — 02: LANGGRAPH AUTONOMOUS AUDIT AGENT (3 TOOLS)")
    print("===================================================================")

    # Investigate the structuring anomaly around $50,000 threshold
    query = (
        "Investigate transactions with vendor 'Apex Cloud Holdings'. Check if they "
        "comply with our internal dual-authorization policies or if any anomalies must be flagged."
    )
    run_audit_investigation(query, thread_id="apex-audit-001")


if __name__ == "__main__":
    main()
