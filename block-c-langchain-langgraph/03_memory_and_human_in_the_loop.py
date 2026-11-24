"""
=============================================================================
03_memory_and_human_in_the_loop.py: Checkpointing, Memory & Human Approval
=============================================================================
Core Concepts Demonstrated:
1. State Persistence: Using `MemorySaver` to checkpoint agent state across turns.
2. Multi-Turn Thread Isolation: Maintaining separate conversation memory per `thread_id`.
3. Human-in-the-Loop (HITL): Halting graph execution via `interrupt_before=["tools"]`.
4. State Inspection & Resumption: Reviewing pending tool calls before granting approval.
=============================================================================
"""

import warnings
warnings.filterwarnings("ignore")

from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from config import get_llm


# ── 1. Define High-Stakes Dangerous Action Tool ─────────────────────────────
@tool
def execute_database_failover(cluster_id: str, target_region: str, dry_run: bool = False) -> str:
    """Execute a live database failover and DNS reroute for an enterprise cluster."""
    print(f"\n  [HIGH-STAKES ACTION EXECUTED]")
    print(f"  --> Swapping cluster '{cluster_id}' to target region '{target_region}' (dry_run={dry_run})")
    return f"SUCCESS: Cluster '{cluster_id}' successfully failed over to '{target_region}'. Traffic re-routed."


tools = [execute_database_failover]


class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


# ── 2. Build the ReAct Graph with Breakpoints ──────────────────────────────
llm = get_llm(temperature=0.0)
model_with_tools = llm.bind_tools(tools)


def call_model(state: State):
    messages = state["messages"]
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}


def should_continue(state: State):
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and len(last_message.tool_calls) > 0:
        return "tools"
    return END


def build_persisted_agent():
    builder = StateGraph(State)
    builder.add_node("agent", call_model)
    builder.add_node("tools", ToolNode(tools))

    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    builder.add_edge("tools", "agent")

    checkpointer = MemorySaver()
    # interrupt_before=["tools"]: Pauses execution right before executing any tool!
    return builder.compile(checkpointer=checkpointer, interrupt_before=["tools"])


# ── 3. Part A: Multi-Turn Memory Persistence Demo ──────────────────────────
def run_multi_turn_memory_demo():
    print("\n" + "=" * 65)
    print("PART 1: Multi-Turn Conversation Memory via Thread Checkpoints")
    print("=" * 65)

    app = build_persisted_agent()
    thread_config = {"configurable": {"thread_id": "session_user_99"}}

    # Turn 1: Providing context
    turn1_msg = "Hello, my name is Alex and I manage the 'us-east-cluster-primary' database."
    print(f"[User Turn 1]: '{turn1_msg}'")
    res1 = app.invoke({"messages": [HumanMessage(content=turn1_msg)]}, config=thread_config)
    print(f"[Agent Reply 1]: {res1['messages'][-1].content.strip()}\n")

    # Turn 2: Querying previous context without re-stating customer or cluster
    turn2_msg = "What cluster do I manage and what is my name?"
    print(f"[User Turn 2]: '{turn2_msg}'")
    res2 = app.invoke({"messages": [HumanMessage(content=turn2_msg)]}, config=thread_config)
    print(f"[Agent Reply 2]: {res2['messages'][-1].content.strip()}")
    print("-" * 65)


# ── 4. Part B: Human-in-the-Loop (HITL) Approval Demo ───────────────────────
def run_hitl_approval_demo(simulate_approval: bool = True):
    print("\n" + "=" * 65)
    print("PART 2: Human-in-the-Loop (HITL) Safety Breakpoint Demo")
    print("=" * 65)

    app = build_persisted_agent()
    thread_config = {"configurable": {"thread_id": "emergency_failover_thread"}}

    request = "Emergency: Please execute a live database failover on cluster 'prod-db-omega' to 'us-west-2'."
    print(f"[Operator Prompt]: '{request}'\n")

    print("[Phase 1: Agent processes request until safety breakpoint...]")
    app.invoke({"messages": [HumanMessage(content=request)]}, config=thread_config)

    # Inspect paused state
    snapshot = app.get_state(thread_config)
    print(f"--> Graph Current Status: Suspended at node '{snapshot.next}'")

    last_ai_message = snapshot.values["messages"][-1]
    pending_tool_call = last_ai_message.tool_calls[0]

    print("\n" + "#" * 60)
    print("⚠️  HUMAN AUDITOR APPROVAL GATEWAY ⚠️")
    print(f"  Pending Function : {pending_tool_call['name']}()")
    print(f"  Requested Args   : {pending_tool_call['args']}")
    print("#" * 60)

    if simulate_approval:
        print("\n[Human Operator Decision]: ✅ APPROVED. Resuming graph execution...")
        # Passing None resumes execution from the exact suspended breakpoint!
        final_state = app.invoke(None, config=thread_config)
        print("\n[Final Output after Human Approval]:")
        print(final_state["messages"][-1].content.strip())
    else:
        print("\n[Human Operator Decision]: ❌ REJECTED. Aborting destructive action.")

    print("=" * 65)


def run_all_memory_demos():
    run_multi_turn_memory_demo()
    run_hitl_approval_demo(simulate_approval=True)


if __name__ == "__main__":
    run_all_memory_demos()
