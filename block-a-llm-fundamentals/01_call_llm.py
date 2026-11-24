"""
=============================================================================
01_call_llm.py: Basic LLM API Call with System Prompt, Temperature & Tokens
=============================================================================
Block A Core Concepts Demonstrated:
1. LLM API Invocation: Sending a request and receiving generated text.
2. System Prompt vs. User Prompt: Setting behavioral guardrails vs user inputs.
3. Temperature & Top-p: Controlling randomness / determinism.
4. Tokens & Context Window: Inspecting input, output, and total token usage.
5. Prompt Engineering: Zero-Shot, Few-Shot, and Chain-of-Thought (CoT).
=============================================================================
"""

from google.genai import types
from config import get_gemini_client, DEFAULT_MODEL

def run_basic_call_demo():
    print("\n" + "=" * 65)
    print("STEP 1: Call an LLM API with System & User Prompts")
    print("=" * 65)
    
    client = get_gemini_client()

    # System instruction defines the AI's persona, boundaries, and formatting rules
    system_instruction = (
        "You are an expert AI instructor. Explain complex concepts in concise, "
        "beginner-friendly terms using exactly 2 bullet points."
    )

    # User prompt is the dynamic task or question from the end user
    user_prompt = "What is a Context Window in an LLM?"

    print(f"[System Instruction]:\n  '{system_instruction}'")
    print(f"\n[User Prompt]:\n  '{user_prompt}'\n")

    # Call Gemini API with configuration parameters
    # Temperature 0.2: Lower randomness, high determinism and factual accuracy
    # Top-P 0.95: Nucleus sampling cutoff
    response = client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.2,
            top_p=0.95,
        ),
    )

    print("-" * 65)
    print("[LLM Response]:")
    print(response.text.strip())
    print("-" * 65)

    # Inspect token counts (Token economics, context consumption, cost tracking)
    if hasattr(response, "usage_metadata") and response.usage_metadata:
        usage = response.usage_metadata
        print("\n[Token & Cost Economics]:")
        print(f"  • Prompt (Input) Tokens    : {usage.prompt_token_count}")
        print(f"  • Candidate (Output) Tokens: {usage.candidates_token_count}")
        print(f"  • Total Tokens Consumed    : {usage.total_token_count}")
        print("  * Note: Pricing is calculated per 1M input and output tokens.")


def run_prompt_engineering_demo():
    print("\n" + "=" * 65)
    print("STEP 2: Prompt Engineering Paradigms (Chain-of-Thought)")
    print("=" * 65)

    client = get_gemini_client()

    # Chain-of-Thought (CoT) asks the model to break reasoning into steps
    # before reaching the final conclusion, reducing hallucinations.
    cot_prompt = """
Solve this word problem step-by-step:
A cloud cluster has 12 GPU nodes. 
- 4 nodes run training jobs consuming 800W each.
- 5 nodes run inference jobs consuming 350W each.
- The remaining nodes are idle consuming 50W each.
What is the total power consumption of the cluster?
Show your step-by-step reasoning, then state the final answer.
"""
    print("[Chain-of-Thought Prompt]:", cot_prompt.strip())

    response = client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=cot_prompt,
        config=types.GenerateContentConfig(
            temperature=0.0  # Greedy/deterministic for mathematical reasoning
        ),
    )

    print("\n[Model Reasoning Output]:")
    print(response.text.strip())
    print("=" * 65)


if __name__ == "__main__":
    run_basic_call_demo()
    run_prompt_engineering_demo()
