# Master GenAI & Agentic AI Curriculum

> **Repository**: `genai-agentic-curriculum`  
> **Ecosystem**: Python 3.15, Google Gemini API (`gemini-3.5-flash-lite`, `gemini-embedding-001`), LangChain, LangGraph, Pandas, OpenCV, FastAPI, React 18, Model Context Protocol (FastMCP).

---

## 1. Directory Structure

```
genai-agentic-curriculum/
├── README.md                          # Master curriculum index (this file)
│
├── docs/                              # Dual-Track Agentic AI Learning Roadmaps
│   ├── README.md                      # Learning portal guide & comparative roadmap matrix
│   ├── 01-agentic-ai-roadmap-for-web-developers.md (12-Week Track for React/Angular/Node/.NET Devs)
│   └── 02-agentic-ai-roadmap-for-college-freshers.md (6-Month Track from Zero to Agentic Engineer)
│
├── block-a-llm-fundamentals/          # Block A: LLM Fundamentals (1.5 hrs)
│   ├── LEARNING_GUIDE_AND_INTERVIEW_QA.md (1,072 lines | 40 Graded Q&As)
│   ├── README.md
│   ├── config.py, main.py, test_project.py
│   └── 01_call_llm.py, 02_structured_json.py, 03_tool_calling.py, 04_embeddings_demo.py
│
├── block-b-rag-mastery/               # Block B: RAG Mastery (3.0 hrs)
│   ├── LEARNING_GUIDE_AND_INTERVIEW_QA.md (1,085 lines | 40 Graded Q&As)
│   ├── README.md
│   ├── config.py, vector_indexer.py, main.py, test_project.py
│   ├── data/ (generate_audit_pdf.py, iso27001_soc2_audit_standard.pdf)
│   └── 01_load_and_chunk.py, 02_vector_store_indexing.py, 03_rag_pipeline_with_citations.py, 04_advanced_retrieval_techniques.py
│
├── block-c-langchain-langgraph/       # Block C: LangChain, LangGraph & MCP (3.5 hrs)
│   ├── LEARNING_GUIDE_AND_INTERVIEW_QA.md (1,265 lines | 40 Graded Q&As)
│   ├── README.md
│   ├── config.py, main.py, test_project.py
│   └── 01_langchain_lcel_chains.py, 02_langgraph_react_agent.py, 03_memory_and_human_in_the_loop.py, 04_multi_agent_supervisor.py
│
├── block-d-agentic-ai/                # Block D: Agentic AI & Audit Governance (3.5 hrs)
│   ├── LEARNING_GUIDE_AND_INTERVIEW_QA.md (1,179 lines | 40 Graded Q&As)
│   ├── README.md
│   ├── config.py, main.py, test_project.py
│   ├── data/ (general_ledger_2026.csv, internal_financial_controls_policy.md)
│   ├── tools/ (ledger_tool.py, policy_rag_tool.py, audit_tools.py)
│   └── 01_agent_architectures.py, 02_langgraph_audit_agent.py, 03_human_in_the_loop_audit.py, 04_multi_agent_audit_team.py
│
├── block-e-mcp-protocol/              # Block E: Model Context Protocol (MCP) (2.0 hrs)
│   ├── LEARNING_GUIDE_AND_INTERVIEW_QA.md (1,236 lines | 40 Graded Q&As)
│   ├── README.md
│   ├── config.py, main.py, test_project.py
│   ├── data/ (invoices.json, invoice_policy.md, generate_sample_data.py)
│   ├── mcp_server.py                  # MCPServer exposing get_invoice, find_duplicates, policy resource, audit prompt
│   ├── mcp_client.py                  # Python MCP client connecting over stdio JSON-RPC 2.0
│   └── agent_mcp_integration.py       # Autonomous Gemini ReAct Agent integrated with MCP Server
│
└── capstone-mini-audit-agent/         # Capstone: Full-Stack Mini Audit Agent (4.0 hrs)
    ├── LEARNING_GUIDE_AND_INTERVIEW_QA.md (535 lines | 40 Graded Q&As)
    ├── README.md
    ├── config.py, main.py, test_project.py
    ├── core/ (ocr_engine.py, ledger_analyzer.py, policy_rag.py)
    ├── mcp_service/ (audit_mcp_server.py)
    ├── agent/ (audit_graph.py)
    ├── backend/ (app.py)
    ├── frontend/ (index.html)
    └── sample_data/ (compliance_policy.md, ledger.csv, sample invoice graphics)
```

---

## 2. Complete Curriculum Breakdown

| Module | Core Topics | Key Practice Project | Graded Q&As | Direct Link |
| :--- | :--- | :--- | :---: | :--- |
| **Block A: LLM Fundamentals** | Tokens, Context Windows, Softmax Temp, Grammar JSON, Embeddings | API calls, Pydantic schemas, Tool execution | **40 Q&As** | [Block A Guide](./block-a-llm-fundamentals/LEARNING_GUIDE_AND_INTERVIEW_QA.md) |
| **Block B: RAG Mastery** | PDF Parsing, Recursive Chunking, HNSW, MMR, Hybrid Search | RAG over 4-page ISO/SOC-2 PDF with exact citations | **40 Q&As** | [Block B Guide](./block-b-rag-mastery/LEARNING_GUIDE_AND_INTERVIEW_QA.md) |
| **Block C: LangChain & LangGraph** | LCEL, Cyclic Graphs, `MemorySaver`, HITL Breakpoints, Swarms | ReAct state machine, HITL approval, Multi-agent supervisor | **40 Q&As** | [Block C Guide](./block-c-langchain-langgraph/LEARNING_GUIDE_AND_INTERVIEW_QA.md) |
| **Block D: Agentic AI & Audit** | 6 Autonomy Levels, State Checkpoints, Guardrails, A2A Protocol | 3-tool Forensic Audit Agent with pandas & RAG + HITL Sign-off | **40 Q&As** | [Block D Guide](./block-d-agentic-ai/LEARNING_GUIDE_AND_INTERVIEW_QA.md) |
| **Block E: Model Context Protocol** | M x N Problem, Tools/Resources/Prompts, JSON-RPC 2.0, stdio/HTTP | Invoice MCP Server + MCP Client + Autonomous Agent Integration | **40 Q&As** | [Block E Guide](./block-e-mcp-protocol/LEARNING_GUIDE_AND_INTERVIEW_QA.md) |
| **Capstone: Mini Audit Agent** | Full-Stack Forensic Agent: React UI, FastAPI, OpenCV OCR, Pandas, RAG, LangGraph, MCP, SSE, HITL | End-to-end web & CLI audit system with live SSE and HITL approval | **40 Q&As** | [Capstone Guide](./capstone-mini-audit-agent/LEARNING_GUIDE_AND_INTERVIEW_QA.md) |

**Total Guide Size**: Over **6,370 lines** of technical guides, system design architectures, and **240 graded interview questions** spanning Junior, Mid-Level, Senior, and Staff/Principal Architect levels.

---

## 3. How to Run Each Block & The Capstone

```bash
# Block A: LLM Fundamentals
cd block-a-llm-fundamentals
python main.py
python test_project.py

# Block B: RAG Mastery
cd block-b-rag-mastery
python main.py
python -m unittest test_project.py

# Block C: LangChain & LangGraph
cd block-c-langchain-langgraph
python main.py
python -m unittest test_project.py

# Block D: Agentic AI & Audit
cd block-d-agentic-ai
python main.py
python -m unittest test_project.py

# Block E: Model Context Protocol
cd block-e-mcp-protocol
python main.py
python -m unittest test_project.py

# Capstone: Mini Audit Agent
cd capstone-mini-audit-agent
python main.py             # Launches Web Application at http://127.0.0.1:8000/
python main.py --demo      # Runs automated CLI forensic audit demonstration
python -m unittest test_project.py
```
