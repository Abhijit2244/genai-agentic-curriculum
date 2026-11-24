"""
Configuration and Embeddings/LLM Initialization for Block B: RAG
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI

BASE_DIR = Path(__file__).parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY or API_KEY == "your_gemini_api_key_here":
    print("ERROR: GEMINI_API_KEY is not set in your .env file!")
    print(f"Please set your API key in {ENV_PATH}")
    sys.exit(1)

# Ensure Gemini API key is also available as GOOGLE_API_KEY for LangChain integrations
os.environ["GOOGLE_API_KEY"] = API_KEY

PDF_PATH = BASE_DIR / "data" / "iso27001_soc2_audit_standard.pdf"

EMBEDDING_MODEL_NAME = "models/gemini-embedding-001"
LLM_MODEL_NAME = "gemini-3.5-flash-lite"


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """Returns Google GenAI embeddings instance."""
    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL_NAME,
        google_api_key=API_KEY
    )


def get_llm(temperature: float = 0.0) -> ChatGoogleGenerativeAI:
    """Returns ChatGoogleGenerativeAI model instance."""
    return ChatGoogleGenerativeAI(
        model=LLM_MODEL_NAME,
        temperature=temperature,
        google_api_key=API_KEY
    )
