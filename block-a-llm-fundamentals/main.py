"""
=============================================================================
Block A: LLM Fundamentals - Interactive Mastery Navigator
=============================================================================
Practice: Call an LLM API from Python, get structured JSON back, and use one tool call.
=============================================================================
"""

import sys
from importlib import import_module


def banner():
    print("""
=============================================================================
  🌟 BLOCK A: LLM FUNDAMENTALS & AGENTIC BUILDING BLOCKS 🌟
  Google Gemini API Mastery Practice Project
=============================================================================
  Topics Covered:
  [1] LLM API Call, System Prompts, Temperature, Tokens & CoT Reasoning
  [2] Structured JSON Outputs with Pydantic & Strict Schema Enforcement
  [3] Function / Tool Calling (The Core Primitive for Agents & MCP)
  [4] Text Embeddings & Cosine Similarity (Text -> Vectors for RAG)
=============================================================================
""")


def menu():
    print("Select an option:")
    print("  1. Run Demo 1: Basic LLM Call (System/User, Temperature, Tokens, CoT)")
    print("  2. Run Demo 2: Structured JSON Output with Pydantic")
    print("  3. Run Demo 3: Function / Tool Calling (Agent Foundation)")
    print("  4. Run Demo 4: Text Embeddings & Cosine Similarity")
    print("  5. Run ALL Demos Sequentially")
    print("  0. Exit")
    print("-" * 65)


def run_all():
    print("\n>>> EXECUTING FULL BLOCK A PRACTICE PIPELINE <<<\n")
    
    print("\n" + "#" * 65)
    print("# STEP 1: Basic LLM API Call & Hyperparameters")
    print("#" * 65)
    mod1 = import_module("01_call_llm")
    mod1.run_basic_call_demo()
    mod1.run_prompt_engineering_demo()

    print("\n" + "#" * 65)
    print("# STEP 2: Structured JSON Output via Pydantic Schema")
    print("#" * 65)
    mod2 = import_module("02_structured_json")
    mod2.run_structured_output_demo()

    print("\n" + "#" * 65)
    print("# STEP 3: Function / Tool Calling (Agent Foundation)")
    print("#" * 65)
    mod3 = import_module("03_tool_calling")
    mod3.run_tool_calling_demo()

    print("\n" + "#" * 65)
    print("# STEP 4: Text Embeddings & Vector Cosine Similarity")
    print("#" * 65)
    mod4 = import_module("04_embeddings_demo")
    mod4.run_embeddings_demo()

    print("\n" + "=" * 65)
    print("🎉 ALL BLOCK A PRACTICE MODULES EXECUTED SUCCESSFULLY!")
    print("=" * 65 + "\n")


def main():
    banner()
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        run_all()
        return

    while True:
        menu()
        choice = input("Enter choice (0-5): ").strip()
        if choice == "1":
            mod1 = import_module("01_call_llm")
            mod1.run_basic_call_demo()
            mod1.run_prompt_engineering_demo()
        elif choice == "2":
            mod2 = import_module("02_structured_json")
            mod2.run_structured_output_demo()
        elif choice == "3":
            mod3 = import_module("03_tool_calling")
            mod3.run_tool_calling_demo()
        elif choice == "4":
            mod4 = import_module("04_embeddings_demo")
            mod4.run_embeddings_demo()
        elif choice == "5":
            run_all()
        elif choice == "0":
            print("Exiting. Happy learning!")
            break
        else:
            print("Invalid choice, please select between 0 and 5.\n")


if __name__ == "__main__":
    main()
