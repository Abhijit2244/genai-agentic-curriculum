# Capstone Project: Mini Audit Agent (Enterprise SOX 404 Forensic Accounting)

An end-to-end autonomous forensic accounting and internal controls audit agent synthesizing Computer Vision OCR, Deterministic Ledger Analytics, Semantic Policy RAG, Model Context Protocol (MCP), LangGraph State Machine Orchestration, Real-Time SSE Streaming, and Human-in-the-Loop (HITL) Auditor Certification.

---

## 1. Project Overview & The 8 Core Specifications

This project connects all five curriculum blocks into a unified enterprise full-stack application:

| Spec # | Specification Requirement | Implementation Mechanism | Status |
|:---:|:---|:---|:---:|
| **1** | **React UI** | React 18 SPA with drag-and-drop dual-file uploader, one-click pre-loaded test fixtures, live 6-stage SSE progress stepper, Human-in-the-Loop review card, and certified report memorandum viewer. | ✅ Complete |
| **2** | **FastAPI Backend** | High-performance asynchronous FastAPI server receiving multipart uploads, managing background tasks, and exposing REST + SSE endpoints. | ✅ Complete |
| **3** | **OpenCV + OCR** | Computer Vision preprocessing pipeline (Grayscale $\to$ CLAHE contrast equalization $\to$ Otsu dynamic binarization) followed by Gemini Multimodal structured field extraction. | ✅ Complete |
| **4** | **Pandas Ledger Analytics** | Deterministic detection of duplicate invoice submissions (`AP-DUP-03`), threshold circumvention / structuring (`AP-STRUCT-02`), and missing PO violations (`AP-PO-04`). | ✅ Complete |
| **5** | **Policy RAG** | Vector semantic retrieval over internal accounting control policies using `gemini-embedding-001` dense embeddings and cosine similarity. | ✅ Complete |
| **6** | **LangGraph Orchestrator** | Cyclic state machine (`StateGraph`) with thread-isolated `MemorySaver` persistence and explicit state transitions. | ✅ Complete |
| **7** | **MCP Server Integration** | FastMCP server (`mcp_service/audit_mcp_server.py`) exposing tools (`ocr_invoice`, `check_ledger_anomalies`, `search_compliance_policy`, `submit_audit_findings`) and resources (`audit://policies/sox404`). | ✅ Complete |
| **8** | **SSE Streaming & HITL** | Real-time progress streamed over HTTP chunked SSE (`/api/audit/events/{job_id}`); execution halts at breakpoint (`interrupt_before=["human_approval"]`) until lead auditor sign-off. | ✅ Complete |

---

## 2. Architecture & Data Flow

```
[Auditor Browser (React 18 SPA)]
            |
            | 1. Upload Invoice PNG + Ledger CSV (POST /api/audit/start)
            v
[FastAPI Asynchronous Gateway]
            |
            | 2. Spawn Thread-Isolated LangGraph Workflow
            v
[LangGraph StateGraph Engine] (Checkpointed via MemorySaver)
   |
   +---> [Node 1: OCR] ---------> (MCP Tool: ocr_invoice)
   |                                 └── OpenCV (CLAHE+Otsu) + Gemini Multimodal
   |
   +---> [Node 2: Ledger Scan] ---> (MCP Tool: check_ledger_anomalies)
   |                                 └── Pandas Vectorized Duplicate/Structuring Detection
   |
   +---> [Node 3: Policy RAG] ----> (MCP Tool: search_compliance_policy)
   |                                 └── Gemini Dense Embeddings + Cosine Similarity
   |
   +---> [Node 4: LLM Synthesis] -> Gemini 3.5 Flash-Lite Forensic Cross-Examination
   |
   +---> [Node 5: BREAKPOINT] ----> Halts execution (interrupt_before=["human_approval"])
   |                                 └── Streams AWAITING_HUMAN_APPROVAL via SSE
   |
   +<--- [Human Sign-off] <------- Auditor reviews findings in React UI, enters notes, approves
   |                                 └── POST /api/audit/approve/{job_id}
   |
   +---> [Node 6: Final Report] -> (MCP Tool: submit_audit_findings)
                                     └── Generates Official SOX 404 Exception Memorandum
```

---

## 3. Directory Structure

```
capstone-mini-audit-agent/
├── .env                                  # API keys & configuration
├── config.py                             # Centralized settings & Gemini LLM/embeddings factories
├── main.py                               # Application entrypoint (Server launcher & CLI demo)
├── test_project.py                       # Comprehensive 6-stage unit & integration test suite
├── README.md                             # Project setup & operational guide
├── LEARNING_GUIDE_AND_INTERVIEW_QA.md    # Architecture deep-dive & 40-question 4-tier interview guide
├── core/
│   ├── ocr_engine.py                     # OpenCV CLAHE/Otsu binarization + Gemini Multimodal OCR
│   ├── ledger_analyzer.py                # Pandas forensic anomaly & structuring detection
│   └── policy_rag.py                     # In-memory vector database & semantic policy retriever
├── mcp_service/
│   └── audit_mcp_server.py               # FastMCP Server exposing tools and compliance resources
├── agent/
│   └── audit_graph.py                    # LangGraph StateGraph with HITL interrupt breakpoint
├── backend/
│   └── app.py                            # FastAPI server, SSE stream generator, and REST endpoints
├── frontend/
│   └── index.html                        # React 18 + Tailwind CSS Auditor Workspace SPA
└── sample_data/
    ├── compliance_policy.md              # Governing SOX 404 Accounts Payable policies
    ├── ledger.csv                        # Historical enterprise general ledger dataset
    ├── invoice_cybershield_dup.png       # Test Scenario A: Duplicate Invoice (AP-DUP-03)
    ├── invoice_apex_structuring.png      # Test Scenario B: Structuring / Threshold Evasion (AP-STRUCT-02)
    └── generate_test_invoices.py         # Pillow generator for realistic invoice graphic test fixtures
```

---

## 4. Quickstart Guide

### Prerequisites
- Python 3.10+
- Valid Google Gemini API Key (`GEMINI_API_KEY` or `GOOGLE_API_KEY`)

### 1. Configure Environment
Ensure `.env` exists in the capstone directory with your Gemini API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
HOST=127.0.0.1
PORT=8000
```

### 2. Run the Web Application
Start the FastAPI server hosting the React UI:
```bash
python main.py
```
Open your browser and navigate to:
👉 **`http://127.0.0.1:8000/`**

### 3. Run Automated CLI Demonstration
To verify the entire LangGraph audit loop, breakpoint, simulated human sign-off, and report generation in your terminal without a browser:
```bash
python main.py --demo
```

### 4. Run the Unit Test Suite
Execute the 6-part test suite validating CV preprocessing, OCR, Pandas anomaly detection, RAG retrieval, MCP tools, and LangGraph resumption:
```bash
python -m unittest test_project.py
```

---

## 5. Pre-Loaded Test Scenarios

The web interface includes two one-click pre-loaded test buttons:

### Scenario A: CyberShield Solutions (`invoice_cybershield_dup.png`)
- **Extracted Invoice:** \$14,250.00 under PO-2026-112.
- **Historical Ledger:** Shows an identical \$14,250.00 disbursement already executed for CyberShield within the 72-hour window.
- **Triggered Control:** `AP-DUP-03` (Automated Duplicate Invoice Quarantine).
- **Audit Outcome:** Payment freeze recommended; requires lead auditor sign-off.

### Scenario B: Apex Cloud Holdings (`invoice_apex_structuring.png`)
- **Extracted Invoice:** \$49,990.00 under PO-2026-130.
- **Historical Ledger:** Shows a previous invoice of \$49,950.00 executed days earlier.
- **Triggered Control:** `AP-STRUCT-02` (Threshold Circumvention / Smurfing). Cumulative spend reaches \$99,940.00, intentionally split beneath the \$50,000 CFO dual-signature threshold.
- **Audit Outcome:** High-severity control exception flagged.

---

## 6. API Reference

- `GET /` — Serves the interactive React 18 Auditor SPA.
- `GET /docs` — Interactive OpenAPI / Swagger documentation.
- `POST /api/audit/start` — Ingests `invoice_file` and optional `ledger_file` as multipart form data. Returns `{"job_id": "...", "status": "started"}`.
- `GET /api/audit/events/{job_id}` — SSE streaming endpoint (`text/event-stream`). Emits live status events:
  - `OCR_STARTED` $\to$ `OCR_DONE`
  - `LEDGER_STARTED` $\to$ `LEDGER_DONE`
  - `RAG_STARTED` $\to$ `RAG_DONE`
  - `REASONING_STARTED` $\to$ `AWAITING_HUMAN_APPROVAL`
  - `REPORT_READY`
- `POST /api/audit/approve/{job_id}` — Submits human auditor sign-off:
  ```json
  {
    "approved": true,
    "notes": "Verified duplicate submission with Accounts Payable manager."
  }
  ```
- `GET /api/audit/report/{job_id}` — Retrieves the final certified Markdown report and metadata.
