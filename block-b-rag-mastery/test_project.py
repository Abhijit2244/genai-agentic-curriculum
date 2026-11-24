"""
Automated Test Verification for Block B RAG Mastery Project
"""

import unittest
from pathlib import Path
from importlib import import_module
from config import PDF_PATH


class TestBlockBRAGMastery(unittest.TestCase):
    def test_01_pdf_exists_and_loads(self):
        self.assertTrue(PDF_PATH.exists(), f"PDF does not exist at {PDF_PATH}")
        from langchain_community.document_loaders import PyPDFLoader
        loader = PyPDFLoader(str(PDF_PATH))
        pages = loader.load()
        self.assertEqual(len(pages), 4)

    def test_02_chunking(self):
        mod1 = import_module("01_load_and_chunk")
        chunks = mod1.run_chunking_demo()
        self.assertTrue(len(chunks) >= 8)
        # Check that page metadata is preserved
        self.assertIn("page", chunks[0].metadata)
        self.assertIn("source", chunks[0].metadata)

    def test_03_vector_indexing(self):
        mod2 = import_module("02_vector_store_indexing")
        vector_store = mod2.build_audit_vector_store()
        results = vector_store.similarity_search("MFA requirements", k=2)
        self.assertTrue(len(results) == 2)
        # The top result for MFA should be on Page 1 (index 0)
        self.assertEqual(results[0].metadata.get("page"), 0)

    def test_04_rag_pipeline_and_citations(self):
        mod2 = import_module("02_vector_store_indexing")
        mod3 = import_module("03_rag_pipeline_with_citations")
        vector_store = mod2.build_audit_vector_store()
        retriever = vector_store.as_retriever(search_kwargs={"k": 2})
        rag_chain = mod3.create_audit_rag_chain(retriever)
        
        answer, docs = mod3.ask_audit_question(
            retriever,
            rag_chain,
            "What is the maximum time for deprovisioning separated employees?"
        )
        self.assertIsNotNone(answer)
        self.assertTrue(len(docs) == 2)
        # Should mention 60 minutes and cite page
        self.assertIn("60", answer)
        self.assertIn("Page", answer)


if __name__ == "__main__":
    unittest.main()
