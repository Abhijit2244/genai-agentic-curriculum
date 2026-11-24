"""
Configuration and LLM Setup for Block C: LangChain & LangGraph Mastery
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

BASE_DIR = Path(__file__).parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not API_KEY or API_KEY == "your_gemini_api_key_here":
    print("ERROR: GEMINI_API_KEY is not set in your .env file!")
    print(f"Please set your API key in {ENV_PATH}")
    sys.exit(1)

os.environ["GOOGLE_API_KEY"] = API_KEY
LLM_MODEL = "gemini-3.5-flash-lite"


def get_llm(temperature: float = 0.0) -> ChatGoogleGenerativeAI:
    """Returns an authenticated ChatGoogleGenerativeAI instance."""
    return ChatGoogleGenerativeAI(
        model=LLM_MODEL,
        temperature=temperature,
        google_api_key=API_KEY
    )
