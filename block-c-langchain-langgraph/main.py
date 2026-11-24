"""
=============================================================================
Block C: LangChain & LangGraph - Interactive Mastery Navigator
=============================================================================
Mastery Project for Stateful Agentic AI, ReAct Cycles, HITL & Multi-Agent Swarms
=============================================================================
"""

import sys
from importlib import import_module
from langchain_core.messages import HumanMessage


def banner():
    print("""
=============================================================================
  🌟 BLOCK C: LANGCHAIN & LANGGRAPH AGENTIC MASTERY 🌟
  Google Gemini 3.5 + Stateful Graph Architecture Practice Project
=============================================================================
  Topics Covered:
  [1] LangChain Expression Language (LCEL) & Structured Output Binding
  [2] Stateful ReAct Agent from Scratch using StateGraph (Cyclical Loops)
  [3] Checkpointing Memory (Thread Persistence) & Human-in-the-Loop (HITL)
  [4] Multi-Agent Collaboration: Supervisor Router Pattern with Specialists
=============================================================================
""")


def menu():
    print("Select an option:")
    print("  1. Run Demo 1: LangChain LCEL, Pydantic & Parallel Chains")
    print("  2. Run Demo 2: LangGraph ReAct Agent Loop from Scratch")
    print("  3. Run Demo 3: Memory Persistence & Human-in-the-Loop Approval")
    print("  4. Run Demo 4: Multi-Agent Collaboration (Supervisor Pattern)")
    print("  5. Run ALL Demos Sequentially")
    print("  6. Interactive ReAct Agent Console (Chat with the agent)")
    print("  0. Exit")
    print("-" * 65)


def run_all():
    print("\n>>> EXECUTING FULL LANGCHAIN & LANGGRAPH PRACTICE PIPELINE <<<\n")
    
    print("\n" + "#" * 65)
    print("# MODULE 1: LangChain LCEL & Structured Chains")
    print("#" * 65)
    mod1 = import_module("01_langchain_lcel_chains")
    mod1.run_all_lcel_demos()

    print("\n" + "#" * 65)
    print("# MODULE 2: LangGraph ReAct Agent Loop")
    print("#" * 65)
    mod2 = import_module("02_langgraph_react_agent")
    mod2.run_react_agent_demo()

    print("\n" + "#" * 65)
    print("# MODULE 3: Memory Persistence & Human-in-the-Loop Breakpoints")
    print("#" * 65)
    mod3 = import_module("03_memory_and_human_in_the_loop")
    mod3.run_all_memory_demos()

    print("\n" + "#" * 65)
    print("# MODULE 4: Multi-Agent Supervisor Orchestration")
    print("#" * 65)
    mod4 = import_module("04_multi_agent_supervisor")
    mod4.run_multi_agent_demo()

    print("\n" + "=" * 65)
    print("🎉 ALL LANGCHAIN & LANGGRAPH MODULES EXECUTED SUCCESSFULLY!")
    print("=" * 65 + "\n")


def interactive_agent_console():
    print("\n" + "=" * 65)
    print("INTERACTIVE LANGGRAPH REACT AGENT CONSOLE")
    print("Ask SLA, downtime, or cloud outage calculation questions.")
    print("Type 'exit' to return to the main menu.")
    print("=" * 65)

    mod2 = import_module("02_langgraph_react_agent")
    app = mod2.build_react_agent_graph()

    while True:
        user_input = input("\nEnter User Query: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["exit", "quit", "0"]:
            break
        
        print("\n[Agent Thinking & Executing Tools]...")
        res = app.invoke({"messages": [HumanMessage(content=user_input)]})
        print(f"\n[Agent Response]:\n{res['messages'][-1].content.strip()}\n")
        print("-" * 65)


def main():
    banner()
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        run_all()
        return

    while True:
        menu()
        choice = input("Enter choice (0-6): ").strip()
        if choice == "1":
            mod = import_module("01_langchain_lcel_chains")
            mod.run_all_lcel_demos()
        elif choice == "2":
            mod = import_module("02_langgraph_react_agent")
            mod.run_react_agent_demo()
        elif choice == "3":
            mod = import_module("03_memory_and_human_in_the_loop")
            mod.run_all_memory_demos()
        elif choice == "4":
            mod = import_module("04_multi_agent_supervisor")
            mod.run_multi_agent_demo()
        elif choice == "5":
            run_all()
        elif choice == "6":
            interactive_agent_console()
        elif choice == "0":
            print("Exiting. Happy building!")
            break
        else:
            print("Invalid choice, please select between 0 and 6.\n")


if __name__ == "__main__":
    main()
