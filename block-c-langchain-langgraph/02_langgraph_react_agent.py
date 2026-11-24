"""
=============================================================================
02_langgraph_react_agent.py: Stateful ReAct Agent Loop Built with StateGraph
=============================================================================
Core Concepts Demonstrated:
1. Cyclical Graph Architecture: Why agents need state machines, not linear DAGs.
2. State & Reducers: `Annotated[Sequence[BaseMessage], add_messages]` for append-only state.
3. Nodes & Tools: Registering `@tool` functions and connecting `ToolNode`.
4. Conditional Routing: Inspecting `tool_calls` to decide whether to loop or terminate.
5. Step-by-Step Trajectory Streaming: Observing Thought ➔ Action ➔ Observation loops.
=============================================================================
"""

import warnings
warnings.filterwarnings("ignore")

from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from config import get_llm


# ── 1. Define Local Tools ──────────────────────────────────────────────────
@tool
def check_sla_credit_policy(plan_tier: str) -> str:
    """Check the contractual SLA uptime policy and hourly credit rates for a customer plan."""
    print(f"\n  [TOOL INVOKED]: check_sla_credit_policy(plan_tier='{plan_tier}')")
    rates = {
        "enterprise": "Contractual SLA: 99.99%. Credit Rate: $250.00 per hour of confirmed downtime.",
        "business": "Contractual SLA: 99.9%. Credit Rate: $75.00 per hour of confirmed downtime.",
        "developer": "Contractual SLA: 99.0%. Credit Rate: $10.00 credit voucher.",
    }
    return rates.get(plan_tier.lower().strip(), "Standard tier: No automated monetary credits.")


@tool
def calculate_downtime_credit(hourly_rate: float, downtime_hours: float) -> str:
    """Calculate the exact total credit compensation for confirmed outage hours."""
    print(f"\n  [TOOL INVOKED]: calculate_downtime_credit(rate={hourly_rate}, hours={downtime_hours})")
    total = hourly_rate * downtime_hours
    return f"Calculated Total Credit: ${total:.2f} USD for {downtime_hours} hours of downtime."


tools = [check_sla_credit_policy, calculate_downtime_credit]


# ── 2. Define State Schema with add_messages Reducer ───────────────────────
class AgentState(TypedDict):
    # add_messages handles appending new messages and deduplicating by ID
    messages: Annotated[Sequence[BaseMessage], add_messages]


# ── 3. Build Graph Nodes & Conditional Routing ─────────────────────────────
llm = get_llm(temperature=0.0)
model_with_tools = llm.bind_tools(tools)


def call_model(state: AgentState):
    """Agent node: Prompts the model with the current conversation state."""
    messages = state["messages"]
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}


def should_continue(state: AgentState):
    """Conditional Edge: Inspects if the LLM emitted a tool call or final text."""
    last_message = state["messages"][-1]
    # If the LLM requested a function call, route to 'tools' node
    if hasattr(last_message, "tool_calls") and len(last_message.tool_calls) > 0:
        return "tools"
    # Otherwise, the agent has formulated its final answer; route to END
    return END


def build_react_agent_graph():
    """Assembles and compiles the cyclical LangGraph workflow."""
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(tools))

    # Add Edges
    workflow.add_edge(START, "agent")
    
    # Conditional edge from agent: either execute tools or terminate
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END
        }
    )

    # Edge from tools back to agent: cyclical feedback loop!
    workflow.add_edge("tools", "agent")

    return workflow.compile()


def extract_text(content) -> str:
    """Normalize message content to plain string across all LLM response formats."""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        return "".join(part.get("text", "") for part in content if isinstance(part, dict))
    return str(content)


def run_react_agent_demo():
    print("\n" + "=" * 65)
    print("LANGGRAPH REACT AGENT DEMO (Cyclical State Machine)")
    print("=" * 65)

    agent_app = build_react_agent_graph()

    query = (
        "Customer ACME Corp is on the 'Enterprise' plan and experienced 3.5 hours "
        "of production database outage. What is their hourly credit rate, and what "
        "is the exact total compensation amount to credit to their account?"
    )

    print(f"[User Query]:\n  '{query}'\n")
    print("[Starting Cyclical Graph Execution...]")
    print("-" * 65)

    inputs = {"messages": [HumanMessage(content=query)]}

    # Stream graph execution step by step
    for event in agent_app.stream(inputs, stream_mode="values"):
        last_msg = event["messages"][-1]
        msg_type = type(last_msg).__name__
        
        if isinstance(last_msg, AIMessage) and last_msg.tool_calls:
            for tc in last_msg.tool_calls:
                print(f"[Graph Step: Agent Decision] --> Request Tool Call: {tc['name']}({tc['args']})")
        elif isinstance(last_msg, ToolMessage):
            print(f"[Graph Step: Tool Output]   --> {last_msg.content}")

    # Final answer
    final_text = extract_text(last_msg.content)
    print("-" * 65)
    print("\n[Final Grounded Answer from Agent]:")
    print(final_text.strip())
    print("\n" + "=" * 65)
    print("RE-ACT AGENT LOOP EXECUTED AND TERMINATED SUCCESSFULLY!")
    print("=" * 65)
    return final_text


if __name__ == "__main__":
    run_react_agent_demo()
