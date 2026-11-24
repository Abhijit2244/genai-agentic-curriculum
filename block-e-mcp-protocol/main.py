"""
main.py — Master Runner for Block E: Model Context Protocol (MCP)
Executes:
1. MCP Protocol Lifecycle & Discovery via mcp_client.py (stdio JSON-RPC 2.0)
2. Autonomous Agent Investigation via agent_mcp_integration.py
3. Instructions for MCP Inspector and Host Configurations (Claude Desktop, Cursor)
"""

import sys
import asyncio
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from mcp_client import run_mcp_client_demo
from agent_mcp_integration import run_mcp_agent_audit


def print_inspector_instructions():
    print("\n" + "=" * 75)
    print("      HOW TO TEST THIS MCP SERVER IN MCP INSPECTOR (GUI)")
    print("=" * 75)
    print("Anthropic provides the visual MCP Inspector tool for interactive testing.")
    print("Run the following command in your terminal from this folder:\n")
    print(f"  cd {BASE_DIR}")
    print("  npx @modelcontextprotocol/inspector python mcp_server.py\n")
    print("This starts a local web server (http://localhost:5173). You can interactively:")
    print("  1. Click 'List Tools' -> execute get_invoice and find_duplicates")
    print("  2. Click 'List Resources' -> read invoice://policy/compliance-rules")
    print("  3. Click 'List Prompts' -> view and render audit_invoice template")
    print("=" * 75 + "\n")


def print_claude_desktop_config():
    print("=" * 75)
    print("  HOW TO CONNECT TO CLAUDE DESKTOP / CURSOR AS AN MCP CLIENT")
    print("=" * 75)
    print("Add this configuration to your Claude Desktop config file:")
    print("Path: %APPDATA%\\Claude\\claude_desktop_config.json\n")
    config_json = f"""{{
  "mcpServers": {{
    "invoice-auditor": {{
      "command": "{sys.executable.replace('\\', '\\\\')}",
      "args": ["{str(BASE_DIR / 'mcp_server.py').replace('\\', '\\\\')}"]
    }}
  }}
}}"""
    print(config_json)
    print("=" * 75 + "\n")


async def run_all_mcp_demos():
    print("=" * 80)
    print("       BLOCK E: MODEL CONTEXT PROTOCOL (MCP) — MASTER DEMONSTRATION")
    print("=" * 80)

    # Demo 1: MCP Client
    print("\n>>> [DEMO 1]: MCP Client Lifecycle Handshake & Primitives Discovery")
    await run_mcp_client_demo()

    # Demo 2: Autonomous Agent + MCP Integration
    print("\n>>> [DEMO 2]: Autonomous Gemini Agent Running Over MCP Protocol")
    await run_mcp_agent_audit("INV-2026-003")

    # Demo 3: MCP Inspector & Host Guides
    print_inspector_instructions()
    print_claude_desktop_config()

    print("=" * 80)
    print("  ALL BLOCK E MCP DEMONSTRATIONS COMPLETED SUCCESSFULLY!")
    print("=" * 80)


def main():
    asyncio.run(run_all_mcp_demos())


if __name__ == "__main__":
    main()
