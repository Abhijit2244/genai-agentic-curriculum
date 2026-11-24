"""
=============================================================================
04_embeddings_demo.py: Text Embeddings & Cosine Similarity (Text -> Vectors)
=============================================================================
Block A Core Concepts Demonstrated:
1. Embeddings: Transforming unstructured text into dense numerical vectors.
2. Semantic Space: Words and concepts with similar meanings cluster together.
3. Cosine Similarity: Measuring the angle/distance between vectors (-1 to 1).
4. Foundation for RAG: How vector databases index documents and retrieve context.
=============================================================================
"""

import math
from typing import List
from config import get_gemini_client, EMBEDDING_MODEL


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calculate the cosine similarity between two numerical vectors."""
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_v1 = math.sqrt(sum(a * a for a in v1))
    norm_v2 = math.sqrt(sum(b * b for b in v2))
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
    return dot_product / (norm_v1 * norm_v2)


def run_embeddings_demo():
    print("\n" + "=" * 65)
    print("EMBEDDINGS DEMO: Text -> Vectors & Semantic Similarity")
    print("=" * 65)

    client = get_gemini_client()

    sentences = [
        "Artificial intelligence and machine learning neural models",
        "Deep learning and transformer architectures for natural language",
        "How to bake delicious homemade chocolate chip cookies",
    ]

    print("[Sentences to Embed]:")
    for i, s in enumerate(sentences, 1):
        print(f"  {i}. \"{s}\"")

    print(f"\n[Generating embeddings using model: '{EMBEDDING_MODEL}']...")

    vectors = []
    for s in sentences:
        res = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=s,
        )
        vec = res.embeddings[0].values
        vectors.append(vec)

    dim = len(vectors[0])
    print(f"--> Successfully generated dense vectors! Dimension size: {dim}")
    print(f"--> First 5 dimensions of Sentence 1: {[round(x, 4) for x in vectors[0][:5]]}...")

    # Calculate similarities
    sim_1_2 = cosine_similarity(vectors[0], vectors[1])
    sim_1_3 = cosine_similarity(vectors[0], vectors[2])

    print("\n[Cosine Similarity Comparison]:")
    print(f"  • Sim(Sentence 1, Sentence 2) [AI vs Deep Learning] : {sim_1_2:.4f} (High Semantic Overlap)")
    print(f"  • Sim(Sentence 1, Sentence 3) [AI vs Baking Cookies] : {sim_1_3:.4f} (Low Semantic Overlap)")

    print("\n[Core Takeaway for RAG]:")
    print("  In RAG, queries are embedded into this same vector space to retrieve")
    print("  the top-k closest reference chunks before prompting the generator LLM.")
    print("=" * 65)


if __name__ == "__main__":
    run_embeddings_demo()
