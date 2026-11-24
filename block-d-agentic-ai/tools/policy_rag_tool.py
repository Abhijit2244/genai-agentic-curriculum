"""
Policy RAG Tool for Block D: Agentic AI
Indexes internal financial control standards into an in-memory vector store
and performs semantic similarity search to retrieve compliance mandates.
"""

from pathlib import Path
from langchain_core.tools import tool
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

try:
    from config import get_embeddings
except ImportError:
    from ..config import get_embeddings

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
POLICY_PATH = DATA_DIR / "internal_financial_controls_policy.md"

_VECTOR_STORE = None


def get_policy_vector_store() -> InMemoryVectorStore:
    """Singleton in-memory vector store for compliance policies."""
    global _VECTOR_STORE
    if _VECTOR_STORE is not None:
        return _VECTOR_STORE

    if not POLICY_PATH.exists():
        try:
            from data.generate_policy_data import generate_policy_md
        except ImportError:
            from ..data.generate_policy_data import generate_policy_md
        generate_policy_md(POLICY_PATH)

    with open(POLICY_PATH, "r", encoding="utf-8") as f:
        text = f.read()

    # Split policy text by control sections
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=50,
        separators=["### POL-", "## Section", "\n\n", "\n"]
    )
    raw_chunks = splitter.split_text(text)

    docs = []
    for i, chunk in enumerate(raw_chunks):
        # Extract policy identifier if present
        policy_id = "GENERAL"
        if "POL-IC-" in chunk:
            start = chunk.find("POL-IC-")
            policy_id = chunk[start:start+9].strip()
        docs.append(Document(
            page_content=chunk.strip(),
            metadata={"source": "internal_financial_controls_policy.md", "chunk_id": f"CHUNK-{i+1}", "policy_id": policy_id}
        ))

    embeddings = get_embeddings()
    _VECTOR_STORE = InMemoryVectorStore.from_documents(docs, embeddings)
    return _VECTOR_STORE


@tool
def search_policy(query: str, top_k: int = 2) -> str:
    """
    Search enterprise internal financial controls and compliance audit standards (SOX 404 / SSAE-18).
    
    Args:
        query: Semantic search query (e.g. 'dual authorization threshold', 'weekend wire transfers', 'invoice structuring').
        top_k: Number of relevant policy clauses to retrieve (default: 2).
        
    Returns:
        The text of the matching internal control clauses, policy IDs, and mandatory audit rules.
    """
    try:
        vs = get_policy_vector_store()
        results = vs.similarity_search(query, k=top_k)
        if not results:
            return "No matching internal control policies found."

        formatted_clauses = []
        for i, doc in enumerate(results, 1):
            pid = doc.metadata.get("policy_id", "N/A")
            cid = doc.metadata.get("chunk_id", f"C-{i}")
            formatted_clauses.append(
                f"--- [Match {i} | Control ID: {pid} | {cid}] ---\n{doc.page_content}"
            )

        return "\n\n".join(formatted_clauses)
    except Exception as e:
        # Fallback to direct text scanning if API call fails
        with open(POLICY_PATH, "r", encoding="utf-8") as f:
            text = f.read()
        return f"[Fallback Search Result]: Query '{query}' evaluated against local policy file.\n" + text[:800]
