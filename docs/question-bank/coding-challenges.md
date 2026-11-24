# Practical AI Engineering Coding Challenges

> **Objective:** Hands-on implementation challenges testing practical AI engineering, algorithm design, vector mathematics, state machine construction, and protocol development.  
> **Difficulty Levels:** Level 1 (Easy), Level 2 (Medium), Level 3 (Hard), Level 4 (Expert).  
> **Languages Provided:** Python 3.11+ and TypeScript / Node.js (with C#/.NET equivalents).

---

## 🟢 Challenge 1 (Easy): Token Budget Estimator & Cost Calculator

### Problem Statement
In production AI gateways, applications must verify that incoming request batches do not exceed maximum context budgets and calculate estimated costs before dispatching inference requests to cloud LLM providers.

Write a function `calculate_batch_token_budget` that takes a list of input prompts, a target model name, and an expected completion length. The function must:
1. Estimate token counts for each prompt using the standard BPE heuristic ($1\text{ token} \approx 4\text{ characters}$, with a minimum of 1 token per non-empty string).
2. Validate whether any individual prompt + completion exceeds the model's context window.
3. Compute the total estimated cost in USD based on provider price cards.

### Pricing & Limits Card
- **`gemini-2.5-flash`**: Context limit = 1,000,000 tokens; Input = \$0.075 / 1M tokens; Output = \$0.30 / 1M tokens.
- **`gpt-4o`**: Context limit = 128,000 tokens; Input = \$2.50 / 1M tokens; Output = \$10.00 / 1M tokens.

### Function Signature & Constraints
* Prompts list length: $1 \le N \le 1,000$.
* Expected completion tokens: $1 \le T_{\text{out}} \le 4,096$.

---

### Reference Solution (Python)
```python
from dataclasses import dataclass

@dataclass
class BudgetReport:
    total_prompt_tokens: int
    total_completion_tokens: int
    total_tokens: int
    total_cost_usd: float
    exceeded_prompts: list[int]  # Indices of prompts exceeding context limits

MODEL_CONFIGS = {
    "gemini-2.5-flash": {"limit": 1_000_000, "in_cost": 0.075 / 1_000_000, "out_cost": 0.30 / 1_000_000},
    "gpt-4o": {"limit": 128_000, "in_cost": 2.50 / 1_000_000, "out_cost": 10.00 / 1_000_000}
}

def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    # Heuristic: 4 characters per token, rounded up
    return max(1, (len(text) + 3) // 4)

def calculate_batch_token_budget(prompts: list[str], model: str, expected_out_tokens: int) -> BudgetReport:
    if model not in MODEL_CONFIGS:
        raise ValueError(f"Unsupported model: {model}")
        
    cfg = MODEL_CONFIGS[model]
    total_in = 0
    exceeded = []
    
    for idx, p in enumerate(prompts):
        tokens = estimate_tokens(p)
        total_in += tokens
        if tokens + expected_out_tokens > cfg["limit"]:
            exceeded.append(idx)
            
    total_out = len(prompts) * expected_out_tokens
    total_cost = (total_in * cfg["in_cost"]) + (total_out * cfg["out_cost"])
    
    return BudgetReport(
        total_prompt_tokens=total_in,
        total_completion_tokens=total_out,
        total_tokens=total_in + total_out,
        total_cost_usd=round(total_cost, 6),
        exceeded_prompts=exceeded
    )
```

---

## 🟢 Challenge 2 (Easy): Self-Healing Structured JSON Schema Validator

### Problem Statement
LLMs frequently return markdown wrappers (````json\n...\n```) or slight syntax violations when asked for structured JSON.

Write a function `parse_and_validate_invoice` that takes a raw LLM string output, sanitizes markdown wrappers, parses the JSON payload, and validates it against a typed schema. If validation fails on non-fatal syntax (e.g., missing closing brace), use auto-repair heuristics before throwing an exception.

---

### Reference Solution (TypeScript with Zod)
```typescript
import { z } from "zod";

export const InvoiceSchema = z.object({
  invoiceNumber: z.string(),
  vendor: z.string(),
  amount: z.number().positive(),
  date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Must be YYYY-MM-DD")
});

export type Invoice = z.infer<typeof InvoiceSchema>;

export function sanitizeAndParseJson(raw: string): any {
  // 1. Strip markdown code fences if present
  let clean = raw.trim();
  if (clean.startsWith("```json")) {
    clean = clean.replace(/^```json\s*/, "").replace(/\s*```$/, "");
  } else if (clean.startsWith("```")) {
    clean = clean.replace(/^```\s*/, "").replace(/\s*```$/, "");
  }

  // 2. Parse JSON safely
  try {
    return JSON.parse(clean);
  } catch (err) {
    // Basic auto-repair: append missing closing brace if truncated
    if (clean.startsWith("{") && !clean.endsWith("}")) {
      return JSON.parse(clean + "}");
    }
    throw new Error(`Invalid JSON syntax: ${err}`);
  }
}

export function parseAndValidateInvoice(rawResponse: string): Invoice {
  const jsonPayload = sanitizeAndParseJson(rawResponse);
  return InvoiceSchema.parse(jsonPayload);
}
```

---

## 🟡 Challenge 3 (Medium): Reciprocal Rank Fusion (RRF) Hybrid Search Engine

### Problem Statement
Implement the core ranking fusion algorithm used in hybrid search engines to merge a list of dense vector search results with a list of sparse BM25 keyword search results.

Write a function `reciprocal_rank_fusion` that takes:
- `dense_results`: Ordered list of document IDs ranked by vector cosine similarity (Rank 1 is best).
- `sparse_results`: Ordered list of document IDs ranked by BM25 keyword frequency (Rank 1 is best).
- `k`: Smoothing constant (default 60).

The function must compute the RRF score for every unique document:
$$\text{RRF\_Score}(d) = \sum_{m \in \{\text{dense}, \text{sparse}\}} \frac{1}{k + \text{rank}_m(d)}$$
and return the documents sorted in descending order of their fused score.

---

### Reference Solution (Python & C#)

#### Python Implementation:
```python
from collections import defaultdict

def reciprocal_rank_fusion(dense_ranks: list[str], sparse_ranks: list[str], k: int = 60) -> list[tuple[str, float]]:
    """
    Computes reciprocal rank fusion across dense and sparse ranked lists.
    Ranks are 1-based (index 0 has rank 1).
    """
    scores = defaultdict(float)
    
    for rank, doc_id in enumerate(dense_ranks, start=1):
        scores[doc_id] += 1.0 / (k + rank)
        
    for rank, doc_id in enumerate(sparse_ranks, start=1):
        scores[doc_id] += 1.0 / (k + rank)
        
    return sorted(scores.items(), key=lambda item: item[1], reverse=True)

# Test execution:
if __name__ == "__main__":
    dense = ["doc_A", "doc_B", "doc_C", "doc_D"]
    sparse = ["doc_C", "doc_A", "doc_E", "doc_B"]
    fused = reciprocal_rank_fusion(dense, sparse, k=60)
    print("Fused Rankings:", fused)
    # doc_A and doc_C will top the rankings because they appear in both lists!
```

#### C# (.NET 8) Implementation:
```csharp
public static class HybridSearchFusion
{
    public static List<(string DocId, double Score)> ReciprocalRankFusion(
        IList<string> denseResults, 
        IList<string> sparseResults, 
        int k = 60)
    {
        var scores = new Dictionary<string, double>();

        for (int rank = 1; rank <= denseResults.Count; rank++)
        {
            var id = denseResults[rank - 1];
            scores[id] = scores.GetValueOrDefault(id, 0.0) + (1.0 / (k + rank));
        }

        for (int rank = 1; rank <= sparseResults.Count; rank++)
        {
            var id = sparseResults[rank - 1];
            scores[id] = scores.GetValueOrDefault(id, 0.0) + (1.0 / (k + rank));
        }

        return scores
            .Select(pair => (DocId: pair.Key, Score: pair.Value))
            .OrderByDescending(x => x.Score)
            .ToList();
    }
}
```

---

## 🟡 Challenge 4 (Medium): Maximal Marginal Relevance (MMR) Diversity Ranker

### Problem Statement
In vector retrieval, the top 5 closest vectors often contain redundant copies of the same information.

Implement a function `maximal_marginal_relevance` that takes:
- `query_embedding`: 1D float array representing query vector.
- `doc_embeddings`: 2D float array where each row represents a candidate document vector.
- `top_k`: Number of diverse documents to select.
- `lambda_param`: Float $\in [0, 1]$ balancing query relevance vs. diversity.

The algorithm must greedily select documents that maximize:
$$\text{MMR} = \arg\max_{d_i \in R \setminus S} \left[ \lambda \cdot \text{CosineSim}(d_i, q) - (1 - \lambda) \max_{d_j \in S} \text{CosineSim}(d_i, d_j) \right]$$

---

### Reference Solution (Python with NumPy)
```python
import numpy as np

def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9)

def maximal_marginal_relevance(
    query_vec: np.ndarray, 
    doc_vecs: list[np.ndarray], 
    top_k: int = 3, 
    lambda_param: float = 0.5
) -> list[int]:
    """
    Returns indices of selected diverse document vectors.
    """
    if len(doc_vecs) <= top_k:
        return list(range(len(doc_vecs)))

    # Compute similarity to query for all candidates
    query_similarities = [cosine_sim(query_vec, d) for d in doc_vecs]
    
    selected_indices = []
    unselected_indices = list(range(len(doc_vecs)))
    
    # 1. First selection: purely highest similarity to query
    first_choice = int(np.argmax(query_similarities))
    selected_indices.append(first_choice)
    unselected_indices.remove(first_choice)
    
    # 2. Iteratively pick next best balancing relevance and redundancy
    while len(selected_indices) < top_k and unselected_indices:
        best_score = -float("inf")
        best_idx = None
        
        for cand_idx in unselected_indices:
            relevance = query_similarities[cand_idx]
            redundancy = max([cosine_sim(doc_vecs[cand_idx], doc_vecs[s]) for s in selected_indices])
            mmr_score = (lambda_param * relevance) - ((1.0 - lambda_param) * redundancy)
            
            if mmr_score > best_score:
                best_score = mmr_score
                best_idx = cand_idx
                
        selected_indices.append(best_idx)
        unselected_indices.remove(best_idx)
        
    return selected_indices
```

---

## 🔴 Challenge 5 (Hard): Complete FastMCP Server with Tool Schema Validation

### Problem Statement
Build an enterprise Model Context Protocol (MCP) Server in Python using `mcp 2.x` `MCPServer` that exposes:
1. A tool `query_ledger_anomalies` validating vendor, amount, and lookback window.
2. A resource `audit://policies/sox404` returning compliance rules.
3. Proper logging directed to `sys.stderr` to prevent `stdout` protocol corruption.

---

### Reference Solution (Python)
```python
import sys
import logging
from pathlib import Path
from mcp.server.mcpserver import MCPServer

# Crucial: Configure logging strictly to stderr!
logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

server = MCPServer(
    name="EnterpriseLedgerMCPServer",
    version="1.0.0",
    description="Exposes general ledger scanning tools and SOX compliance resources"
)

@server.tool(
    name="query_ledger_anomalies",
    description="Scans general ledger records for duplicate submissions and structuring near thresholds"
)
def query_ledger_anomalies(vendor: str, amount: float, lookback_days: int = 90) -> dict:
    logging.info(f"Scanning ledger for vendor '{vendor}' amount ${amount:,.2f} over {lookback_days} days.")
    
    # Validation
    if amount <= 0:
        return {"isError": True, "error": "Amount must be positive."}
        
    # Simulated forensic check
    if amount >= 48000.0 and amount < 50000.0:
        return {
            "status": "FLAGGED",
            "violation": "AP-STRUCT-02",
            "risk": "HIGH",
            "detail": f"Amount ${amount:,.2f} structures just beneath the $50k dual-authorization threshold."
        }
        
    return {"status": "CLEAN", "violation": None, "risk": "LOW"}

@server.resource(
    uri="audit://policies/sox404",
    name="SOX 404 AP Accounting Standard",
    mime_type="text/markdown"
)
def get_sox_policy() -> str:
    return "# SOX 404 INTERNAL CONTROLS\nRule AP-STRUCT-02: Splitting disbursements to evade approval is prohibited."

if __name__ == "__main__":
    logging.info("Starting MCP Server over stdio transport...")
    server.run(transport="stdio")
```

---

## 🔴 Challenge 6 (Hard): LangGraph State Machine with Cycle Detection Circuit Breaker

### Problem Statement
Construct a complete LangGraph agent state machine using `StateGraph` that:
1. Queries an external mock tool.
2. Tracks how many times the same tool has been called with identical arguments.
3. If the tool fails or repeats $\ge 3$ times, triggers a circuit breaker edge that halts autonomous loops and transitions to a `human_fallback` node.

---

### Reference Solution (Python with LangGraph)
```python
import operator
import hashlib
import json
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, ToolMessage

class AgentLoopState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    call_history_hashes: Annotated[list[str], operator.add]
    circuit_broken: bool

def mock_llm_node(state: AgentLoopState):
    # Simulates an LLM repeatedly emitting a failing tool call
    tool_call = {
        "name": "fetch_stock_price",
        "args": {"ticker": "INVALID_CO"},
        "id": "call_1"
    }
    return {
        "messages": [AIMessage(content="", tool_calls=[tool_call])],
        "call_history_hashes": [hashlib.md5(json.dumps(tool_call).encode()).hexdigest()]
    }

def mock_tool_node(state: AgentLoopState):
    # Simulates a tool failing
    return {
        "messages": [ToolMessage(tool_call_id="call_1", content="Error: Ticker not found.")]
    }

def human_fallback_node(state: AgentLoopState):
    return {
        "circuit_broken": True,
        "messages": [HumanMessage(content="CIRCUIT_BREAKER_TRIGGERED: Repeated tool failure escalated to human operator.")]
    }

def loop_detector_router(state: AgentLoopState) -> str:
    hashes = state["call_history_hashes"]
    # Check if the latest tool hash has appeared 3 or more times:
    if hashes and hashes.count(hashes[-1]) >= 3:
        return "human_fallback"
        
    last_msg = state["messages"][-1]
    if isinstance(last_msg, AIMessage) and last_msg.tool_calls:
        return "tool_node"
    return END

# Build Graph
workflow = StateGraph(AgentLoopState)
workflow.add_node("llm_node", mock_llm_node)
workflow.add_node("tool_node", mock_tool_node)
workflow.add_node("human_fallback", human_fallback_node)

workflow.add_edge(START, "llm_node")
workflow.add_conditional_edges("llm_node", loop_detector_router, ["tool_node", "human_fallback", END])
workflow.add_edge("tool_node", "llm_node")
workflow.add_edge("human_fallback", END)

app = workflow.compile()
```

---

## 🟣 Challenge 7 (Expert): Asynchronous Human-in-the-Loop Webhook Service with SSE Generator

### Problem Statement
Design an asynchronous FastAPI backend service that:
1. Ingests an audit job, initializes a LangGraph workflow with `interrupt_before=["human_approval"]`, and runs it in the background.
2. Streams real-time progress to a web UI using Server-Sent Events (`text/event-stream`).
3. Pauses execution at the breakpoint and serves an approval endpoint (`POST /api/audit/approve/{job_id}`).
4. Resumes execution with auditor notes and delivers the final report over the existing thread.

---

### Reference Solution (Python with FastAPI & LangGraph)
```python
import asyncio
import uuid
import json
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langgraph.checkpoint.memory import MemorySaver

app = FastAPI(title="HITL Audit Service")
checkpointer = MemorySaver()

# In-memory session registry (In production: Redis / PostgreSQL)
JOB_REGISTRY = {}

class ApprovalPayload(BaseModel):
    approved: bool
    notes: str

# (Assume workflow is compiled with checkpointer and interrupt_before=["human_approval"])
# from agent.audit_graph import build_audit_workflow
# compiled_workflow = build_audit_workflow(checkpointer=checkpointer)

@app.post("/api/audit/start")
async def start_audit_job(background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    event_queue = asyncio.Queue()
    
    JOB_REGISTRY[job_id] = {
        "queue": event_queue,
        "status": "RUNNING"
    }
    
    config = {"configurable": {"thread_id": job_id}}
    
    async def run_agent():
        await event_queue.put({"step": "STARTED"})
        # 1. Run until breakpoint:
        # compiled_workflow.invoke(initial_state, config=config)
        await asyncio.sleep(1) # Simulate OCR & Ledger execution
        await event_queue.put({"step": "AWAITING_HUMAN_APPROVAL", "job_id": job_id})
        JOB_REGISTRY[job_id]["status"] = "AWAITING_APPROVAL"
        
    background_tasks.add_task(run_agent)
    return {"job_id": job_id, "status": "started"}

@app.get("/api/audit/events/{job_id}")
async def stream_events(job_id: str):
    if job_id not in JOB_REGISTRY:
        raise HTTPException(status_code=404, detail="Job not found")
        
    queue = JOB_REGISTRY[job_id]["queue"]
    
    async def sse_generator():
        while True:
            event = await queue.get()
            yield f"data: {json.dumps(event)}\n\n"
            if event.get("step") in ["REPORT_READY", "ERROR"]:
                break
                
    return StreamingResponse(sse_generator(), media_type="text/event-stream")

@app.post("/api/audit/approve/{job_id}")
async def approve_audit_job(job_id: str, payload: ApprovalPayload):
    if job_id not in JOB_REGISTRY:
        raise HTTPException(status_code=404, detail="Job not found")
        
    config = {"configurable": {"thread_id": job_id}}
    queue = JOB_REGISTRY[job_id]["queue"]
    
    # 1. Update state with human feedback:
    # compiled_workflow.update_state(config, {"human_approved": payload.approved, "notes": payload.notes})
    
    # 2. Resume execution:
    # compiled_workflow.invoke(None, config=config)
    
    await queue.put({"step": "REPORT_READY", "notes": payload.notes, "status": "APPROVED"})
    JOB_REGISTRY[job_id]["status"] = "COMPLETED"
    
    return {"status": "resumed", "job_id": job_id}
```
