"""
app.py — Streamlit UI for the Multi-Agent Customer Support System.

Provides a chat interface for John to interact with the AI assistant,
upload policy PDFs, and query customer data.
"""

import os
import sys
import uuid
import streamlit as st

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
# Load .env from project dir, then parent dir
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

# Map GEMINI_API_KEY to GOOGLE_API_KEY for langchain-google-genai
if os.environ.get("GEMINI_API_KEY") and not os.environ.get("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]

from setup_database import setup_database
from agents.router import query_router, reset_agents
from agents.rag_agent import ingest_pdf, get_vectorstore, reset_rag

# Import UI components
from ui.styles import get_custom_css
from ui.sidebar import render_sidebar
from ui.chat import render_chat

# ──────────────────────────── Page Config ─────────────────────

st.set_page_config(
    page_title="AI Customer Support Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(get_custom_css(), unsafe_allow_html=True)

# ──────────────────────────── Initialization ──────────────────

# Ensure database exists
db_path = setup_database()
db_uri = f"sqlite:///file:{db_path}?mode=ro&uri=true"
from langchain_community.utilities import SQLDatabase
db = SQLDatabase.from_uri(db_uri)

# Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

# ──────────────────────────── UI Render ───────────────────────

render_sidebar(db, get_vectorstore, ingest_pdf, reset_agents, reset_rag)
render_chat(query_router)
