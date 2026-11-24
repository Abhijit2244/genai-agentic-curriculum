"""
=============================================================================
04_multi_agent_supervisor.py: Multi-Agent Collaboration & Supervisor Pattern
=============================================================================
Core Concepts Demonstrated:
1. Multi-Agent Systems: Splitting complex work across specialized autonomous agents.
2. The Supervisor / Router Pattern: A central orchestrator delegating tasks dynamically.
3. Domain Specialization:
   - Security Auditor Agent: Focuses on CVE scanning & compliance rules.
   - DevOps Engineer Agent: Focuses on Kubernetes pods & infrastructure health.
4. Unified Synthesis: Aggregating findings from multiple agents into an executive report.
=============================================================================
"""

import warnings
warnings.filterwarnings("ignore")

from typing import Annotated, Sequence, TypedDict, Literal
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from config import get_llm


# ── 1. Define Specialized Worker Tools ─────────────────────────────────────
@tool
def scan_cve_vulnerabilities(service_name: str) -> str:
    """Run an automated security scan for known CVEs on a microservice container image."""
    print(f"    --> [Security Agent Tool]: scan_cve_vulnerabilities('{service_name}')")
    database = {
        "payment-api": "FOUND 1 Critical CVE (CVE-2026-4412, CVSS 9.8 in base glibc image). Immediate patch required.",
        "auth-service": "All clean. Zero critical or high severity CVEs detected.",
    }
    return database.get(service_name.lower().strip(), "Scan complete. 0 vulnerabilities found.")


@tool
def inspect_kubernetes_pods(namespace: str) -> str:
    """Inspect the status, restarts, and memory utilization of Kubernetes pods."""
    print(f"    --> [DevOps Agent Tool]: inspect_kubernetes_pods('{namespace}')")
    return (
        f"Namespace '{namespace}': 3/3 pods Running. "
        "Pod 'payment-api-7b9f-x9' has 4 restarts in the last hour due to OOMKilled."
    )


# ── 2. Define Supervisor Routing Schema ────────────────────────────────────
class SupervisorDecision(BaseModel):
    next_agent: Literal["SecurityAuditor", "DevOpsEngineer", "FINISH"] = Field(
        description="The next specialized agent to route to, or 'FINISH' if sufficient data has been collected."
    )
    routing_reason: str = Field(description="Explanation of why this agent was selected")


# ── 3. Define Graph State ──────────────────────────────────────────────────
class MultiAgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    next_worker: str
    audit_findings: list[str]


# ── 4. Build Worker and Supervisor Nodes ───────────────────────────────────
llm = get_llm(temperature=0.0)


def extract_text(content) -> str:
    """Normalize message content to plain string across all LLM response formats."""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        return "".join(part.get("text", "") for part in content if isinstance(part, dict))
    return str(content)


def supervisor_node(state: MultiAgentState):
    """Supervisor determines whether to route to Security, DevOps, or Finish."""
    messages = state["messages"]
    
    transcript = []
    for msg in messages:
        sender = getattr(msg, "name", None) or type(msg).__name__
        transcript.append(f"{sender}: {extract_text(msg.content)}")
    
    history_block = "\n".join(transcript)
    
    system_prompt = (
        "You are the Lead Systems Supervisor managing two specialists:\n"
        "1. 'SecurityAuditor': Handles CVE scans, vulnerability checks, and security audits.\n"
        "2. 'DevOpsEngineer': Handles Kubernetes pod inspections and infrastructure telemetry.\n\n"
        "Review the conversation history and specialist reports. "
        "If a domain specialist's task is still pending, route to them. "
        "If both tasks are completed, route to 'FINISH'."
    )
    
    user_prompt = f"Current Progress:\n{history_block}\n\nDecide next specialist or FINISH."
    
    router_llm = llm.with_structured_output(SupervisorDecision)
    decision: SupervisorDecision = router_llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])
    
    print(f"\n[Supervisor Decision] --> Route To: '{decision.next_agent}' (Reason: {decision.routing_reason})")
    return {"next_worker": decision.next_agent}


def security_worker_node(state: MultiAgentState):
    """Specialized Security Auditor agent."""
    print("  [Executing Security Auditor Agent...]")
    sec_model = llm.bind_tools([scan_cve_vulnerabilities])
    
    # Check if tool is needed
    prompt = [
        SystemMessage(content="You are a senior security auditor. Use scan_cve_vulnerabilities to inspect requested services."),
        HumanMessage(content="Scan the requested payment-api container image for CVEs.")
    ]
    
    res = sec_model.invoke(prompt)
    tool_results = []
    if res.tool_calls:
        for tc in res.tool_calls:
            out = scan_cve_vulnerabilities.invoke(tc["args"])
            tool_results.append(out)
    
    summary = f"Security Audit Result: {tool_results[0] if tool_results else extract_text(res.content)}"
    return {
        "messages": [AIMessage(content=summary, name="SecurityAuditor")],
        "audit_findings": [summary]
    }


def devops_worker_node(state: MultiAgentState):
    """Specialized DevOps Engineer agent."""
    print("  [Executing DevOps Engineer Agent...]")
    devops_model = llm.bind_tools([inspect_kubernetes_pods])
    
    prompt = [
        SystemMessage(content="You are a senior DevOps engineer. Use inspect_kubernetes_pods to check pod status."),
        HumanMessage(content="Inspect the Kubernetes pod status in the production namespace.")
    ]
    
    res = devops_model.invoke(prompt)
    tool_results = []
    if res.tool_calls:
        for tc in res.tool_calls:
            out = inspect_kubernetes_pods.invoke(tc["args"])
            tool_results.append(out)
            
    summary = f"DevOps Telemetry Result: {tool_results[0] if tool_results else extract_text(res.content)}"
    return {
        "messages": [AIMessage(content=summary, name="DevOpsEngineer")],
        "audit_findings": [summary]
    }


def synthesizer_node(state: MultiAgentState):
    """Formulates the final unified report incorporating all agent findings."""
    print("\n[Synthesizer Node] --> Generating Executive Unified Summary...")
    findings = "\n".join(f"• {f}" for f in state.get("audit_findings", []))
    prompt = [
        SystemMessage(content=(
            "You are the Operations Incident Commander. Synthesize a unified executive status "
            "report using the specialist findings below. Use bullet points."
        )),
        HumanMessage(content=f"Specialist Findings Collected:\n{findings}\n\nProvide the executive summary.")
    ]
    
    final_report = llm.invoke(prompt)
    return {"messages": [final_report]}


# ── 5. Assemble and Compile Multi-Agent Graph ──────────────────────────────
def build_multi_agent_graph():
    workflow = StateGraph(MultiAgentState)

    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("SecurityAuditor", security_worker_node)
    workflow.add_node("DevOpsEngineer", devops_worker_node)
    workflow.add_node("synthesizer", synthesizer_node)

    # Edge from START to supervisor
    workflow.add_edge(START, "supervisor")

    # Conditional router from supervisor
    workflow.add_conditional_edges(
        "supervisor",
        lambda state: state["next_worker"],
        {
            "SecurityAuditor": "SecurityAuditor",
            "DevOpsEngineer": "DevOpsEngineer",
            "FINISH": "synthesizer"
        }
    )

    # Workers report back to supervisor!
    workflow.add_edge("SecurityAuditor", "supervisor")
    workflow.add_edge("DevOpsEngineer", "supervisor")
    workflow.add_edge("synthesizer", END)

    return workflow.compile()


def run_multi_agent_demo():
    print("\n" + "=" * 65)
    print("MULTI-AGENT SUPERVISOR ORCHESTRATION DEMO")
    print("=" * 65)

    multi_agent_app = build_multi_agent_graph()

    task = (
        "Perform a full production audit on the 'payment-api' service: "
        "1. Check if there are any critical CVE security vulnerabilities. "
        "2. Inspect the live Kubernetes pod stability in the 'production' namespace."
    )

    print(f"[Mission Objective]:\n  '{task}'\n")
    print("[Starting Multi-Agent Swarm Execution...]")
    print("-" * 65)

    initial_state = {
        "messages": [HumanMessage(content=task)],
        "next_worker": "supervisor",
        "audit_findings": []
    }

    final_state = multi_agent_app.invoke(initial_state)

    final_text = extract_text(final_state["messages"][-1].content)
    print("-" * 65)
    print("\n[Executive Incident Commander Report]:")
    print(final_text.strip())
    print("\n" + "=" * 65)
    print("MULTI-AGENT COLLABORATION COMPLETED SUCCESSFULLY!")
    print("=" * 65)
    return final_text


if __name__ == "__main__":
    run_multi_agent_demo()
