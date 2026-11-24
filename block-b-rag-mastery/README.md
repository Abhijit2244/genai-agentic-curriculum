# Block B: Retrieval-Augmented Generation (RAG) Mastery

> **Curriculum Module**: LLMs, RAG, Agentic AI, MCP (The Most Important Day)  
> **Topic**: Block B: RAG Architecture & Implementation (3 Hours Intensive)  
> **Frameworks**: LangChain, Modern Google GenAI (`gemini-3.5-flash-lite`, `gemini-embedding-001`), Vector Stores  
> **Location**: `block-b-rag-mastery/`

---

## 📑 Table of Contents
1. [Core Theoretical Foundations](#1-core-theoretical-foundations)
   - Why RAG? (Parametric vs. Non-Parametric Memory)
   - The RAG Pipeline: Load ➔ Clean ➔ Chunk ➔ Embed ➔ Store ➔ Retrieve ➔ Augment ➔ Generate
   - Chunking Strategies & Overlap Dynamics
   - Embedding Models & Similarity Distance Metrics
   - Vector Databases Compared (FAISS, Chroma, pgvector, Azure AI Search, Pinecone)
   - Retrieval Mechanics: Top-K, MMR, Metadata Filtering, Hybrid Search & Re-Ranking
   - Prompt Construction with Citations & Source Tracing (Audit Standard)
   - Advanced RAG Paradigms (Query Rewriting, HyDE, Parent-Child, GraphRAG, Agentic RAG)
   - Document Parsing Realities: PDFs, Tables & OCR
   - Evaluation Metrics: The RAG Triad & RAGAS
   - Enterprise Access Control (RBAC/ACL) & Data Privacy
   - Strategic Decision Framework: RAG vs. Fine-Tuning vs. Long Context Window
2. [Project Architecture & Quickstart](#2-project-architecture--quickstart)
3. [Practice Walkthrough & Code Modules](#3-practice-walkthrough--code-modules)
4. [Verification & Automated Tests](#4-verification--automated-tests)

---

## 1. Core Theoretical Foundations

### 1.1 Why RAG? (Parametric vs. Non-Parametric Memory)
LLMs possess two distinct memory mechanisms:
1. **Parametric Memory**: Knowledge encoded inside the billions of static weights $\theta$ during pretraining. It is static, expensive to update, and subject to knowledge cutoff dates and probabilistic hallucinations.
2. **Non-Parametric Memory**: Dynamic external knowledge storage (vector databases, search indexes, relational tables, documents).

**Retrieval-Augmented Generation (RAG)** marries both: it dynamically retrieves verified external context from non-parametric stores and injects it into the prompt, giving the model:
- **Freshness**: Access to real-time, up-to-the-minute data without re-training.
- **Private Domain Knowledge**: Secure querying over proprietary enterprise documents (PDFs, policies, wikis).
- **Hallucination Suppression**: Grounding generation strictly in retrieved facts.
- **Source Citations & Provenance**: Enabling transparent auditing by tracing every statement to a specific document, page, and paragraph.

---

### 1.2 The End-to-End RAG Pipeline

```
[Unstructured Data] (PDF, DOCX, MD)
       │
       ▼ 1. Load & Extract Text
[Raw Text + Page Metadata]
       │
       ▼ 2. Clean & Chunk (e.g., 400 chars, 80 overlap)
[Discrete Document Chunks]
       │
       ▼ 3. Embed (Bi-Encoder Model -> 3072-dim vectors)
[Dense Vector Embeddings]
       │
       ▼ 4. Index & Store
[Vector Database / Index] (FAISS, Chroma, pgvector, Pinecone)
       │
       │ ── User Query: "What are the MFA rules?" ──
       ▼ 5. Similarity Search (Cosine, Top-K, MMR, Hybrid BM25)
[Top-k Grounded Chunks]
       │
       ▼ 6. Augment Prompt (System Prompt + Injected Context + Citations)
[Grounding Prompt]
       │
       ▼ 7. Generate (LLM: Gemini 3.5 Flash)
[Grounded Answer with Page Citations [Page 1]]
```

---

### 1.3 Chunking Strategies & Overlap Dynamics
Chunk size dictates the trade-off between **semantic specificity** and **contextual completeness**:

| Strategy | Mechanism | Pros | Cons / Best Use |
| :--- | :--- | :--- | :--- |
| **Fixed-Size Chunking** | Splits strictly every $N$ characters/tokens. | Fast, trivial to implement. | Breaks mid-sentence, severs tables. Naive. |
| **Recursive Character Splitting** | Recursively tries separators: `["\n\n", "\n", ". ", " ", ""]`. | Keeps paragraphs and sentences intact. | **Industry standard** for general documents & PDFs. |
| **Document-Structure Chunking** | Splits on Markdown headers (`#`, `##`) or PDF sections. | High semantic cohesion per section. | Variable chunk sizes; requires structured input. |
| **Semantic Chunking** | Computes cosine distance between consecutive sentences; splits where distance spikes. | Purely semantic topic grouping. | Computationally expensive embedding overhead. |
| **Parent-Child (Small-to-Big)** | Indexes small sentences for vector search; returns larger parent paragraph to LLM. | Maximum search precision + full context preservation. | Requires hierarchical indexing in vector store. |

#### Why Chunk Overlap is Critical
If a crucial compliance sentence spans the boundary between Chunk 1 and Chunk 2 (e.g., `"Accounts of separated employees must be permanently deprovisioned"` at end of Chunk 1, and `"within 60 minutes of HR notice"` at start of Chunk 2), a search for *"termination timeline"* without overlap might rank neither chunk high enough. An overlap of **15%–25% (e.g., 80 characters)** guarantees continuous semantic coverage across boundaries.

---

### 1.4 Embedding Models & Vector Similarity
An embedding model converts a sequence of tokens into a continuous geometric vector $\vec{v} \in \mathbb{R}^D$ (e.g., $D = 3072$ for `gemini-embedding-001`).

$$\vec{u} = \text{Embed}(\text{Text}_A), \quad \vec{v} = \text{Embed}(\text{Text}_B)$$

#### Mathematical Distance Metrics:
1. **Cosine Similarity** (Measures orientation, invariant to text length):
   $$\text{CosineSim}(\vec{u}, \vec{v}) = \frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\|_2 \|\vec{v}\|_2} = \cos(\theta) \in [-1, 1]$$
2. **Dot Product (Inner Product)**:
   $$\langle \vec{u}, \vec{v} \rangle = \sum_{i=1}^{D} u_i v_i \quad (\text{Identical to Cosine if vectors are } L_2\text{-normalized})$$
3. **Euclidean Distance ($L_2$)**:
   $$\|\vec{u} - \vec{v}\|_2 = \sqrt{\sum_{i=1}^{D} (u_i - v_i)^2}$$

---

### 1.5 Vector Databases Compared

| Engine | Storage Architecture | Index Algorithm | Best Fit | Enterprise Notes |
| :--- | :--- | :--- | :--- | :--- |
| **FAISS** (Meta) | In-Memory / Local C++ | HNSW, IVF, PQ | Offline batch evaluation, maximum ANN speed | No native persistent client/server; library only. |
| **Chroma** | Embedded SQLite / DuckDB | HNSW | Local developer prototyping, lightweight apps | Single-node; limited distributed multi-tenancy. |
| **pgvector** | Relational PostgreSQL extension | HNSW, IVFFlat | Applications already using PostgreSQL | Full ACID compliance, transactional joins with business data. |
| **Azure AI Search** | Enterprise Cloud Managed | HNSW + BM25 + Semantic Ranker | Microsoft Azure ecosystem, SOC-2 / FedRAMP | Built-in hybrid search and semantic re-ranking engine. |
| **Pinecone** | Serverless Cloud Distributed | Proprietary Graph ANN | High-scale, multi-tenant cloud-native SaaS | Zero ops, metadata filtering, horizontal autoscaling. |

---

### 1.6 Retrieval Mechanics: Top-K, MMR, Hybrid Search & Re-Ranking

#### 1. Top-K Similarity Search
Retrieves the $k$ chunks with highest cosine similarity to the query vector.  
*Limitation*: Often retrieves 3 near-identical chunks from the same paragraph, wasting prompt context on redundant information.

#### 2. Maximal Marginal Relevance (MMR)
Balances **Relevance** to the query with **Diversity** among already chosen chunks:

$$\text{MMR} = \operatorname{argmax}_{d_i \in R \setminus S} \left[ \lambda \cdot \text{Sim}(d_i, q) - (1 - \lambda) \max_{d_j \in S} \text{Sim}(d_i, d_j) \right]$$

- $\lambda = 1.0$: Pure Top-K relevance (high redundancy).
- $\lambda = 0.5$: Balanced relevance and topic diversity.
- $\lambda = 0.0$: Maximum diversity across distinct pages.

#### 3. Hybrid Search (Dense + Sparse / BM25)
- **Dense Vectors (Embeddings)**: High semantic recall (`"worker leaves"` $\to$ `"separated employee"`).
- **Sparse Vectors (BM25 / Keyword)**: High lexical precision for exact acronyms, error codes, SKUs, and standard numbers (`"AUD-STD-2026-V4"`).
- **Reciprocal Rank Fusion (RRF)**: Combines rankings without needing normalized score calibration:
  $$\text{RRF\_Score}(d) = \sum_{m \in M} \frac{1}{60 + r_m(d)}$$

#### 4. Two-Stage Retrieval with Cross-Encoder Re-Ranking
- **Stage 1 (Bi-Encoder Retriever)**: Quickly scans 100,000 chunks via dot products to retrieve candidate top-50.
- **Stage 2 (Cross-Encoder Re-Ranker)**: Evaluates full cross-attention over $(q, \text{chunk})$ pairs on the top-50 to re-order the true top-5 with pinpoint accuracy.

---

### 1.7 Advanced RAG Paradigms
- **Query Rewriting / Expansion**: LLM rewrites colloquial queries into formal technical search variants.
- **HyDE (Hypothetical Document Embeddings)**: LLM hallucinates a hypothetical ideal answer first; the hypothetical answer is embedded to retrieve actual documents.
- **GraphRAG**: Extracts knowledge graphs (Entities, Relations, Claims) from documents. Enables multi-hop inductive reasoning across separate documents.
- **Agentic RAG**: An autonomous agent plans retrieval, routes across multiple indexes, evaluates whether retrieved context is sufficient, and re-queries dynamically if gaps exist.

---

### 1.8 Document Parsing: PDFs, Tables & OCR
- **PDF Challenges**: PDFs are visual layout languages (drawing commands), not text streams. Multi-column text often interleaves lines incorrectly if parsed naively.
- **Tables**: Spatial grids lose meaning when flattened to text. Best practice: convert tables to structured Markdown or HTML tables during parsing.
- **Scanned Documents**: Requires Optical Character Recognition (OCR) engines (Tesseract, Google Cloud Document AI, AWS Textract).

---

### 1.9 Evaluation & The RAG Triad (RAGAS Framework)
Evaluating RAG systems requires testing three independent dimensions:

```
          [User Query]
           /        \
  Answer Relevance   Context Relevance
         /            \
        ▼              ▼
   [LLM Answer] ◄──── [Retrieved Context]
           Faithfulness (Groundedness)
```

1. **Context Relevance**: Did the retriever fetch chunks actually relevant to the query?
2. **Faithfulness / Groundedness**: Is every statement in the generated answer strictly derived from the context (0% hallucination)?
3. **Answer Relevance**: Did the generated answer directly address the user's question without rambling?

---

### 1.10 Enterprise Access Control (RBAC) & Data Privacy
- **Document-Level Security (DLS)**: In enterprise RAG, users must never see chunks from documents they lack permission to read (e.g., Executive Payroll).
- **Pre-Filtering by ACL**: The user's Active Directory / RBAC groups are injected into the vector query filter (`filter={"department": {"$in": user_groups}}`), ensuring unauthorized vectors are never evaluated during nearest-neighbor search.

---

### 1.11 Strategic Decision Matrix: RAG vs. Fine-Tuning vs. Long Context

| Dimension | RAG | Fine-Tuning | Long Context Window (1M+ Tokens) |
| :--- | :--- | :--- | :--- |
| **Primary Purpose** | Inject dynamic factual knowledge & proprietary documents. | Teach style, tone, format, domain jargon, or specialized tasks. | One-off reasoning over massive unified inputs (entire codebases, whole books). |
| **Knowledge Freshness** | **Real-time (instant update upon indexing)**. | Static (frozen at training time). | Real-time (injected directly in prompt). |
| **Hallucination Risk** | **Extremely Low** (strictly grounded with citations). | Moderate to High (models can fabricate facts confidently). | Low (grounded in prompt, but subject to "Lost in the Middle"). |
| **Setup & Maintenance Cost** | Low to Moderate (Vector DB + Embedding API). | High (GPU clusters, dataset curation, compute runs). | High per-inference token cost ($3–$10 per large call). |
| **Auditability & Citations** | **Yes (exact file, page, and chunk provenance)**. | No (weights are a black box; no citations). | Partial (citations possible, but noisy over 1M tokens). |

---

## 2. Project Architecture & Quickstart

```
block-b-rag-mastery/
│
├── data/
│   ├── generate_audit_pdf.py               # Generates the multi-page Audit Standard PDF
│   └── iso27001_soc2_audit_standard.pdf    # 4-page realistic enterprise compliance standard
│
├── .env                                    # Pre-configured with active GEMINI_API_KEY
├── requirements.txt                        # Production dependencies
├── config.py                               # LangChain embeddings & Gemini LLM initializer
├── vector_indexer.py                       # Shared indexing & embedding logic
│
├── 01_load_and_chunk.py                    # Practice 1: Document Loading & Overlap Chunking
├── 02_vector_store_indexing.py             # Practice 2: Embedding Generation & Vector Search
├── 03_rag_pipeline_with_citations.py       # Practice 3: End-to-End RAG with Inline Citations
├── 04_advanced_retrieval_techniques.py     # Practice 4: MMR, Multi-Query & Re-Ranking
│
├── main.py                                 # Interactive CLI navigator (Options 1–6)
├── test_project.py                         # Automated verification test suite
└── README.md                               # Comprehensive Block B reference guide
```

### Quickstart

1. **Navigate to the project directory**:
   ```powershell
   cd block-b-rag-mastery
   ```

2. **Run the interactive menu**:
   ```powershell
   python main.py
   ```

3. **Or run the entire pipeline end-to-end**:
   ```powershell
   python main.py --all
   ```

4. **Ask your own custom audit questions**:
   ```powershell
   python main.py
   # Select option 6: Interactive Auditor Query Mode
   ```

5. **Run automated unit tests**:
   ```powershell
   python -m unittest test_project.py
   ```

---

## 3. Practice Walkthrough & Code Modules

### 3.1 Module 1: Document Ingestion & Chunking
[01_load_and_chunk.py](./01_load_and_chunk.py) demonstrates:
- Extracting raw text and metadata across all 4 PDF pages with `PyPDFLoader`.
- Comparing naive character splitting with `RecursiveCharacterTextSplitter`.
- Configuring `chunk_size=400` with `chunk_overlap=80` to preserve context across boundaries.

### 3.2 Module 2: Vector Store Indexing & Similarity Search
[02_vector_store_indexing.py](./02_vector_store_indexing.py) demonstrates:
- Generating 3072-dimensional embeddings via `models/gemini-embedding-001`.
- Performing Top-K similarity search and inspecting cosine relevance scores.
- Applying metadata filtering to constrain retrieval strictly to specific pages.

### 3.3 Module 3: End-to-End RAG Pipeline with Citations
[03_rag_pipeline_with_citations.py](./03_rag_pipeline_with_citations.py) demonstrates:
- Constructing an LCEL (LangChain Expression Language) prompt chain with strict auditor constraints.
- Producing grounded answers with mandatory inline page citations: `[Page X]`.
- Enforcing refusal when asked about policies not present in the document.
- Printing a complete verified source audit trail showing exact chunk excerpts.

### 3.4 Module 4: Advanced Retrieval Techniques
[04_advanced_retrieval_techniques.py](./04_advanced_retrieval_techniques.py) demonstrates:
- Maximal Marginal Relevance (MMR) vs. Top-K search.
- Multi-Query Expansion via LLM query rewriting.
- Production architectures: Hybrid BM25 search, Cross-Encoder re-ranking, and GraphRAG.

---

## 4. Verification & Automated Tests

Run the test suite:
```powershell
python -m unittest test_project.py
```

Expected output:
```
Ran 4 tests in ~10.5s
OK
```
Verifies PDF existence, 4-page parsing, chunk metadata preservation, vector retrieval accuracy, and grounded RAG answer generation with page citations.
