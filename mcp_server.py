"""
mcp_server.py — FastMCP Server for the Multi-Agent Customer Support System.

Exposes agent capabilities as MCP tools that can be consumed
by any MCP-compatible client.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
# Also try parent .env
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from fastmcp import FastMCP
from agents.router import query_router
from agents.rag_agent import ingest_pdf, ingest_all_policies, get_vectorstore

mcp = FastMCP("CustomerSupport")


@mcp.tool()
def ask_support_assistant(question: str) -> str:
    """Ask the AI support assistant a question. It automatically determines
    whether to search the customer database, policy documents, or both,
    and returns a comprehensive answer.

    Args:
        question: A natural language question about customers, tickets, or policies.
    """
    return query_router(question)


@mcp.tool()
def upload_policy_document(file_path: str) -> str:
    """Upload and index a PDF policy document into the knowledge base.

    Args:
        file_path: Absolute path to the PDF file to upload.
    """
    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"
    if not file_path.lower().endswith(".pdf"):
        return "Error: Only PDF files are supported."

    try:
        count = ingest_pdf(file_path)
        return f"✅ Successfully indexed '{os.path.basename(file_path)}' — {count} chunks added to the knowledge base."
    except Exception as e:
        return f"Error indexing document: {str(e)}"


@mcp.tool()
def get_knowledge_base_stats() -> str:
    """Get statistics about the current knowledge base (number of indexed document chunks)."""
    try:
        vs = get_vectorstore()
        count = vs._collection.count()
        return f"Knowledge base contains {count} document chunks."
    except Exception as e:
        return f"Error getting stats: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
