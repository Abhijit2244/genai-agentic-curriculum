# Block A: LLM Fundamentals & Agentic Building Blocks

> **Curriculum Module**: LLMs, RAG, Agentic AI, MCP (The Most Important Day)  
> **Topic**: Block A: LLM Fundamentals (1.5 Hours Intensive)  
> **SDK**: Modern Google GenAI Python SDK (`google-genai` / Gemini 3.5 Series)  
> **Location**: `C:\Users\COM\Desktop\sample\block-a-llm-fundamentals`

---

## 📑 Table of Contents
1. [Core Theoretical Foundations](#1-core-theoretical-foundations)
   - What an LLM Is & How It Works
   - Tokens & Subword Tokenization
   - Context Window Dynamics
   - Hyperparameter Steering (Temperature & Top-p)
   - System vs. User Prompts
   - Prompt Engineering (Zero-Shot, Few-Shot, Chain-of-Thought)
   - Structured Outputs (JSON Schema & Pydantic)
   - Function / Tool Calling (The Foundation of Agents & MCP)
   - Embeddings & Semantic Vector Space
   - Hallucinations, Cost, Latency & Rate Limits
   - Architectural Comparison: Azure OpenAI vs. Direct OpenAI vs. Gemini API
2. [Project Architecture & Quickstart](#2-project-architecture--quickstart)
3. [Practice Walkthrough & Code Examples](#3-practice-walkthrough--code-examples)
4. [Verification & Automated Tests](#4-verification--automated-tests)

---

## 1. Core Theoretical Foundations

### 1.1 What an LLM Is
A **Large Language Model (LLM)** is a probabilistic autoregressive neural network (predominantly based on the Transformer decoder architecture) trained on massive textual corpora. Its fundamental mathematical objective during pretraining is **Causal Language Modeling**: predicting the next token $w_t$ given all preceding tokens:

$$\mathcal{L}_{LLM} = - \sum_{t=1}^{T} \log P(w_t \mid w_1, w_2, \dots, w_{t-1}; \theta)$$

- **Pretraining**: Unsupervised learning across trillions of tokens to learn grammar, world knowledge, reasoning patterns, and syntax.
- **Post-Training (Alignment)**: Supervised Fine-Tuning (SFT) and Reinforcement Learning from Human Feedback (RLHF / DPO) to turn a raw text completer into an instruction-following assistant.

---

### 1.2 Tokens & Subword Tokenization
LLMs do not process characters or strings directly; they process discrete integer IDs called **tokens**.
- Tokenizers use algorithms such as **Byte-Pair Encoding (BPE)** or **SentencePiece** to segment text into frequent subwords.
- **Rule of Thumb**:
  - $1 \text{ token} \approx 4 \text{ characters}$ or $\approx 0.75 \text{ English words}$.
  - $1,000 \text{ words} \approx 1,333 \text{ tokens}$.
  - Punctuation, spaces, and code syntax are separate tokens.

---

### 1.3 Context Window
The **Context Window** represents the maximum memory capacity (in total tokens) an LLM can attend to during a single inference call.
- It encompasses **Prompt Tokens (Input)** $+$ **Completion Tokens (Output)**.
- If input exceeds the context window, inputs are truncated or rejected.
- **Attention Scaling**: Standard self-attention scales quadratically $\mathcal{O}(N^2)$ with sequence length $N$. Modern models leverage innovations like FlashAttention, RoPE (Rotary Position Embeddings), and linear-attention variants to support context windows from 128k up to 1M–2M tokens (e.g., Gemini 3.5 / 1.5).

---

### 1.4 Hyperparameter Steering: Temperature & Top-p
During generation, the model produces raw unbounded logits $z_i$ over its vocabulary $V$. These are converted into probabilities via the **Softmax with Temperature ($T$)**:

$$P(w_i) = \frac{\exp(z_i / T)}{\sum_{j \in V} \exp(z_j / T)}$$

| Parameter | Range | Mathematical Effect | Recommended Setting |
| :--- | :--- | :--- | :--- |
| **Temperature ($T$)** | $0.0 - 2.0$ | As $T \to 0$, the probability distribution sharpens toward a delta function (argmax / greedy decoding). As $T \to \infty$, distribution flattens toward uniform. | `0.0` for code, extraction, tool calling, JSON. `0.7 - 1.0` for creative writing. |
| **Top-p (Nucleus Sampling)** | $0.0 - 1.0$ | Selects the smallest subset of vocabulary $V^{(p)}$ whose cumulative probability meets or exceeds $p$: $\sum_{i \in V^{(p)}} P(w_i) \ge p$. | `0.9 - 0.95` for natural fluent generation. |

---

### 1.5 System vs. User Prompts
Modern instruction-tuned models partition incoming context into designated roles:
- **System Prompt (Instruction / Metaprompt)**: Invariant directives defining the agent's persona, operational boundaries, formatting restrictions, and safety constraints. It holds higher steering priority in attention layers.
- **User Prompt**: The dynamic query, instruction, or data payload submitted by the end user.

---

### 1.6 Prompt Engineering Paradigms
1. **Zero-Shot**: Asking the model to perform a task directly without giving examples.
2. **Few-Shot (In-Context Learning)**: Providing 2–5 exemplar `Input ➔ Output` pairs inside the prompt to anchor the expected schema, tone, or taxonomy.
3. **Chain-of-Thought (CoT)**: Instructing the model to produce step-by-step reasoning tokens before emitting the final answer. Generating intermediate reasoning tokens increases test-time compute, allowing the attention heads to perform multi-hop factual aggregation.

---

### 1.7 Structured Outputs (JSON Schema & Pydantic)
- **The Problem**: Prompting an LLM with `"Return only valid JSON"` often fails in production because models occasionally emit leading text, trailing explanations, or invalid quotes.
- **The Modern Solution**: **Constrained Decoding (Grammar-guided Sampling)**. The inference engine intercepts the token logits at each step, masking out any token that would violate the supplied JSON schema.
- By defining a **Pydantic `BaseModel`**, the schema is transmitted directly to the model via `response_schema`, producing guaranteed type-safe output that parses instantly into Python classes.

---

### 1.8 Function / Tool Calling (The Foundation of Agents & MCP)
LLMs are isolated neural weights frozen in time. They cannot browse the live web, run Python code, or query internal SQL databases. **Tool Calling** bridges this gap:

```
[User Query] ──> [LLM detects missing data] ──> [Emits Structured Tool Call: func(args)]
                                                                  │
                                                                  ▼
[LLM Synthesizes Final Answer] <── [Tool Result] <── [Local Runtime executes Python tool]
```

- **Foundation of Agents**: An AI Agent is simply an LLM wrapped in a loop that can iteratively decide which tools to call, inspect their outputs, and take subsequent actions until a goal is achieved.
- **Model Context Protocol (MCP)**: An open standard created to standardize how applications provide context and tools to LLMs across servers, IDEs, and local environments.

---

### 1.9 Embeddings & Vector Similarity
- An **Embedding Model** transforms a string of text into a dense fixed-dimension vector $\vec{v} \in \mathbb{R}^D$ (e.g., $D = 3072$).
- Words and passages with similar semantic meanings are projected close to each other in vector space.
- **Cosine Similarity**:
  $$\text{CosineSim}(\vec{u}, \vec{v}) = \frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\|_2 \|\vec{v}\|_2}$$
- **RAG Connection**: Embeddings are the bedrock of Retrieval-Augmented Generation (RAG). External documents are chunked and embedded into a Vector Database. When a user queries, the query is embedded, the closest document vectors are retrieved via similarity search, and they are passed into the LLM context.

---

### 1.10 Operational Realities: Hallucinations, Cost, Latency & Limits
- **Hallucinations**: Plausible-sounding falsehoods generated because LLMs optimize for next-token probability, not factual truth. Mitigated via low temperature, CoT, grounding tools, and RAG.
- **Cost Structure**: Priced per 1 Million tokens. Output tokens generally cost 3–4× more than input tokens due to sequential autoregressive generation compute.
- **Latency**:
  - **TTFT (Time to First Token)**: Time taken to process the entire input prompt (parallel matrix multiplication).
  - **ITL (Inter-Token Latency)**: Time per generated token (memory bandwidth bound).
- **Rate Limits**:
  - **RPM**: Requests Per Minute
  - **TPM**: Tokens Per Minute
  - **RPD**: Requests Per Day

---

### 1.11 Architectural Comparison: Azure OpenAI vs. OpenAI API vs. Gemini API

| Dimension | OpenAI API | Azure OpenAI Service | Gemini API (Google Cloud / AI Studio) |
| :--- | :--- | :--- | :--- |
| **Target Audience** | Rapid prototyping, startups, individual developers. | Regulated enterprise, Fortune 500, healthcare/fintech. | Developers & Enterprises needing massive context & multimodal AI. |
| **Infrastructure & Security** | Public cloud infrastructure hosted by OpenAI. | Hosted within customer's private Azure tenant; Virtual Network (VNet) peering, Private Endpoints. | Hosted on Google Cloud with native Vertex AI integration and global private backbone. |
| **Data Privacy & SLAs** | Standard zero-data-retention (ZDR) available via enterprise tier. | Enterprise HIPAA, SOC2, FedRAMP, GDPR compliance; customer data never trains foundation models. | Strict enterprise privacy; data isolation via Vertex AI; zero training on enterprise payloads. |
| **Context & Multimodality** | 128k tokens; vision, audio, text. | Matches OpenAI releases with enterprise deployment ring lag. | **Industry-leading 1M–2M context window**; native multimodal processing across video, audio, code, and text. |

---

## 2. Project Architecture & Quickstart

```
block-a-llm-fundamentals/
│
├── .env                     # API key configuration (pre-configured)
├── .env.example             # Template for API credentials
├── requirements.txt         # Minimal production dependencies
├── config.py                # Gemini client initializer & constants
│
├── 01_call_llm.py           # Practice 1: System/User Prompts, Temp, Tokens, CoT
├── 02_structured_json.py    # Practice 2: Pydantic & Schema-Enforced JSON
├── 03_tool_calling.py       # Practice 3: Python Tool / Function Calling Agent
├── 04_embeddings_demo.py    # Practice 4: Text Embeddings & Cosine Similarity
│
├── main.py                  # Interactive CLI navigator (options 1-5)
├── test_project.py          # Automated verification test suite
└── README.md                # Comprehensive theoretical & practical guide
```

### Quickstart

1. **Navigate to the project directory**:
   ```powershell
   cd C:\Users\COM\Desktop\sample\block-a-llm-fundamentals
   ```

2. **Run the interactive navigator**:
   ```powershell
   python main.py
   ```

3. **Or run the entire pipeline at once**:
   ```powershell
   python main.py --all
   ```

4. **Run automated unit tests**:
   ```powershell
   python test_project.py
   ```

---

## 3. Practice Walkthrough & Code Examples

### 3.1 Script 1: Basic API Call with System Instruction & Temperature
[01_call_llm.py](file:///C:/Users/COM/Desktop/sample/block-a-llm-fundamentals/01_call_llm.py) demonstrates:
- Specifying `system_instruction` to constrain tone and format.
- Configuring `temperature=0.2` and `top_p=0.95`.
- Reading `usage_metadata` (`prompt_token_count`, `candidates_token_count`, `total_token_count`).
- Eliciting step-by-step reasoning via **Chain-of-Thought (CoT)**.

### 3.2 Script 2: Structured JSON Output via Pydantic
[02_structured_json.py](file:///C:/Users/COM/Desktop/sample/block-a-llm-fundamentals/02_structured_json.py) demonstrates:
- Declaring a Pydantic schema `TechConceptAnalysis`.
- Supplying `response_schema=TechConceptAnalysis` and `response_mime_type="application/json"`.
- Validating the output using `TechConceptAnalysis.model_validate_json(response.text)`.

### 3.3 Script 3: Tool / Function Calling (Agent Foundation)
[03_tool_calling.py](file:///C:/Users/COM/Desktop/sample/block-a-llm-fundamentals/03_tool_calling.py) demonstrates:
- Defining a Python function `get_service_health(service_name, region)`.
- Registering the function in `types.GenerateContentConfig(tools=[get_service_health])`.
- Watching the LLM recognize the missing factual context, invoke the local Python function, and produce a grounded response.

### 3.4 Script 4: Embeddings & Vector Cosine Similarity
[04_embeddings_demo.py](file:///C:/Users/COM/Desktop/sample/block-a-llm-fundamentals/04_embeddings_demo.py) demonstrates:
- Generating 3072-dimensional dense embeddings with `gemini-embedding-001`.
- Computing cosine similarity between related vs. unrelated concepts.

---

## 4. Verification & Automated Tests

All modules include assertions and automated unit tests. Run:
```powershell
python test_project.py
```
Expected output:
```
Ran 4 tests in ~7.8s
OK
```
