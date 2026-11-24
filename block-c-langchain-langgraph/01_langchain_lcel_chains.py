"""
=============================================================================
01_langchain_lcel_chains.py: LangChain Expression Language (LCEL) & Composability
=============================================================================
Core Concepts Demonstrated:
1. LCEL Mechanics: Using the pipe operator `|` to chain Prompts, LLMs, and Parsers.
2. Prompt Templating: Dynamic variable interpolation and System/Human message roles.
3. Structured Output Binding: Enforcing Pydantic schemas via `.with_structured_output()`.
4. Parallel Execution: Using `RunnableParallel` to evaluate multiple perspectives simultaneously.
=============================================================================
"""

import warnings
warnings.filterwarnings("ignore")

from typing import List
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from config import get_llm


# 1. Pydantic Schema for Structured Analysis
class IncidentAnalysis(BaseModel):
    root_cause: str = Field(description="One-sentence root cause explanation")
    impact_severity: str = Field(description="Low, Medium, High, or Critical")
    remediation_steps: List[str] = Field(description="2-3 recommended technical action items")
    preventative_controls: List[str] = Field(description="Long-term defensive guardrails")


def run_basic_lcel_demo():
    print("\n" + "=" * 65)
    print("STEP 1: Basic LCEL Chain (Prompt | LLM | StrOutputParser)")
    print("=" * 65)

    llm = get_llm(temperature=0.0)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert Cloud Architect. Explain concepts in 2 crisp bullet points."),
        ("human", "What is the difference between a linear chain and a cyclical state graph?"),
    ])

    # LCEL pipeline composition
    chain = prompt | llm | StrOutputParser()

    result = chain.invoke({})
    print("[Chain Output]:\n" + result.strip())
    print("-" * 65)


def run_structured_output_chain_demo():
    print("\n" + "=" * 65)
    print("STEP 2: Structured Output Binding (LLM.with_structured_output)")
    print("=" * 65)

    llm = get_llm(temperature=0.0)

    # Bind the Pydantic schema directly to the model
    structured_llm = llm.with_structured_output(IncidentAnalysis)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Lead Site Reliability Engineer analyzing a production post-mortem."),
        ("human", "Analyze this telemetry: 'Database memory utilization hit 99.4%, causing connection pool exhaustion and 504 gateway timeouts on the payment API.'"),
    ])

    chain = prompt | structured_llm
    analysis: IncidentAnalysis = chain.invoke({})

    print(f"--> Parsed Class: {type(analysis).__name__}")
    print(f"--> Root Cause  : {analysis.root_cause}")
    print(f"--> Severity    : {analysis.impact_severity}")
    print("--> Remediation Steps:")
    for step in analysis.remediation_steps:
        print(f"      • {step}")
    print("--> Preventative Controls:")
    for ctrl in analysis.preventative_controls:
        print(f"      • {ctrl}")
    print("-" * 65)
    return analysis


def run_parallel_chain_demo():
    print("\n" + "=" * 65)
    print("STEP 3: RunnableParallel Multi-Perspective Evaluation")
    print("=" * 65)

    llm = get_llm(temperature=0.0)

    optimist_prompt = ChatPromptTemplate.from_template(
        "Summarize the positive engineering advantages of using LangGraph for multi-agent workflows in 1 sentence. Feature: {feature}"
    )
    risk_prompt = ChatPromptTemplate.from_template(
        "Identify the primary architectural complexity risk of using LangGraph for stateful workflows in 1 sentence. Feature: {feature}"
    )

    # Execute two chains simultaneously on the same input
    parallel_chain = RunnableParallel({
        "advantages": optimist_prompt | llm | StrOutputParser(),
        "risks": risk_prompt | llm | StrOutputParser(),
    })

    results = parallel_chain.invoke({"feature": "Stateful cyclical graphs with human-in-the-loop checkpoints"})

    print("[Optimist View]:\n  " + results["advantages"].strip())
    print("\n[Risk Officer View]:\n  " + results["risks"].strip())
    print("=" * 65)


def run_all_lcel_demos():
    run_basic_lcel_demo()
    run_structured_output_chain_demo()
    run_parallel_chain_demo()


if __name__ == "__main__":
    run_all_lcel_demos()
