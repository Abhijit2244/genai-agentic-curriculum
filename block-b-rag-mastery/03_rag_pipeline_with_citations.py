"""
=============================================================================
03_rag_pipeline_with_citations.py: End-to-End RAG Pipeline with Citations
=============================================================================
Block B Core Practice:
1. RAG over a PDF Auditing Standard using LangChain.
2. Context Construction & Grounding: Feeding retrieved context into the LLM.
3. Citation & Source Tracing: Ensuring every claim is attributable to a specific page.
4. Hallucination Mitigation: Preventing extrapolation beyond verified policy text.
=============================================================================
"""

import warnings
warnings.filterwarnings("ignore")

from typing import List, Tuple
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from config import get_llm
from vector_indexer import build_audit_vector_store


def format_docs_with_citations(docs: List[Document]) -> str:
    """Formats retrieved document chunks with explicit page metadata tags."""
    formatted_chunks = []
    for doc in docs:
        page_num = doc.metadata.get("page", 0) + 1
        source_name = doc.metadata.get("source", "Audit-Standard")
        header = f"[DOCUMENT: {source_name} | PAGE: {page_num}]"
        formatted_chunks.append(f"{header}\n{doc.page_content.strip()}")
    return "\n\n" + ("=" * 40) + "\n\n".join(formatted_chunks) + "\n" + ("=" * 40)


def create_audit_rag_chain(retriever):
    """Builds an LCEL (LangChain Expression Language) RAG Chain with citation enforcement."""
    llm = get_llm(temperature=0.0)

    system_template = (
        "You are a certified Lead IT Security Auditor reviewing company policies.\n"
        "Your task is to provide strict, factual answers grounded EXCLUSIVELY in the provided context.\n\n"
        "RULES:\n"
        "1. Answer ONLY using information explicitly stated in the context.\n"
        "2. If the policy does not contain the answer, reply: 'The standard does not specify this policy.'\n"
        "3. Every factual claim MUST include an inline citation to its source page in brackets, e.g., '[Page 2]'.\n"
        "4. Structure your response with concise bullet points.\n\n"
        "AUDIT CONTEXT:\n{context}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("human", "{question}"),
    ])

    # LCEL pipeline: Question -> Retrieve -> Format Context -> Prompt -> LLM -> String
    rag_chain = (
        {"context": retriever | format_docs_with_citations, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


def ask_audit_question(retriever, rag_chain, question: str):
    """Executes RAG query and prints grounded answer alongside source citations."""
    print("\n" + "=" * 65)
    print(f"AUDIT QUESTION: '{question}'")
    print("=" * 65)

    # 1. Retrieve raw source chunks for audit verification
    retrieved_docs = retriever.invoke(question)

    # 2. Generate grounded answer
    answer = rag_chain.invoke(question)

    print("\n[GROUNDED AUDITOR ANSWER WITH CITATIONS]:")
    print(answer)
    print("\n" + "-" * 65)

    print(f"[VERIFIED SOURCE AUDIT TRAIL] ({len(retrieved_docs)} Chunks Retrieved):")
    for idx, doc in enumerate(retrieved_docs, 1):
        page = doc.metadata.get("page", 0) + 1
        print(f"\n  Source Citation #{idx}:")
        print(f"    • File Origin : {doc.metadata.get('source')}")
        print(f"    • Document Page: Page {page}")
        print(f"    • Content Excerpt:")
        snippet_lines = doc.page_content.strip().split("\n")
        for line in snippet_lines[:3]:
            print(f"        {line}")
        if len(snippet_lines) > 3:
            print(f"        ... [truncated]")
    print("-" * 65)
    return answer, retrieved_docs


def run_rag_practice_demo():
    print("\n" + "=" * 65)
    print("STEP 3: LangChain RAG Over Auditing Standard PDF")
    print("=" * 65)

    # Initialize vector store and retriever
    vector_store = build_audit_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    # Create the RAG chain
    rag_chain = create_audit_rag_chain(retriever)

    # Question 1: Incident response timelines (cross-page / multi-clause)
    q1 = "What are the exact mandatory notification timelines for critical P1 incidents and external regulatory disclosures?"
    ask_audit_question(retriever, rag_chain, q1)

    # Question 2: Cryptographic standards
    q2 = "What encryption algorithms are required for data at rest and how often must keys be rotated?"
    ask_audit_question(retriever, rag_chain, q2)

    # Question 3: Negative test (Unanswerable query to verify hallucination prevention)
    q3 = "What is the policy for using personal smartphones for company cryptocurrency mining?"
    ask_audit_question(retriever, rag_chain, q3)

    print("\n" + "=" * 65)
    print("RAG PRACTICE DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 65)


if __name__ == "__main__":
    run_rag_practice_demo()
