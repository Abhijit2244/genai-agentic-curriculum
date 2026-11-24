"""
=============================================================================
02_vector_store_indexing.py: Vector Store Embeddings, Indexing & Search
=============================================================================
Block B Core Concepts Demonstrated:
1. Embedding Generation: Transforming chunked text into dense 3072-dim vectors.
2. Vector Indexing: Storing vector embeddings alongside rich metadata.
3. Similarity Search & Scoring: Measuring semantic proximity (Cosine Similarity).
4. Top-k Retrieval & Metadata Filtering: Narrowing search scopes.
5. Ecosystem Context: How in-memory stores relate to FAISS, Chroma, pgvector & Pinecone.
=============================================================================
"""

import warnings
warnings.filterwarnings("ignore")

from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import PDF_PATH, get_embeddings


from vector_indexer import build_audit_vector_store


def run_vector_search_demo():
    print("\n" + "=" * 65)
    print("STEP 2: Vector Database Indexing & Similarity Search")
    print("=" * 65)

    vector_store = build_audit_vector_store()

    # Query 1: Semantic match (doesn't use exact wording from the document)
    query = "What happens to accounts of workers who leave the company?"
    print(f"\n[Semantic Query]: '{query}'")
    print("[Performing Top-K Vector Search (k=2)]...\n")

    results_with_scores = vector_store.similarity_search_with_score(query, k=2)

    for rank, (doc, score) in enumerate(results_with_scores, 1):
        page_num = doc.metadata.get("page", 0) + 1
        print(f"Result Rank #{rank} | Relevance Score: {score:.4f} | Page: {page_num}")
        print(f"Snippet: {doc.page_content.strip()}")
        print("-" * 50)

    # Query 2: Metadata Filtering
    # Only retrieve chunks originating from Page 2 (Cryptographic Standards)
    print("\n[Metadata Filtering Demo]: Restricting search strictly to Page 2")
    crypto_query = "What algorithm is required for storage encryption?"
    
    filtered_results = vector_store.similarity_search(
        crypto_query,
        k=2,
        filter=lambda doc: doc.metadata.get("page") == 1  # 0-indexed page 1 = human Page 2
    )

    for rank, doc in enumerate(filtered_results, 1):
        print(f"Filtered Rank #{rank} | Page: {doc.metadata.get('page') + 1}")
        print(f"Snippet: {doc.page_content.strip()}")
        print("-" * 50)

    print("\n[Vector Database Landscape Comparison]:")
    print("  • FAISS (Facebook AI): In-memory C++ library, extremely fast for billion-scale ANN.")
    print("  • Chroma: Lightweight embedded vector database, popular for local development.")
    print("  • pgvector: PostgreSQL extension, perfect for transactional apps needing ACID + vectors.")
    print("  • Pinecone / Azure AI Search: Fully managed, serverless, enterprise multi-tenant cloud engines.")
    print("=" * 65)

    return vector_store


if __name__ == "__main__":
    run_vector_search_demo()
