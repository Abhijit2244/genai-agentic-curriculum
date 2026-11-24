"""
=============================================================================
01_load_and_chunk.py: Document Parsing & Text Chunking Strategies
=============================================================================
Block B Core Concepts Demonstrated:
1. Document Ingestion: Extracting unstructured text & page numbers from PDFs.
2. Chunking Trade-Offs:
   - Fixed Character Splitting (Naive: truncates mid-sentence/mid-word).
   - Recursive Character Text Splitting (Best Practice: respects paragraph/sentence boundaries).
3. Chunk Overlap: Preserving semantic context across segment boundaries.
4. Metadata Preservation: Tracking `source` and `page` for auditing & citations.
=============================================================================
"""

import warnings
warnings.filterwarnings("ignore")

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, CharacterTextSplitter
from config import PDF_PATH


def run_chunking_demo():
    print("\n" + "=" * 65)
    print("STEP 1: Document Parsing & Chunking Strategies")
    print("=" * 65)

    if not PDF_PATH.exists():
        raise FileNotFoundError(f"PDF not found at {PDF_PATH}. Run generate_audit_pdf.py first.")

    # 1. Load PDF
    print(f"[Loading PDF Document]: {PDF_PATH.name}")
    loader = PyPDFLoader(str(PDF_PATH))
    pages = loader.load()
    print(f"--> Successfully extracted {len(pages)} pages.")

    sample_page = pages[0]
    print(f"--> Page 1 Character Count: {len(sample_page.page_content)} characters")
    print(f"--> Page 1 Metadata: {sample_page.metadata}")

    # 2. Strategy A: Naive Character Splitting
    print("\n[Strategy A: Naive Fixed-Length Splitting (chunk_size=300, overlap=0)]")
    naive_splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=0, separator=" ")
    naive_chunks = naive_splitter.split_documents(pages)
    print(f"--> Generated {len(naive_chunks)} chunks.")
    print("--> Drawback: Can sever paragraphs and compound sentences abruptly.")

    # 3. Strategy B: Recursive Character Text Splitting (Industry Standard)
    # Tries to split on paragraphs ("\n\n"), then sentences ("\n"), then words (" ")
    print("\n[Strategy B: Recursive Character Splitting (chunk_size=400, overlap=80)]")
    recursive_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=80,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )
    recursive_chunks = recursive_splitter.split_documents(pages)
    print(f"--> Generated {len(recursive_chunks)} high-quality semantic chunks.")

    # Inspect first 2 chunks and metadata
    print("\n" + "-" * 65)
    print("[Inspecting Enriched Chunks for Audit Tracing]:")
    for i, chunk in enumerate(recursive_chunks[:2], 1):
        page_num = chunk.metadata.get("page", 0) + 1  # 1-indexed for humans
        print(f"\n--- Chunk #{i} | Source: {chunk.metadata.get('source')} | Page: {page_num} ---")
        print(f"Length: {len(chunk.page_content)} chars")
        print(f"Content:\n{chunk.page_content.strip()}")
    print("-" * 65)

    print("\n[Why Chunk Overlap Matters]:")
    print("  An 80-character overlap guarantees that terms spanning chunk boundaries")
    print("  (e.g., 'Quarterly entitlement audits... accounts of separated employees')")
    print("  are never orphaned or lost during vector similarity retrieval.")
    print("=" * 65)

    return recursive_chunks


if __name__ == "__main__":
    run_chunking_demo()
