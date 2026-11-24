# Block E: Model Context Protocol (MCP)

> **Curriculum Module**: Block E: MCP — Model Context Protocol (2.0 Hours Intensive)  
> **Topic Scope**: $M \times N$ Integration Problem, Host-Client-Server Architecture, Tools/Resources/Prompts Primitives, JSON-RPC 2.0 Lifecycle, stdio vs. Streamable HTTP, OAuth 2.1, Security (Tool Poisoning, Confused Deputy), MCP vs. Function Calling vs. REST vs. A2A.  
> **Directory**: `block-e-mcp-protocol/`

---

## 1. Project Overview & Practice Assignment

This project implements a complete, production-grade **Model Context Protocol (MCP) Server and Client** in Python 3.15 conforming to the modern **MCP 2.x specification (`mcp` SDK)**.

### The Practice Implementation:
1. **MCP Server (`mcp_server.py`)**:
   - **Tool 1: `get_invoice(id: str)`**: Fetches structured invoice metadata by ID.
   - **Tool 2: `find_duplicates(file: str)`**: Scans for duplicate disbursements (`AP-DUP-03`), invoice structuring near $50k (`AP-STRUCT-02`), and missing POs (`AP-PO-04`).
   - **Resource: `invoice://policy/compliance-rules`**: Exposes the corporate accounts payable compliance standard (`invoice_policy.md`) as a readable resource.
   - **Prompt: `audit_invoice(invoice_id: str)`**: Exposes a standardized audit prompt template.
2. **MCP Client (`mcp_client.py`)**:
   - Spawns the MCP server as a subprocess over `stdio` transport.
   - Negotiates JSON-RPC 2.0 protocol version and discovers capabilities.
   - Executes tools, reads resources, and renders prompt templates.
3. **Agent Integration (`agent_mcp_integration.py`)**:
   - An autonomous **Gemini ReAct Agent** that connects to the MCP server.
   - Ingests the policy resource as ground-truth context.
   - Binds the MCP tools to perform an end-to-end forensic audit and emits an executive Audit Exception Memorandum.

---

## 2. Directory Structure

```
block-e-mcp-protocol/
├── .env                                # Gemini API key & settings
├── config.py                           # Gemini LLM initialization + common utilities
├── data/
│   ├── invoices.json                   # Mock invoice database (various vendors, duplicates, structuring)
│   ├── invoice_policy.md               # Compliance & invoice review policy (exposed as MCP resource)
│   └── generate_sample_data.py         # Script to generate invoices and policy doc
├── mcp_server.py                       # MCP Server exposing tools, resources, and prompts over stdio/HTTP
├── mcp_client.py                       # Python MCP client connecting via stdio transport (JSON-RPC 2.0)
├── agent_mcp_integration.py            # LangChain/Gemini ReAct Agent integrated with MCP Server
├── test_project.py                     # Automated unit test suite (5/5 tests passing)
├── main.py                             # Master runner demonstrating server, client, and agent
├── README.md                           # This architecture and execution guide
└── LEARNING_GUIDE_AND_INTERVIEW_QA.md  # Deep technical guide + 4-tier graded Q&A (Basic to Staff)
```

---

## 3. How to Run

### Step 1: Run the Automated Unit Tests
```bash
cd block-e-mcp-protocol
python -m unittest test_project.py
```

### Step 2: Run Master Demonstration
```bash
python main.py
```

### Step 3: Run the MCP Client Demo
```bash
python mcp_client.py
```

### Step 4: Run the Autonomous Agent Over MCP
```bash
python agent_mcp_integration.py INV-2026-003
```

### Step 5: Test in MCP Inspector (Visual Web UI)
Anthropic's official MCP Inspector lets you test your server interactively:
```bash
npx @modelcontextprotocol/inspector python mcp_server.py
```
Open your browser at `http://localhost:5173` to inspect tools, resources, and prompts in a rich GUI!

---

## 4. Connecting to Claude Desktop / Cursor

To connect this server to **Claude Desktop**, add this to `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "invoice-auditor": {
      "command": "python",
      "args": [
        "C:\\Users\\COM\\Desktop\\sample\\genai-agentic-curriculum\\block-e-mcp-protocol\\mcp_server.py"
      ]
    }
  }
}
```
Restart Claude Desktop, and you will see the hammer icon 🔨 with `get_invoice`, `find_duplicates`, and the book icon 📖 for `invoice://policy/compliance-rules`!
