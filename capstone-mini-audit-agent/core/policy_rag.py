"""
policy_rag.py — In-Memory RAG Engine for Internal Accounting & SOX 404 Controls
Retrieves governing policy standards, clauses, and violation codes via semantic search.
"""

from pathlib import Path
from typing import Dict, Any, List
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import get_embeddings, BASE_DIR

DEFAULT_POLICY_PATH = BASE_DIR / "sample_data" / "compliance_policy.md"
_VECTOR_STORE = None


def get_policy_vector_store(policy_path: Path = DEFAULT_POLICY_PATH) -> InMemoryVectorStore:
    """Singleton in-memory vector store indexing the compliance policy document."""
    global _VECTOR_STORE
    if _VECTOR_STORE is not None:
        return _VECTOR_STORE

    if not policy_path.exists():
        from sample_data.generate_test_invoices import generate_all
        generate_all()

    with open(policy_path, "r", encoding="utf-8") as f:
        text = f.read()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["### Standard", "## Mandatory", "\n\n", "\n"]
    )
    raw_chunks = splitter.split_text(text)

    docs = []
    for i, chunk in enumerate(raw_chunks):
        code = "GENERAL"
        if "AP-" in chunk:
            idx = chunk.find("AP-")
            code = chunk[idx:idx+10].strip("`. \n")
        docs.append(Document(
            page_content=chunk.strip(),
            metadata={"source": "compliance_policy.md", "chunk_id": f"CHUNK-{i+1}", "code": code}
        ))

    embeddings = get_embeddings()
    _VECTOR_STORE = InMemoryVectorStore.from_documents(docs, embeddings)
    return _VECTOR_STORE


def retrieve_policy_context(query: str, top_k: int = 2) -> List[Dict[str, Any]]:
    """
    Performs semantic vector retrieval across internal compliance standards.
    Returns matched documents with metadata and citations.
    """
    try:
        vs = get_policy_vector_store()
        results = vs.similarity_search(query, k=top_k)
        return [
            {
                "citation": doc.metadata.get("code", "GENERAL"),
                "chunk_id": doc.metadata.get("chunk_id"),
                "text": doc.page_content
            }
            for doc in results
        ]
    except Exception as e:
        # Fallback reading
        with open(DEFAULT_POLICY_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        return [{
            "citation": "AP-FALLBACK",
            "chunk_id": "FALLBACK-1",
            "text": content[:600]
        }]
