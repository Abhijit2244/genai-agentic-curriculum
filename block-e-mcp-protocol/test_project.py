"""
test_project.py — Automated Unit Test Suite for Block E: Model Context Protocol (MCP)
Tests:
1. Server Tool Logic (get_invoice, find_duplicates)
2. Server Resource Logic (get_invoice_policy)
3. Server Prompt Logic (audit_invoice_prompt)
4. Full MCP Client JSON-RPC 2.0 handshake and capability discovery over stdio
5. Tool execution and resource reading via ClientSession
"""

import sys
import unittest
import asyncio
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from mcp_server import get_invoice, find_duplicates, get_invoice_policy, audit_invoice_prompt, server
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

SERVER_SCRIPT = BASE_DIR / "mcp_server.py"


class TestBlockEMCPProtocol(unittest.TestCase):

    def test_01_server_tools_direct(self):
        """Test direct execution of MCP tools."""
        # Test get_invoice found
        res = get_invoice("INV-2026-001")
        self.assertEqual(res["status"], "found")
        self.assertEqual(res["invoice"]["vendor"], "CloudMatrix Systems")
        self.assertEqual(res["invoice"]["amount"], 24500.00)

        # Test get_invoice not found
        res_missing = get_invoice("INV-NONEXISTENT")
        self.assertEqual(res_missing["status"], "not_found")
        self.assertIn("error", res_missing)

        # Test find_duplicates
        dup_res = find_duplicates("invoices.json")
        self.assertEqual(dup_res["status"], "success")
        self.assertGreater(dup_res["total_anomalies_detected"], 0)
        self.assertGreater(len(dup_res["duplicate_groups"]), 0)
        self.assertGreater(len(dup_res["structuring_candidates"]), 0)
        self.assertGreater(len(dup_res["missing_po_violations"]), 0)

    def test_02_server_resources_direct(self):
        """Test reading the compliance policy resource."""
        policy_text = get_invoice_policy()
        self.assertIn("Corporate Accounts Payable & Invoice Verification Policy", policy_text)
        self.assertIn("AP-AUTH-01", policy_text)
        self.assertIn("AP-DUP-03", policy_text)

    def test_03_server_prompt_direct(self):
        """Test prompt template rendering."""
        rendered = audit_invoice_prompt("INV-2026-005")
        self.assertIn("INV-2026-005", rendered)
        self.assertIn("get_invoice", rendered)
        self.assertIn("invoice://policy/compliance-rules", rendered)

    def test_04_mcp_client_stdio_handshake(self):
        """Test running real JSON-RPC 2.0 handshake and capability discovery via stdio."""
        async def run_handshake():
            server_params = StdioServerParameters(
                command=sys.executable,
                args=[str(SERVER_SCRIPT)],
                env=None
            )
            async with stdio_client(server_params) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    init_res = await session.initialize()
                    self.assertEqual(init_res.server_info.name, "InvoiceAuditServer")

                    # Check tool discovery
                    tools_res = await session.list_tools()
                    tool_names = [t.name for t in tools_res.tools]
                    self.assertIn("get_invoice", tool_names)
                    self.assertIn("find_duplicates", tool_names)

                    # Check resource discovery
                    resources_res = await session.list_resources()
                    resource_uris = [str(r.uri) for r in resources_res.resources]
                    self.assertIn("invoice://policy/compliance-rules", resource_uris)

                    # Check prompt discovery
                    prompts_res = await session.list_prompts()
                    prompt_names = [p.name for p in prompts_res.prompts]
                    self.assertIn("audit_invoice", prompt_names)

        asyncio.run(run_handshake())

    def test_05_mcp_client_call_tool_and_read_resource(self):
        """Test executing tool calls and resource reading over ClientSession."""
        async def run_operations():
            server_params = StdioServerParameters(
                command=sys.executable,
                args=[str(SERVER_SCRIPT)],
                env=None
            )
            async with stdio_client(server_params) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()

                    # Execute get_invoice tool
                    tool_call_res = await session.call_tool("get_invoice", {"id": "INV-2026-003"})
                    self.assertTrue(len(tool_call_res.content) > 0)
                    self.assertIn("CyberShield Solutions", tool_call_res.content[0].text)

                    # Read resource
                    resource_read = await session.read_resource("invoice://policy/compliance-rules")
                    self.assertTrue(len(resource_read.contents) > 0)
                    content_text = resource_read.contents[0].text if hasattr(resource_read.contents[0], "text") else str(resource_read.contents[0])
                    self.assertIn("AP-POL-2026", content_text)

        asyncio.run(run_operations())


if __name__ == "__main__":
    unittest.main()
