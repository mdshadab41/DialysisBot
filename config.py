"""
Configuration file for DialysisBot
All settings are stored here in one place
"""

import os
from dotenv import load_dotenv # type: ignore

# Load .env file
load_dotenv()

# ─────────────────────────────
# Groq API Settings
# ─────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Model for generating answers (Groq-hosted Llama3 - FREE)
CHAT_MODEL = "llama-3.1-8b-instant"

# Model for embeddings (runs locally, no API needed)
EMBED_MODEL = "all-MiniLM-L6-v2"

# ─────────────────────────────
# Folder Settings
# ─────────────────────────────
# Where PDF files are stored
PDF_FOLDER = "docs"

# Where vector database stores data
CHROMA_DB_PATH = "chroma_db"

# ─────────────────────────────
# PDF Processing Settings
# ─────────────────────────────
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 300
CHUNK_SEPARATORS = [
    "\n\n",
    "\n",
    ". ",
    "! ",
    "? ",
    "; ",
    ", ",
    " ",
    ""
]

# ─────────────────────────────
# Retrieval Settings
# ─────────────────────────────
TOP_K = 5
SIMILARITY_THRESHOLD = 0.5

# ─────────────────────────────
# Chat Settings
# ─────────────────────────────
CHAT_HISTORY_SIZE = 5
TEMPERATURE = 0.1

# ─────────────────────────────
# UI Settings
# ─────────────────────────────
APP_TITLE = "DialysisBot: AI-Powered Dialysis Assistant"

DISCLAIMER = """
⚠️ **Medical Disclaimer**: This chatbot is for educational and informational 
purposes only. It is NOT a substitute for professional medical advice, diagnosis, 
or treatment. Always consult your doctor or healthcare provider for medical advice.
"""