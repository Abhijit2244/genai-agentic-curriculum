# Block D: Agentic AI & Audit Governance

> **Curriculum Module**: Block D: Agentic AI (3.5 Hours Intensive)  
> **Topic Scope**: Chatbot vs Workflow vs Agent, Autonomy Levels, ReAct Agent Loops, State Management, Human-in-the-Loop (HITL), Guardrails, Agent Frameworks, A2A Protocol, and Audit Governance.  
> **Directory**: `block-d-agentic-ai/`

---

## 1. Project Overview & Practice Assignment

This project implements a complete, enterprise-grade **Autonomous Forensic Audit Agent** built with **LangGraph** and the **Gemini API** (`gemini-3.5-flash-lite` and `models/gemini-embedding-001`).

### The Practice Implementation:
1. **`query_ledger_csv`**: Uses **pandas** to filter, slice, and aggregate transactions from `general_ledger_2026.csv` (detects structuring, duplicate payments, unauthorized weekend wires, and missing purchase orders).
2. **`search_policy`**: Uses an in-memory **RAG** vector store over `internal_financial_controls_policy.md` (SOX 404 & SSAE-18 internal controls).
3. **`flag_anomaly`**: Formats and logs official Audit Exception Records in audit workpapers.
4. **Human-in-the-Loop (HITL)**: Uses LangGraph's `interrupt_before=["tools"]` to pause execution before committing findings to workpapers, allowing a human auditor to review evidence, exercise professional skepticism, modify findings, or approve.

---

## 2. Project Directory Structure

```
block-d-agentic-ai/
├── .env                                # Gemini API Keys & Model configuration
├── config.py                           # Gemini LLM & Embedding singletons + text extractor
├── data/
│   ├── generate_ledger_data.py         # Script generating realistic 25-row General Ledger CSV
│   ├── generate_policy_data.py         # Script generating SOX 404 internal controls standard
│   ├── general_ledger_2026.csv         # Ledger dataset with legitimate & anomalous transactions
│   └── internal_financial_controls_policy.md # Compliance policies (POL-IC-01 through POL-IC-05)
├── tools/
│   ├── __init__.py                     # Clean package exports
│   ├── ledger_tool.py                  # query_ledger_csv (pandas querying & table formatting)
│   ├── policy_rag_tool.py              # search_policy (in-memory RAG over SOX controls)
│   └── audit_tools.py                  # flag_anomaly & workpaper exception logging
├── 01_agent_architectures.py           # Chatbot (L1) vs Workflow (L2) vs ReAct Agent (L3) & Autonomy Levels (0-5)
├── 02_langgraph_audit_agent.py         # Autonomous LangGraph ReAct agent binding all 3 tools
├── 03_human_in_the_loop_audit.py       # HITL approval gate: inspection, state mutation & resumption
├── 04_multi_agent_audit_team.py        # Supervisor pattern coordinating DataAuditor & PolicyAuditor
├── main.py                             # Interactive master runner executing all demos
├── test_project.py                     # Automated unit test suite (5/5 tests)
├── README.md                           # This architecture and execution guide
└── LEARNING_GUIDE_AND_INTERVIEW_QA.md  # Deep technical guide + 4-tier graded Q&A (Basic to Staff)
```

---

## 3. How to Run

### Step 1: Run the Automated Unit Tests
```bash
cd block-d-agentic-ai
python test_project.py
```

### Step 2: Run All Demonstrations in Sequence
```bash
python main.py
```

### Step 3: Run Individual Modules
```bash
# 1. Compare Chatbot vs Workflow vs Agent (Autonomy Levels 0-5)
python 01_agent_architectures.py

# 2. Autonomous LangGraph Audit Agent (3 Tools: pandas ledger, RAG policy, flag anomaly)
python 02_langgraph_audit_agent.py

# 3. Human-in-the-Loop Audit Approval Gate (Breakpoints, State Mutation, Sign-Off)
python 03_human_in_the_loop_audit.py

# 4. Multi-Agent Team (Supervisor, Data Auditor, Policy Auditor, Lead Partner)
python 04_multi_agent_audit_team.py
```

---

## 4. The Audit Lens: Why Agents Must Assist, Not Replace Judgement

In financial auditing (SOX 404, PCAOB, AICPA SSAE-18), AI agents are strictly **investigative accelerators**:
1. **Traceability**: Every assertion must link back to exact ledger rows (`transaction_id`) and control citations (`POL-IC-02`).
2. **Explainability**: Black-box generative summaries are inadmissible without audit trails.
3. **Reproducibility**: Setting deterministic temperature ($T=0.0$) and preserving state checkpoints ensures independent audit re-performance.
4. **Professional Skepticism**: The agent flags candidate anomalies, but human auditors evaluate intent, business context, and materiality.
5. **Reviewer Sign-off**: Official workpaper exceptions require human CPA sign-off before submission to the Audit Committee.
