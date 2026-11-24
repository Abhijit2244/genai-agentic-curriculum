"""
=============================================================================
03_tool_calling.py: Function Calling / Tool Calling (The Foundation of Agents)
=============================================================================
Block A Core Concepts Demonstrated:
1. Tool / Function Calling: How LLMs connect to the real world (APIs, DBs, Python functions).
2. Agent Loop Foundation:
   - User requests information the LLM does not know (or real-time state).
   - LLM recognizes it needs a tool and generates structured tool arguments.
   - The tool executes in the local Python environment.
   - The result is sent back to the LLM.
   - LLM provides a grounded, truthful final answer (preventing hallucinations!).
3. Bridge to Agentic AI & MCP: Tool calling is the identical primitive that powers
   autonomous agents, LangGraph/CrewAI, and the Model Context Protocol (MCP).
=============================================================================
"""

from google.genai import types
from config import get_gemini_client, DEFAULT_MODEL


# Define our local Python tool.
# Note: Google GenAI inspects the function name, docstring, and type annotations
# to automatically generate the function schema for the LLM!
def get_service_health(service_name: str, region: str = "us-east") -> str:
    """Check the real-time health, latency, and status of a cloud microservice.
    
    Args:
        service_name: The name of the service (e.g., 'auth-service', 'payment-gateway', 'vector-db').
        region: Cloud region where the service is deployed (e.g., 'us-east', 'eu-west').
        
    Returns:
        A formatted string with status, uptime, latency, and active alerts.
    """
    print(f"\n[TOOL EXECUTION TRIGGERED]")
    print(f"  --> Function: get_service_health()")
    print(f"  --> Arguments: service_name='{service_name}', region='{region}'")
    
    # Mock real-time backend database / telemetry lookup
    database = {
        "payment-gateway": {"status": "HEALTHY", "latency_ms": 42, "uptime": "99.99%"},
        "auth-service": {"status": "DEGRADED", "latency_ms": 310, "uptime": "98.50%", "alert": "High CPU load"},
        "vector-db": {"status": "HEALTHY", "latency_ms": 15, "uptime": "100.0%"},
    }

    key = service_name.lower().strip()
    data = database.get(key, {"status": "UNKNOWN", "latency_ms": 0, "uptime": "N/A"})
    
    result = (
        f"Service '{service_name}' in region '{region}': Status={data['status']}, "
        f"Latency={data['latency_ms']}ms, Uptime={data['uptime']}"
    )
    if "alert" in data:
        result += f", Alert='{data['alert']}'"
    
    print(f"  --> Tool Output Returned: {result}\n")
    return result


def run_tool_calling_demo():
    print("\n" + "=" * 65)
    print("TOOL CALLING (FUNCTION CALLING) DEMO")
    print("=" * 65)

    client = get_gemini_client()

    # Create a chat session with registered tools
    # Gemini SDK's client.chats automatically handles Automatic Function Calling (AFC):
    # It receives the LLM's function call, invokes get_service_health, and returns the result!
    chat = client.chats.create(
        model=DEFAULT_MODEL,
        config=types.GenerateContentConfig(
            tools=[get_service_health],
            temperature=0.0,  # Zero temperature for deterministic tool invocation
            system_instruction=(
                "You are an SRE Operations Copilot. Always check service health using "
                "the provided tool before answering user questions about system status."
            ),
        ),
    )

    user_query = "What is the current health and latency of the auth-service in us-east?"
    print(f"[User Query]:\n  '{user_query}'\n")

    print("[Sending query to Gemini Agent...]")
    response = chat.send_message(user_query)

    print("-" * 65)
    print("[Agent Final Grounded Response]:")
    print(response.text.strip())
    print("-" * 65)
    print("\n[Why This Matters]:")
    print("  • The model did NOT guess or hallucinate the latency or status.")
    print("  • It determined that 'get_service_health' was needed, formulated the parameters,")
    print("    consumed the tool output, and summarized the factual truth for the user.")
    print("=" * 65)
    return response.text


if __name__ == "__main__":
    run_tool_calling_demo()
