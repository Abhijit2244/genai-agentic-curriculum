"""
=============================================================================
Block B: RAG (Retrieval-Augmented Generation) - Interactive Mastery Navigator
=============================================================================
Practice: RAG over a PDF auditing standard using LangChain with vector search.
Ask questions and print the sources.
=============================================================================
"""

import sys
from importlib import import_module
from config import PDF_PATH


def banner():
    print("""
=============================================================================
  🌟 BLOCK B: RETRIEVAL-AUGMENTED GENERATION (RAG) MASTERY 🌟
  LangChain + Google Gemini 3.5 + Vector Search Practice Project
=============================================================================
  Target Document: Public Auditing Standard PDF (SOC-2 & ISO-27001)
  Topics Covered:
  [1] Document Loading, Recursive Chunking & Overlap Strategy
  [2] Vector Store Indexing, Embedding Generation & Similarity Scoring
  [3] End-to-End RAG Pipeline with Strict Inline Citations & Source Audit Trail
  [4] Advanced Retrieval: MMR, Multi-Query Expansion, Hybrid & Re-ranking
=============================================================================
""")


def menu():
    print("Select an option:")
    print("  1. Run Demo 1: Document Parsing & Chunking Strategies")
    print("  2. Run Demo 2: Vector Store Indexing & Similarity Search")
    print("  3. Run Demo 3: End-to-End RAG Pipeline with Citations")
    print("  4. Run Demo 4: Advanced Retrieval (MMR, Multi-Query, Re-ranking)")
    print("  5. Run ALL Demos Sequentially")
    print("  6. Interactive Auditor Query Mode (Ask your own question)")
    print("  0. Exit")
    print("-" * 65)


def run_all():
    print("\n>>> EXECUTING FULL BLOCK B RAG PIPELINE <<<\n")
    
    print("\n" + "#" * 65)
    print("# MODULE 1: Document Loading & Chunking")
    print("#" * 65)
    mod1 = import_module("01_load_and_chunk")
    mod1.run_chunking_demo()

    print("\n" + "#" * 65)
    print("# MODULE 2: Vector Store Indexing & Similarity Search")
    print("#" * 65)
    mod2 = import_module("02_vector_store_indexing")
    mod2.run_vector_search_demo()

    print("\n" + "#" * 65)
    print("# MODULE 3: End-to-End RAG Pipeline with Citations")
    print("#" * 65)
    mod3 = import_module("03_rag_pipeline_with_citations")
    mod3.run_rag_practice_demo()

    print("\n" + "#" * 65)
    print("# MODULE 4: Advanced Retrieval Techniques")
    print("#" * 65)
    mod4 = import_module("04_advanced_retrieval_techniques")
    mod4.run_advanced_demo()

    print("\n" + "=" * 65)
    print("🎉 ALL BLOCK B RAG MODULES EXECUTED SUCCESSFULLY!")
    print("=" * 65 + "\n")


def interactive_mode():
    print("\n" + "=" * 65)
    print("INTERACTIVE AUDITOR QUERY CONSOLE")
    print("Ask any question regarding the ISO 27001 / SOC 2 Auditing Standard PDF.")
    print("Type 'exit' to return to main menu.")
    print("=" * 65)
    
    mod2 = import_module("02_vector_store_indexing")
    mod3 = import_module("03_rag_pipeline_with_citations")
    
    vector_store = mod2.build_audit_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    rag_chain = mod3.create_audit_rag_chain(retriever)

    while True:
        user_q = input("\nEnter Audit Question: ").strip()
        if not user_q:
            continue
        if user_q.lower() in ["exit", "quit", "0"]:
            break
        mod3.ask_audit_question(retriever, rag_chain, user_q)


def main():
    # Verify PDF exists or generate
    if not PDF_PATH.exists():
        print(f"Generating missing audit PDF at {PDF_PATH}...")
        gen_mod = import_module("data.generate_audit_pdf")
        gen_mod.generate_audit_standard_pdf(PDF_PATH)

    banner()
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        run_all()
        return

    while True:
        menu()
        choice = input("Enter choice (0-6): ").strip()
        if choice == "1":
            mod = import_module("01_load_and_chunk")
            mod.run_chunking_demo()
        elif choice == "2":
            mod = import_module("02_vector_store_indexing")
            mod.run_vector_search_demo()
        elif choice == "3":
            mod = import_module("03_rag_pipeline_with_citations")
            mod.run_rag_practice_demo()
        elif choice == "4":
            mod = import_module("04_advanced_retrieval_techniques")
            mod.run_advanced_demo()
        elif choice == "5":
            run_all()
        elif choice == "6":
            interactive_mode()
        elif choice == "0":
            print("Exiting. Happy learning!")
            break
        else:
            print("Invalid choice, please select between 0 and 6.\n")


if __name__ == "__main__":
    main()
