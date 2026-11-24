"""
agent_mcp_integration.py — LangChain/Gemini Agent Integrated with MCP Server
Demonstrates:
1. Connecting an autonomous LLM Agent to an external MCP Server via stdio.
2. Ingesting authoritative compliance context via MCP Resource (invoice://policy/compliance-rules).
3. Exposing MCP Tools (get_invoice, find_duplicates) to the LLM.
4. Performing an autonomous forensic invoice audit with verified policy citations.
"""

import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List

from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from config import get_llm, extract_text

BASE_DIR = Path(__file__).resolve().parent
SERVER_SCRIPT = BASE_DIR / "mcp_server.py"


class GetInvoiceInput(BaseModel):
    id: str = Field(description="The unique invoice identifier, e.g. 'INV-2026-003'.")


class FindDuplicatesInput(BaseModel):
    file: str = Field(default="invoices.json", description="The invoice database file to scan.")


async def run_mcp_agent_audit(target_invoice_id: str = "INV-2026-003") -> str:
    """
    Connects to MCP server, fetches policy resource, binds tools,
    and executes an autonomous audit investigation.
    """
    print("\n" + "=" * 75)
    print("      AUTONOMOUS AGENT + MCP SERVER FORENSIC AUDIT")
    print("=" * 75)
    print(f"Target Invoice: {target_invoice_id}")
    print(f"Server Host:    {SERVER_SCRIPT}\n")

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_SCRIPT)],
        env=None
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            
            # 1. Initialize MCP Session
            await session.initialize()
            print("[MCP Handshake]: JSON-RPC 2.0 connection established.")

            # 2. Read Compliance Policy Resource from MCP Server
            print("[MCP Resource]: Reading 'invoice://policy/compliance-rules'...")
            policy_resource = await session.read_resource("invoice://policy/compliance-rules")
            policy_content = policy_resource.contents[0].text if hasattr(policy_resource.contents[0], "text") else str(policy_resource.contents[0])
            print(f"[MCP Resource]: Retrieved {len(policy_content)} characters of compliance rules.\n")

            # 3. Create Tool wrappers that route directly to MCP session.call_tool
            async def _get_invoice_wrapper(id: str) -> str:
                res = await session.call_tool("get_invoice", {"id": id})
                return res.content[0].text if res.content else "No output."

            async def _find_duplicates_wrapper(file: str = "invoices.json") -> str:
                res = await session.call_tool("find_duplicates", {"file": file})
                return res.content[0].text if res.content else "No output."

            # Construct LangChain StructuredTools bound to the MCP server
            tools = [
                StructuredTool.from_function(
                    coroutine=_get_invoice_wrapper,
                    name="get_invoice",
                    description="Look up a single corporate invoice by its unique ID (e.g. 'INV-2026-003').",
                    args_schema=GetInvoiceInput
                ),
                StructuredTool.from_function(
                    coroutine=_find_duplicates_wrapper,
                    name="find_duplicates",
                    description="Scan invoice database for duplicate submissions, structuring, and missing POs.",
                    args_schema=FindDuplicatesInput
                )
            ]

            # 4. Bind Tools to Gemini Model
            model = get_llm(temperature=0.0).bind_tools(tools)
            tool_map = {t.name: t for t in tools}

            # 5. Build Grounded Prompt with MCP Policy Resource
            system_instruction = (
                "You are an Elite Forensic Accounting & AP Compliance Audit Agent.\n"
                "Your objective is to audit the requested invoice for fraud, duplicate billing, "
                "structuring, or internal control deficiencies.\n\n"
                f"--- GOVERNING COMPLIANCE POLICY (FROM MCP RESOURCE) ---\n"
                f"{policy_content}\n"
                "--------------------------------------------------------\n\n"
                "INVESTIGATION PROTOCOL:\n"
                "1. Fetch the invoice metadata using 'get_invoice'.\n"
                "2. Scan for duplicates or systemic anomalies across the dataset using 'find_duplicates'.\n"
                "3. Cross-reference findings against the governing compliance policy.\n"
                "4. Draft a formal Audit Exception Memorandum with: Executive Summary, Violated Control Code, Evidence, and Recommendation."
            )

            messages: List[Any] = [
                SystemMessage(content=system_instruction),
                HumanMessage(content=f"Please audit invoice '{target_invoice_id}' and identify if any compliance rules were violated.")
            ]

            print(f">>> [Agent Investigation Started]: Auditing {target_invoice_id}...")

            # 6. Execute ReAct Loop
            max_steps = 6
            final_response = ""
            for step in range(1, max_steps + 1):
                print(f"\n--- [Agent Reasoning Turn {step}] ---")
                ai_message = await model.ainvoke(messages)
                messages.append(ai_message)

                if not ai_message.tool_calls:
                    final_response = extract_text(ai_message.content)
                    print(f"\n[Final Audit Memorandum Emitted]:\n\n{final_response}\n")
                    break

                for tc in ai_message.tool_calls:
                    tool_name = tc["name"]
                    tool_args = tc["args"]
                    tool_call_id = tc["id"]
                    print(f"  [Action -> MCP Tool]: {tool_name}({tool_args})")

                    target_tool = tool_map[tool_name]
                    tool_output = await target_tool.ainvoke(tool_args)
                    print(f"  [Observation <- MCP Server]: {str(tool_output)[:160]}...")

                    messages.append(ToolMessage(
                        content=str(tool_output),
                        tool_call_id=tool_call_id,
                        name=tool_name
                    ))

            print("=" * 75)
            print("  AUTONOMOUS MCP AGENT AUDIT FINISHED")
            print("=" * 75)
            return final_response


def main():
    invoice_target = sys.argv[1] if len(sys.argv) > 1 else "INV-2026-003"
    asyncio.run(run_mcp_agent_audit(invoice_target))


if __name__ == "__main__":
    main()
