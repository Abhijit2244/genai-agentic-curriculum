"""
04_multi_agent_audit_team.py — Multi-Agent Supervisor Pattern for Audit Teams
Coordinates specialized agents:
1. Supervisor (Orchestrator): Assesses progress and routes tasks.
2. DataAuditor: Forensic accountant analyzing transaction distributions and outliers via pandas.
3. PolicyAuditor: Regulatory specialist retrieving SOX 404 & SSAE-18 mandates via RAG.
4. Synthesizer: Incident Commander compiling the final Audit Memorandum.

Resolves Gemini model prefilling requirements by wrapping serialized history in HumanMessage.
"""

from typing import TypedDict, Annotated, Sequence, Literal
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from config import get_llm, extract_text
try:
    from tools import query_ledger_csv, search_policy, flag_anomaly
except ImportError:
    from .tools import query_ledger_csv, search_policy, flag_anomaly


# Define Shared Multi-Agent Team State
class AuditTeamState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    next_agent: str
    iteration: int


# Create specialized sub-agents
data_agent = create_react_agent(
    model=get_llm(temperature=0.0),
    tools=[query_ledger_csv],
    name="DataAuditor",
    prompt="You are a Forensic Data Auditor. Use query_ledger_csv to extract exact transaction numbers, dates, amounts, and PO numbers. Report facts clearly."
)

policy_agent = create_react_agent(
    model=get_llm(temperature=0.0),
    tools=[search_policy],
    name="PolicyAuditor",
    prompt="You are a Regulatory Compliance Auditor. Use search_policy to retrieve internal controls clauses and citations. Match facts to control rules."
)


def supervisor_node(state: AuditTeamState) -> dict:
    """
    Evaluates historical progress and routes to the next specialist or finishes.
    Wraps serialized history in a HumanMessage to guarantee Gemini compatibility.
    """
    history_lines = []
    for msg in state["messages"]:
        sender = getattr(msg, "name", None) or type(msg).__name__
        content = extract_text(msg.content)
        if content.strip():
            history_lines.append(f"[{sender}]: {content[:250]}")
    history_text = "\n".join(history_lines[-6:])

    prompt = [
        SystemMessage(content=(
            "You are the Audit Supervisor coordinating a team to audit general ledger transactions.\n"
            "WORKERS:\n"
            "- DataAuditor: Inspects ledger CSV for vendor amounts, PO status, dates.\n"
            "- PolicyAuditor: Retrieves SOX internal controls standards.\n"
            "- FINISH: Route here once both data and policies have been retrieved and evaluated.\n\n"
            "Respond with strictly ONE word: 'DataAuditor', 'PolicyAuditor', or 'FINISH'."
        )),
        HumanMessage(content=f"Current Audit Investigation Progress:\n{history_text}\n\nWho should act next?")
    ]

    response = get_llm(temperature=0.0).invoke(prompt)
    decision_text = extract_text(response.content).strip().upper()

    if "DATA" in decision_text and state.get("iteration", 0) == 0:
        next_step = "DataAuditor"
    elif "POLICY" in decision_text or state.get("iteration", 0) == 1:
        next_step = "PolicyAuditor"
    else:
        next_step = "FINISH"

    return {"next_agent": next_step, "iteration": state.get("iteration", 0) + 1}


def data_node(state: AuditTeamState) -> dict:
    """Invokes the Data Auditor."""
    result = data_agent.invoke({"messages": state["messages"]})
    last_msg = result["messages"][-1]
    return {"messages": [AIMessage(content=extract_text(last_msg.content), name="DataAuditor")]}


def policy_node(state: AuditTeamState) -> dict:
    """Invokes the Policy Compliance Auditor."""
    result = policy_agent.invoke({"messages": state["messages"]})
    last_msg = result["messages"][-1]
    return {"messages": [AIMessage(content=extract_text(last_msg.content), name="PolicyAuditor")]}


def synthesizer_node(state: AuditTeamState) -> dict:
    """Consolidates findings into a formal SOX 404 Audit Workpaper Memorandum."""
    history = "\n\n".join(f"{getattr(m, 'name', type(m).__name__)}: {extract_text(m.content)}" for m in state["messages"])
    prompt = [
        SystemMessage(content="You are the Lead Audit Partner. Draft an executive SOX 404 Audit Exception Memorandum."),
        HumanMessage(content=f"Forensic Investigation Findings:\n{history}\n\nDraft a formal memorandum with: 1. Executive Summary, 2. Control Deficiencies Identified, 3. Auditor Recommendation.")
    ]
    report = get_llm(temperature=0.0).invoke(prompt)
    return {"messages": [AIMessage(content=extract_text(report.content), name="AuditPartner")]}


def build_audit_team_graph():
    """Builds the multi-agent state graph."""
    workflow = StateGraph(AuditTeamState)

    workflow.add_node("Supervisor", supervisor_node)
    workflow.add_node("DataAuditor", data_node)
    workflow.add_node("PolicyAuditor", policy_node)
    workflow.add_node("Synthesizer", synthesizer_node)

    workflow.add_edge(START, "Supervisor")

    workflow.add_conditional_edges(
        "Supervisor",
        lambda state: state["next_agent"],
        {
            "DataAuditor": "DataAuditor",
            "PolicyAuditor": "PolicyAuditor",
            "FINISH": "Synthesizer"
        }
    )

    workflow.add_edge("DataAuditor", "Supervisor")
    workflow.add_edge("PolicyAuditor", "Supervisor")
    workflow.add_edge("Synthesizer", END)

    return workflow.compile(checkpointer=MemorySaver())


def run_multi_agent_audit(query: str):
    """Runs the multi-agent audit investigation."""
    print(f"\n{'='*75}")
    print(f"  MULTI-AGENT AUDIT TEAM INVESTIGATION")
    print(f"  Assignment: {query}")
    print(f"{'='*75}\n")

    app = build_audit_team_graph()
    config = {"configurable": {"thread_id": "audit-team-001"}}
    inputs = {"messages": [HumanMessage(content=query)], "iteration": 0}

    for event in app.stream(inputs, config=config, stream_mode="updates"):
        for node_name, state_update in event.items():
            print(f">>> [Node Activated]: {node_name}")
            if "messages" in state_update:
                last = state_update["messages"][-1]
                sender = getattr(last, "name", "Agent")
                text = extract_text(last.content)
                print(f"    [{sender} Output]:\n{text[:300]}...\n")


def main():
    print("===================================================================")
    print("  BLOCK D — 04: MULTI-AGENT SUPERVISOR AUDIT TEAM")
    print("===================================================================")

    query = (
        "Investigate transactions for vendor 'Apex Cloud Holdings'. Check for potential "
        "invoice structuring / threshold avoidance under our internal financial policies."
    )
    run_multi_agent_audit(query)


if __name__ == "__main__":
    main()
