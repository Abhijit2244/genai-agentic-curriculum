"""
test_project.py — Automated Unit Test Suite for Capstone: Mini Audit Agent
Tests:
1. OpenCV preprocessing
2. Multimodal OCR field extraction
3. Pandas ledger duplicate & structuring checks
4. Policy RAG semantic retrieval
5. MCP Server tool execution
6. LangGraph orchestration, Human-in-the-Loop breakpoint, and report completion
"""

import sys
import unittest
from pathlib import Path
from langgraph.checkpoint.memory import MemorySaver

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.ocr_engine import preprocess_invoice_image, extract_invoice_fields
from core.ledger_analyzer import check_invoice_against_ledger
from core.policy_rag import retrieve_policy_context
from mcp_service.audit_mcp_server import ocr_invoice, check_ledger_anomalies, search_compliance_policy
from agent.audit_graph import build_audit_workflow


SAMPLE_CYBER_IMAGE = str(BASE_DIR / "sample_data" / "invoice_cybershield_dup.png")
SAMPLE_APEX_IMAGE = str(BASE_DIR / "sample_data" / "invoice_apex_structuring.png")
SAMPLE_LEDGER_CSV = str(BASE_DIR / "sample_data" / "ledger.csv")


class TestCapstoneMiniAuditAgent(unittest.TestCase):

    def test_01_opencv_preprocessing(self):
        """Test OpenCV computer vision pipeline (grayscale, CLAHE, Otsu thresholding)."""
        preprocessed = preprocess_invoice_image(SAMPLE_CYBER_IMAGE)
        self.assertTrue(Path(preprocessed).exists())
        self.assertIn("_cv_preprocessed", preprocessed)

    def test_02_ocr_extraction(self):
        """Test multimodal OCR field extraction on invoice image."""
        fields = extract_invoice_fields(SAMPLE_CYBER_IMAGE)
        self.assertEqual(fields.get("invoice_number"), "INV-2026-004")
        self.assertIn("cybershield", fields.get("vendor", "").lower())
        self.assertAlmostEqual(float(fields.get("amount", 0.0)), 14250.00, delta=10.0)

    def test_03_pandas_duplicate_detection(self):
        """Test pandas ledger analysis detecting duplicate invoice AP-DUP-03."""
        anomalies = check_invoice_against_ledger(
            ledger_csv_path=SAMPLE_LEDGER_CSV,
            vendor="CyberShield Solutions",
            amount=14250.00,
            invoice_id="INV-2026-004"
        )
        self.assertEqual(anomalies["status"], "flagged")
        self.assertGreater(anomalies["anomalies_detected"], 0)
        violation_codes = [a["violation_code"] for a in anomalies["anomalies"]]
        self.assertIn("AP-DUP-03", violation_codes)

    def test_04_policy_rag_retrieval(self):
        """Test semantic vector retrieval for internal accounting controls."""
        citations = retrieve_policy_context("duplicate invoice quarantine 72 hours")
        self.assertTrue(len(citations) > 0)
        codes = [c.get("citation") for c in citations]
        self.assertTrue(any("AP-DUP" in code or "AP-" in code for code in codes))

    def test_05_mcp_server_tools(self):
        """Test tools exposed by the MCP server."""
        ledger_res = check_ledger_anomalies(
            ledger_csv_path=SAMPLE_LEDGER_CSV,
            vendor="Apex Cloud Holdings",
            amount=49990.00,
            invoice_id="INV-2026-007"
        )
        self.assertEqual(ledger_res["status"], "flagged")
        violation_codes = [a["violation_code"] for a in ledger_res["anomalies"]]
        self.assertIn("AP-STRUCT-02", violation_codes)

    def test_06_langgraph_breakpoint_and_resumption(self):
        """Test LangGraph execution halting at human_approval and resuming after sign-off."""
        checkpointer = MemorySaver()
        workflow = build_audit_workflow(checkpointer=checkpointer)
        job_id = "test-job-audit-001"
        config = {"configurable": {"thread_id": job_id}}

        initial_state = {
            "job_id": job_id,
            "invoice_image_path": SAMPLE_CYBER_IMAGE,
            "ledger_csv_path": SAMPLE_LEDGER_CSV,
            "invoice_data": None,
            "ledger_anomalies": None,
            "policy_citations": None,
            "reasoning_synthesis": None,
            "pending_approval": False,
            "human_approved": None,
            "human_notes": None,
            "final_report": None,
            "progress_step": "STARTED",
            "status_message": "Running unit test..."
        }

        # 1. Run until breakpoint
        workflow.invoke(initial_state, config=config)

        # 2. Inspect state at breakpoint
        snapshot = workflow.get_state(config)
        self.assertEqual(snapshot.next, ("human_approval",))
        self.assertEqual(snapshot.values.get("progress_step"), "AWAITING_HUMAN_APPROVAL")
        self.assertIsNotNone(snapshot.values.get("invoice_data"))
        self.assertIsNotNone(snapshot.values.get("ledger_anomalies"))

        # 3. Simulate Human Sign-Off
        workflow.update_state(
            config,
            {
                "human_approved": True,
                "human_notes": "Unit test verified: duplicate payment certified by auditor."
            }
        )

        # 4. Resume graph execution
        workflow.invoke(None, config=config)

        # 5. Verify final report
        final_snapshot = workflow.get_state(config)
        self.assertEqual(final_snapshot.next, ())
        self.assertEqual(final_snapshot.values.get("progress_step"), "REPORT_READY")
        self.assertIn("OFFICIAL SOX 404 AUDIT EXCEPTION MEMORANDUM", final_snapshot.values.get("final_report", ""))


if __name__ == "__main__":
    unittest.main()
