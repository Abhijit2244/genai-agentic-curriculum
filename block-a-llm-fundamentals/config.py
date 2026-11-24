"""
Configuration & Client Initialization for Block A: LLM Fundamentals
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from google import genai

# Load environment variables from .env
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY or API_KEY == "your_gemini_api_key_here":
    print("ERROR: GEMINI_API_KEY is not set in your .env file!")
    print("Please set your API key in C:\\Users\\COM\\Desktop\\sample\\block-a-llm-fundamentals\\.env")
    sys.exit(1)

# Default fast & capable model
DEFAULT_MODEL = "gemini-3.5-flash-lite"
EMBEDDING_MODEL = "gemini-embedding-001"

def get_gemini_client() -> genai.Client:
    """Returns an authenticated Gemini API client."""
    return genai.Client(api_key=API_KEY)
