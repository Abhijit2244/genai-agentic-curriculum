"""
Shared Vector Store Indexing Logic for Block B RAG
"""

from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import PDF_PATH, get_embeddings


def build_audit_vector_store() -> InMemoryVectorStore:
    """Extracts chunks from the audit PDF, computes embeddings, and builds vector store."""
    embeddings = get_embeddings()
    loader = PyPDFLoader(str(PDF_PATH))
    pages = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=80,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = splitter.split_documents(pages)

    vector_store = InMemoryVectorStore.from_documents(chunks, embeddings)
    return vector_store
