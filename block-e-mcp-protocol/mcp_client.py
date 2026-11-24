"""
mcp_client.py — Python Model Context Protocol (MCP) Client
Connects to mcp_server.py via stdio transport using JSON-RPC 2.0.
Demonstrates:
1. Lifecycle Handshake (initialize & capability negotiation)
2. Discovery of Tools, Resources, and Prompts
3. Tool Execution (get_invoice, find_duplicates)
4. Resource Reading (invoice://policy/compliance-rules)
5. Prompt Template Rendering (audit_invoice)
"""

import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List

from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

BASE_DIR = Path(__file__).resolve().parent
SERVER_SCRIPT = BASE_DIR / "mcp_server.py"


async def run_mcp_client_demo() -> Dict[str, Any]:
    """
    Connects to the MCP Server over stdio, discovers capabilities,
    and executes tools and resource queries.
    """
    print("\n" + "=" * 75)
    print("      MODEL CONTEXT PROTOCOL (MCP) CLIENT DEMONSTRATION")
    print("=" * 75)
    print(f"Connecting to MCP Server: {SERVER_SCRIPT}")
    print("Transport: stdio (JSON-RPC 2.0 over standard I/O pipes)\n")

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_SCRIPT)],
        env=None
    )

    results: Dict[str, Any] = {}

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            
            # --- PHASE 1: Protocol Lifecycle Handshake ---
            print(">>> [Phase 1: Handshake] Initializing JSON-RPC 2.0 session...")
            init_res = await session.initialize()
            print(f"    Protocol Version: {init_res.protocol_version}")
            print(f"    Server Name:     {init_res.server_info.name} (v{init_res.server_info.version})")
            print(f"    Capabilities:    {init_res.capabilities}\n")

            # --- PHASE 2: Discover Server Primitives ---
            print(">>> [Phase 2: Discovery] Querying server for Tools, Resources, and Prompts...")
            
            # 1. Tools
            tools_list = await session.list_tools()
            print(f"    Discovered Tools ({len(tools_list.tools)}):")
            for t in tools_list.tools:
                print(f"      • {t.name}: {t.description[:70]}...")
            results["tools"] = [t.name for t in tools_list.tools]

            # 2. Resources
            resources_list = await session.list_resources()
            print(f"\n    Discovered Resources ({len(resources_list.resources)}):")
            for r in resources_list.resources:
                print(f"      • {r.uri} ({r.mime_type}): {r.name}")
            results["resources"] = [str(r.uri) for r in resources_list.resources]

            # 3. Prompts
            prompts_list = await session.list_prompts()
            print(f"\n    Discovered Prompts ({len(prompts_list.prompts)}):")
            for p in prompts_list.prompts:
                print(f"      • {p.name}: {p.description}")
            results["prompts"] = [p.name for p in prompts_list.prompts]

            # --- PHASE 3: Resource Reading ---
            print("\n>>> [Phase 3: Resources] Reading policy resource 'invoice://policy/compliance-rules'...")
            policy_resource = await session.read_resource("invoice://policy/compliance-rules")
            policy_text = policy_resource.contents[0].text if hasattr(policy_resource.contents[0], "text") else str(policy_resource.contents[0])
            print(f"    Resource Content Received ({len(policy_text)} chars):")
            print(f"    Preview:\n    {policy_text[:220]}...\n")
            results["policy_preview"] = policy_text[:150]

            # --- PHASE 4: Prompt Rendering ---
            print(">>> [Phase 4: Prompts] Rendering prompt template 'audit_invoice' for 'INV-2026-003'...")
            prompt_res = await session.get_prompt("audit_invoice", {"invoice_id": "INV-2026-003"})
            rendered_msg = prompt_res.messages[0].content.text
            print(f"    Rendered Prompt Output:\n    {rendered_msg}\n")
            results["rendered_prompt"] = rendered_msg

            # --- PHASE 5: Tool Execution ---
            print(">>> [Phase 5: Tools] Executing Tool: get_invoice(id='INV-2026-003')...")
            inv_res = await session.call_tool("get_invoice", {"id": "INV-2026-003"})
            inv_text = inv_res.content[0].text if inv_res.content else ""
            print(f"    Tool Result:\n    {inv_text}\n")
            results["get_invoice_result"] = inv_text

            print(">>> [Phase 5: Tools] Executing Tool: find_duplicates(file='invoices.json')...")
            dup_res = await session.call_tool("find_duplicates", {"file": "invoices.json"})
            dup_text = dup_res.content[0].text if dup_res.content else ""
            dup_data = json.loads(dup_text)
            print(f"    Duplicate Groups Found:    {len(dup_data.get('duplicate_groups', []))}")
            print(f"    Structuring Schemes Found: {len(dup_data.get('structuring_candidates', []))}")
            print(f"    Missing PO Violations:     {len(dup_data.get('missing_po_violations', []))}")
            results["find_duplicates_summary"] = {
                "duplicates": len(dup_data.get("duplicate_groups", [])),
                "structuring": len(dup_data.get("structuring_candidates", [])),
                "missing_pos": len(dup_data.get("missing_po_violations", []))
            }

            print("\n" + "=" * 75)
            print("  MCP CLIENT DEMONSTRATION COMPLETED SUCCESSFULLY")
            print("=" * 75)

    return results


def main():
    asyncio.run(run_mcp_client_demo())


if __name__ == "__main__":
    main()
