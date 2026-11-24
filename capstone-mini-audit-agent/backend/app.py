"""
app.py — FastAPI Application for Capstone: Mini Audit Agent
Exposes:
1. POST /api/audit/upload -> Ingests invoice image + ledger CSV, starts agent job
2. GET /api/audit/events/{job_id} -> Server-Sent Events (SSE) streaming real-time agent progress
3. POST /api/audit/approve/{job_id} -> Human-in-the-Loop approval endpoint resuming LangGraph
4. GET /api/audit/report/{job_id} -> Retrieves final signed audit report
5. GET /api/audit/samples -> Returns pre-packaged sample files for one-click testing
6. Serves the interactive React Single-Page Application
"""

import sys
import uuid
import json
import asyncio
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langgraph.checkpoint.memory import MemorySaver

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import UPLOADS_DIR, SAMPLE_DATA_DIR, HOST, PORT
from agent.audit_graph import build_audit_workflow, AuditState

app = FastAPI(
    title="Mini Audit Agent API",
    description="Enterprise Forensic Audit Agent with OpenCV, OCR, Pandas, RAG, LangGraph, and Human Approval",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global in-memory storage for active job queues and checkpointers
JOB_EVENT_QUEUES: Dict[str, asyncio.Queue] = {}
JOB_CHECKPOINTERS: Dict[str, MemorySaver] = {}
JOB_WORKFLOWS: Dict[str, Any] = {}
JOB_FINAL_STATES: Dict[str, Dict[str, Any]] = {}


class ApprovalRequest(BaseModel):
    approved: bool = True
    notes: Optional[str] = "Approved by Senior Forensic CPA Auditor."


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "Mini Audit Agent"}


@app.get("/api/audit/samples")
def get_sample_files():
    """Lists preloaded sample invoices and ledger for one-click testing."""
    return {
        "ledger_csv": "sample_data/ledger.csv",
        "samples": [
            {
                "id": "sample_cybershield",
                "title": "Duplicate Invoice (CyberShield $14,250)",
                "image_path": "sample_data/invoice_cybershield_dup.png",
                "expected_violation": "AP-DUP-03 (Duplicate Submission)",
                "description": "Invoice INV-2026-004 submitted for the exact same amount and date as INV-2026-003."
            },
            {
                "id": "sample_apex",
                "title": "Structuring Anomaly (Apex Cloud $49,990)",
                "image_path": "sample_data/invoice_apex_structuring.png",
                "expected_violation": "AP-STRUCT-02 (Threshold Structuring)",
                "description": "Invoice INV-2026-007 for $49,990 adjacent to $49,950 evading $50k CFO dual-signoff."
            }
        ]
    }


async def _run_agent_pipeline_background(job_id: str, image_path: str, ledger_path: str):
    """Executes the LangGraph agent pipeline and pushes progress events to the SSE queue."""
    queue = JOB_EVENT_QUEUES[job_id]
    checkpointer = JOB_CHECKPOINTERS[job_id]
    workflow = build_audit_workflow(checkpointer=checkpointer)
    JOB_WORKFLOWS[job_id] = workflow

    config = {"configurable": {"thread_id": job_id}}

    initial_state = {
        "job_id": job_id,
        "invoice_image_path": image_path,
        "ledger_csv_path": ledger_path,
        "invoice_data": None,
        "ledger_anomalies": None,
        "policy_citations": None,
        "reasoning_synthesis": None,
        "pending_approval": False,
        "human_approved": None,
        "human_notes": None,
        "final_report": None,
        "progress_step": "PIPELINE_STARTED",
        "status_message": "Initializing agent pipeline and OpenCV preprocessing..."
    }

    await queue.put({"type": "progress", "step": "STARTED", "message": "Starting forensic audit pipeline..."})

    try:
        # Run graph until the interrupt_before=["human_approval"] breakpoint is hit
        for event in workflow.stream(initial_state, config=config, stream_mode="updates"):
            for node_name, update in event.items():
                step = update.get("progress_step", node_name.upper())
                msg = update.get("status_message", f"Completed node '{node_name}'.")
                payload = {
                    "type": "progress",
                    "node": node_name,
                    "step": step,
                    "message": msg,
                    "state_update": {k: v for k, v in update.items() if k not in ["invoice_image_path", "ledger_csv_path"]}
                }
                await queue.put(payload)
                await asyncio.sleep(0.1)

        # Inspect state at breakpoint
        snapshot = workflow.get_state(config)
        JOB_FINAL_STATES[job_id] = snapshot.values

        if snapshot.next == ("human_approval",):
            anomalies = (snapshot.values.get("ledger_anomalies") or {}).get("anomalies", [])
            synthesis = snapshot.values.get("reasoning_synthesis", "")
            inv = snapshot.values.get("invoice_data", {})
            
            await queue.put({
                "type": "awaiting_approval",
                "step": "AWAITING_HUMAN_APPROVAL",
                "message": "Forensic analysis complete. Paused at Human-in-the-Loop gate for auditor sign-off.",
                "invoice": inv,
                "anomalies": anomalies,
                "synthesis": synthesis
            })
    except Exception as e:
        await queue.put({
            "type": "error",
            "step": "ERROR",
            "message": f"Pipeline failed: {str(e)}"
        })


@app.post("/api/audit/start")
async def start_audit_job(
    sample_id: Optional[str] = Form(None),
    invoice_file: Optional[UploadFile] = File(None),
    ledger_file: Optional[UploadFile] = File(None)
):
    """
    Initiates an audit investigation job.
    Accepts either uploaded files or a sample_id.
    """
    job_id = f"job-{uuid.uuid4().hex[:8]}"
    job_dir = UPLOADS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    # 1. Determine files
    if sample_id == "sample_cybershield":
        image_path = str(SAMPLE_DATA_DIR / "invoice_cybershield_dup.png")
        ledger_path = str(SAMPLE_DATA_DIR / "ledger.csv")
    elif sample_id == "sample_apex":
        image_path = str(SAMPLE_DATA_DIR / "invoice_apex_structuring.png")
        ledger_path = str(SAMPLE_DATA_DIR / "ledger.csv")
    else:
        # Save uploaded files
        if invoice_file:
            saved_inv = job_dir / invoice_file.filename
            with open(saved_inv, "wb") as f:
                shutil.copyfileobj(invoice_file.file, f)
            image_path = str(saved_inv)
        else:
            image_path = str(SAMPLE_DATA_DIR / "invoice_cybershield_dup.png")

        if ledger_file:
            saved_ledger = job_dir / ledger_file.filename
            with open(saved_ledger, "wb") as f:
                shutil.copyfileobj(ledger_file.file, f)
            ledger_path = str(saved_ledger)
        else:
            ledger_path = str(SAMPLE_DATA_DIR / "ledger.csv")

    # 2. Setup job queue and checkpointer
    JOB_EVENT_QUEUES[job_id] = asyncio.Queue()
    JOB_CHECKPOINTERS[job_id] = MemorySaver()

    # 3. Launch background execution
    asyncio.create_task(_run_agent_pipeline_background(job_id, image_path, ledger_path))

    return {
        "job_id": job_id,
        "status": "started",
        "image_path": image_path,
        "ledger_path": ledger_path
    }


@app.get("/api/audit/events/{job_id}")
async def stream_audit_events(job_id: str):
    """Server-Sent Events (SSE) streaming progress and status updates."""
    if job_id not in JOB_EVENT_QUEUES:
        raise HTTPException(status_code=404, detail="Job not found.")

    queue = JOB_EVENT_QUEUES[job_id]

    async def event_generator():
        while True:
            event = await queue.get()
            yield f"data: {json.dumps(event)}\n\n"
            if event.get("type") in ["completed", "error"]:
                break

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/api/audit/approve/{job_id}")
async def approve_audit_job(job_id: str, request: ApprovalRequest):
    """
    Human-in-the-Loop Approval Endpoint.
    Resumes the LangGraph agent after senior auditor sign-off.
    """
    if job_id not in JOB_WORKFLOWS:
        raise HTTPException(status_code=404, detail="Active workflow not found for job.")

    workflow = JOB_WORKFLOWS[job_id]
    config = {"configurable": {"thread_id": job_id}}
    queue = JOB_EVENT_QUEUES[job_id]

    # Mutate state with auditor's decision
    workflow.update_state(
        config,
        {
            "human_approved": request.approved,
            "human_notes": request.notes
        }
    )

    await queue.put({
        "type": "progress",
        "step": "HUMAN_SIGN_OFF_RECEIVED",
        "message": f"Auditor sign-off recorded ({'APPROVED' if request.approved else 'REJECTED'}). Resuming report compilation..."
    })

    # Resume graph execution (invoking with None resumes paused graph)
    try:
        for event in workflow.stream(None, config=config, stream_mode="updates"):
            for node_name, update in event.items():
                step = update.get("progress_step", node_name.upper())
                msg = update.get("status_message", f"Executed node '{node_name}'.")
                await queue.put({
                    "type": "progress",
                    "node": node_name,
                    "step": step,
                    "message": msg,
                    "state_update": update
                })

        snapshot = workflow.get_state(config)
        final_report = snapshot.values.get("final_report", "Report generated.")
        JOB_FINAL_STATES[job_id] = snapshot.values

        await queue.put({
            "type": "completed",
            "step": "REPORT_READY",
            "message": "Forensic audit certified and committed to official workpapers.",
            "report": final_report
        })

        return {
            "status": "certified",
            "job_id": job_id,
            "approved": request.approved,
            "report": final_report
        }
    except Exception as e:
        await queue.put({"type": "error", "message": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/audit/report/{job_id}")
def get_final_report(job_id: str):
    """Fetches the final signed audit memorandum."""
    if job_id not in JOB_FINAL_STATES:
        raise HTTPException(status_code=404, detail="Job report not ready.")
    state = JOB_FINAL_STATES[job_id]
    return {
        "job_id": job_id,
        "final_report": state.get("final_report"),
        "progress_step": state.get("progress_step"),
        "invoice_data": state.get("invoice_data"),
        "ledger_anomalies": state.get("ledger_anomalies")
    }


# Mount Frontend Single Page Application
FRONTEND_DIR = PROJECT_ROOT / "frontend"
FRONTEND_DIR.mkdir(parents=True, exist_ok=True)
INDEX_HTML = FRONTEND_DIR / "index.html"

@app.get("/")
def serve_index():
    if INDEX_HTML.exists():
        return FileResponse(INDEX_HTML)
    return {"message": "Mini Audit Agent Backend is live. Please ensure frontend/index.html exists."}


if __name__ == "__main__":
    import uvicorn
    print(f"Starting Mini Audit Agent FastAPI server on http://{HOST}:{PORT}")
    uvicorn.run("app:app", host=HOST, port=PORT, reload=True)
