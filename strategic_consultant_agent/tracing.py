"""LangTrace tracing initialization.

CRITICAL: This module MUST be imported before any LLM library imports.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from langtrace_python_sdk import langtrace

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Initialize LangTrace with API key from environment
LANGTRACE_API_KEY = os.getenv("LANGTRACE_API_KEY")

if LANGTRACE_API_KEY:
    langtrace.init(
        api_key=LANGTRACE_API_KEY,
        batch=True,  # Enable batching for better performance
    )
    print("✓ LangTrace initialized successfully")
else:
    print("⚠ LANGTRACE_API_KEY not found in environment - tracing disabled")
