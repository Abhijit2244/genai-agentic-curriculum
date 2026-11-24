"""
03_human_in_the_loop_audit.py — Human-in-the-Loop (HITL) Audit Approval Gate
Demonstrates human-in-the-loop control for audit workflows:
- "Agents should assist the auditor, not replace judgement."
- Uses LangGraph `interrupt_before=["tools"]` when calling `flag_anomaly`.
- Enables senior auditor inspection, sign-off, state mutation, and resumption.
"""

from typing import TypedDict, Annotated, Sequence, Optional
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from config import get_llm, extract_text
try:
    from tools import query_ledger_csv, search_policy, flag_anomaly, get_flagged_anomalies, reset_anomalies
except ImportError:
    from .tools import query_ledger_csv, search_policy, flag_anomaly, get_flagged_anomalies, reset_anomalies


class HITLAuditState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    auditor_approved: Optional[bool]
    auditor_notes: Optional[str]


SYSTEM_PROMPT = """You are an AI Forensic Audit Assistant.
You assist human CPA auditors in detecting internal control failures.
TOOLS:
- query_ledger_csv: Look up transactions.
- search_policy: Look up internal controls policies.
- flag_anomaly: Flag an official audit exception in workpapers.

RULE: When you discover a violation, call flag_anomaly. An authorized human auditor will review and sign off before it is entered into the official audit workpapers.
"""


def build_hitl_audit_agent(checkpointer: Optional[MemorySaver] = None):
    """
    Builds a LangGraph agent with an interrupt breakpoint before tool execution.
    """
    tools = [query_ledger_csv, search_policy, flag_anomaly]
    model = get_llm(temperature=0.0).bind_tools(tools)

    def agent_node(state: HITLAuditState):
        messages = state["messages"]
        response = model.invoke(messages)
        return {"messages": [response]}

    def should_continue(state: HITLAuditState) -> str:
        last = state["messages"][-1]
        if hasattr(last, "tool_calls") and last.tool_calls:
            return "tools"
        return END

    tool_node = ToolNode(tools=tools, handle_tool_errors=True)

    workflow = StateGraph(HITLAuditState)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)

    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    workflow.add_edge("tools", "agent")

    # CRITICAL: Interrupt execution before entering the tools node
    # Allows human auditor inspection of the proposed exception
    return workflow.compile(
        checkpointer=checkpointer or MemorySaver(),
        interrupt_before=["tools"]
    )


def run_hitl_audit_demo():
    """
    Demonstrates the full Human-in-the-Loop lifecycle:
    1. Agent perceives anomaly and proposes `flag_anomaly`.
    2. Graph pauses at breakpoint `interrupt_before=["tools"]`.
    3. Human Auditor inspects evidence and reviews proposed finding.
    4. Human Auditor approves / modifies findings.
    5. Graph resumes and commits finding to workpapers.
    """
    print("\n" + "=" * 75)
    print("  HUMAN-IN-THE-LOOP (HITL) AUDIT APPROVAL DEMONSTRATION")
    print("=" * 75)
    reset_anomalies()

    checkpointer = MemorySaver()
    app = build_hitl_audit_agent(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": "audit-hitl-session-101"}}

    # Audit query targeting the weekend wire transfer
    query = (
        "Check transaction TXN-2026-008 for vendor 'Starlight Offshore Ltd'. "
        "Verify if it complied with our weekend wire transfer policies."
    )
    print(f"\n[Audit Assignment]: {query}\n")

    initial_messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=query),
    ]

    # --- PHASE 1: Run graph until breakpoint is hit ---
    print(">>> [Phase 1]: Agent running initial analysis...")
    for event in app.stream({"messages": initial_messages}, config=config):
        for node, update in event.items():
            print(f"    Executed Node: {node}")

    # Inspect state at breakpoint
    state_snapshot = app.get_state(config)
    print(f"\n[GRAPH PAUSED]: Next scheduled node: {state_snapshot.next}")

    # Extract pending tool call
    last_msg = state_snapshot.values["messages"][-1]
    pending_tool_calls = getattr(last_msg, "tool_calls", [])

    if not pending_tool_calls:
        print("No tool call proposed. Agent concluded without tools.")
        return

    # Check if the pending tool call is an inquiry or flag_anomaly
    pending_call = pending_tool_calls[0]
    print(f"\n>>> [PAUSED FOR HUMAN AUDITOR REVIEW]")
    print(f"    Pending Tool Call: {pending_call['name']}")
    print(f"    Arguments: {pending_call['args']}")

    # If it's query_ledger or search_policy, allow it to run and loop again
    while pending_call["name"] in ["query_ledger_csv", "search_policy"]:
        print(f"\n[Auditor Auto-Approving Inquiry Tool]: {pending_call['name']}...")
        app.invoke(None, config=config)
        state_snapshot = app.get_state(config)
        if not state_snapshot.next:
            break
        last_msg = state_snapshot.values["messages"][-1]
        pending_tool_calls = getattr(last_msg, "tool_calls", [])
        if not pending_tool_calls:
            break
        pending_call = pending_tool_calls[0]
        print(f"\n[GRAPH PAUSED AGAIN]: Next tool: {pending_call['name']}")
        print(f"Arguments: {pending_call['args']}")

    # Now we have reached flag_anomaly!
    if pending_call["name"] == "flag_anomaly":
        print("\n" + "#" * 65)
        print("  CRITICAL AUDIT ACTION: FLAG_ANOMALY DETECTED")
        print("  HUMAN REVIEWER SIGN-OFF REQUIRED")
        print("#" * 65)
        args = pending_call["args"]
        print(f"  • Transaction ID:     {args.get('transaction_id')}")
        print(f"  • Policy Control ID:  {args.get('policy_violation_code')}")
        print(f"  • Proposed Severity:  {args.get('severity')}")
        print(f"  • Forensic Rationale: {args.get('rationale')}")
        print(f"  • Proposed Action:    {args.get('recommended_action')}")
        print("#" * 65)

        # Senior Auditor Decision:
        # The auditor exercises professional skepticism:
        # Upgrades severity to 'CRITICAL' because it involves an offshore destination!
        print("\n[Senior Lead Auditor Action]:")
        print("  'Professional skepticism applied: Since the beneficiary is an offshore entity")
        print("   without CFO emergency clearance, I am UPGRADING severity from HIGH to CRITICAL")
        print("   and adding instructions to contact international AML compliance.'")

        updated_args = dict(args)
        updated_args["severity"] = "CRITICAL"
        updated_args["rationale"] = (
            f"[Auditor Modified]: {args.get('rationale')} — "
            "High AML exposure: Unregistered offshore wire with unauthorized weekend release."
        )

        # Mutate the pending message in LangGraph state
        modified_tool_call = {
            "name": "flag_anomaly",
            "args": updated_args,
            "id": pending_call["id"],
        }
        modified_ai_msg = AIMessage(
            content=last_msg.content,
            tool_calls=[modified_tool_call],
            id=last_msg.id,
        )

        app.update_state(
            config,
            {
                "messages": [modified_ai_msg],
                "auditor_approved": True,
                "auditor_notes": "Reviewed and upgraded to CRITICAL by Senior CPA Auditor."
            }
        )

        print("\n>>> [Phase 2]: Resuming graph with approved & mutated state...")
        # Resume execution
        for event in app.stream(None, config=config):
            for node, update in event.items():
                print(f"    Executed Node: {node}")

    # Final Verification
    anomalies = get_flagged_anomalies()
    print(f"\n{'='*75}")
    print(f"  AUDIT WORKPAPER REPOSITORY STATUS: {len(anomalies)} EXCEPTION(S) COMMITTED")
    for anom in anomalies:
        print(f"  • [{anom['exception_id']}] {anom['transaction_id']} | Severity: {anom['severity']}")
        print(f"    Rationale: {anom['rationale']}")
    print(f"{'='*75}\n")


def main():
    print("===================================================================")
    print("  BLOCK D — 03: HUMAN-IN-THE-LOOP (HITL) AUDIT GOVERNANCE")
    print("===================================================================")
    run_hitl_audit_demo()


if __name__ == "__main__":
    main()
