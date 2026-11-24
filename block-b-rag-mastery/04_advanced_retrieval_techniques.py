"""
=============================================================================
04_advanced_retrieval_techniques.py: Advanced RAG Retrieval Paradigms
=============================================================================
Block B Advanced Concepts Demonstrated:
1. Maximal Marginal Relevance (MMR): Diversity vs Relevance balancing.
2. Multi-Query Rewriting: Expanding ambiguous user prompts into multiple angles.
3. Hybrid Search: Combining Dense Semantic Vectors with Sparse Lexical (BM25) matching.
4. Re-Ranking (Cross-Encoders): Re-scoring retrieved top candidates for precision.
5. Next-Gen Architectures: HyDE, Parent-Child Chunking, GraphRAG & Agentic RAG.
=============================================================================
"""

import warnings
warnings.filterwarnings("ignore")

from typing import List
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import get_llm
from vector_indexer import build_audit_vector_store


def demonstrate_mmr_vs_topk(vector_store):
    """Compares naive Top-K similarity search with Maximal Marginal Relevance (MMR)."""
    print("\n" + "=" * 65)
    print("TECHNIQUE 1: Top-K vs. Maximal Marginal Relevance (MMR)")
    print("=" * 65)

    query = "What are the rules for encrypting data and cryptographic keys?"

    # Standard Top-K (May return 3 near-identical sentences from the same page)
    print(f"\n[Standard Top-K Similarity Search (k=3)] for: '{query}'")
    top_k_docs = vector_store.similarity_search(query, k=3)
    for i, doc in enumerate(top_k_docs, 1):
        print(f"  Top-K #{i} (Page {doc.metadata.get('page') + 1}): {doc.page_content.strip()[:80]}...")

    # MMR Search: lambda_mult=0.5 balances query relevance with diversity across different topics
    print("\n[Maximal Marginal Relevance (MMR) Search (fetch_k=6, k=3, lambda=0.5)]")
    # InMemoryVectorStore supports max_marginal_relevance_search
    try:
        mmr_docs = vector_store.max_marginal_relevance_search(query, k=3, fetch_k=6, lambda_mult=0.5)
        for i, doc in enumerate(mmr_docs, 1):
            print(f"  MMR #{i} (Page {doc.metadata.get('page') + 1}): {doc.page_content.strip()[:80]}...")
    except NotImplementedError:
        print("  * MMR optimizes: Argmax [ lambda * Sim(doc, query) - (1 - lambda) * MaxSim(doc, selected) ]")
        print("  * It suppresses redundant duplicate chunks, capturing wider cross-section context.")


def demonstrate_multi_query_expansion():
    """Generates 3 diverse query perspectives using LLM to expand retrieval recall."""
    print("\n" + "=" * 65)
    print("TECHNIQUE 2: Multi-Query Rewriting & Query Expansion")
    print("=" * 65)

    llm = get_llm(temperature=0.3)
    user_query = "What happens if a worker leaves?"

    prompt = PromptTemplate.from_template(
        "You are an AI assistant helping a search engine retrieve auditing standards.\n"
        "Generate exactly 3 different semantic variations of the given user query to improve document retrieval.\n"
        "Output each variation on a new line without numbering.\n\n"
        "Original Query: {query}\n\n"
        "Alternate Variations:"
    )

    expansion_chain = prompt | llm | StrOutputParser()
    expansions = expansion_chain.invoke({"query": user_query})

    print(f"[Original User Query]: '{user_query}'")
    print("\n[Generated Multi-Query Variations for Retrieval Fan-Out]:")
    for line in expansions.strip().split("\n"):
        clean_line = line.strip().lstrip("1234567890.- ")
        if clean_line:
            print(f"  • {clean_line}")

    print("\n[How Multi-Query Works in Production]:")
    print("  1. The system queries the vector store in parallel for all 3 variations.")
    print("  2. It computes the set union of retrieved chunks, deduplicating them.")
    print("  3. This dramatically improves Recall when the user uses colloquial or vague phrasing.")


def summarize_advanced_rag_paradigms():
    """Educational summary of advanced RAG architectures."""
    print("\n" + "=" * 65)
    print("ADVANCED RAG ARCHITECTURAL PATTERNS OVERVIEW")
    print("=" * 65)
    print("""
1. Hybrid Search (Dense + Sparse / BM25):
   • Dense Vectors (Embeddings): Excel at semantic understanding ('worker leaves' -> 'separated employee').
   • Sparse Vectors (BM25 / Keyword): Excel at exact acronyms, error codes, and IDs ('AUD-STD-2026-V4').
   • Reciprocal Rank Fusion (RRF): Combines ranks: RRF_score(d) = sum(1 / (60 + rank_i(d))).

2. Re-Ranking with Cross-Encoders:
   • Bi-Encoder (Embedding): Fast retrieval of top-50 candidates via dot-product.
   • Cross-Encoder (Re-Ranker): Evaluates full attention over (Query, Chunk) pairs to re-order top-5.

3. HyDE (Hypothetical Document Embeddings):
   • Generates a hypothetical answer first with an LLM, then embeds the answer to search the index.

4. Parent-Document / Small-to-Big Chunking:
   • Indexes small granular sentences for precise vector matching, but passes the larger parent
     paragraph into the LLM context to preserve full surrounding semantics.

5. GraphRAG:
   • Extracts entities & relationships into an enterprise Knowledge Graph. Perfect for multi-hop
     reasoning across disparate documents (e.g. 'Which vendors share a subprocessor with Cloud X?').

6. Agentic RAG:
   • An autonomous agent plans whether retrieval is needed, routes between multiple vector stores,
     evaluates if retrieved chunks are sufficient, and iteratively re-queries if facts are missing.
""")
    print("=" * 65)


def run_advanced_demo():
    vector_store = build_audit_vector_store()
    demonstrate_mmr_vs_topk(vector_store)
    demonstrate_multi_query_expansion()
    summarize_advanced_rag_paradigms()


if __name__ == "__main__":
    run_advanced_demo()
