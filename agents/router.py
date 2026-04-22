"""
router.py — LangGraph Router Agent.

Classifies incoming queries and routes to the appropriate specialized agent:
- SQL Agent for structured customer data queries
- RAG Agent for policy document queries
- Both agents when the query spans both domains

Uses the LangGraph StateGraph for orchestration.
"""

import os
import operator
from typing import Annotated, TypedDict, Literal

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

from llm_factory import get_llm
from agents.sql_agent import create_sql_agent_instance
from agents.rag_agent import create_rag_agent


# ──────────────────────────── State ────────────────────────────

class RouterState(TypedDict):
    """State for the router graph."""
    history: list
    query: str
    classification: str  # "sql", "rag", or "both"
    sql_response: str
    rag_response: str
    final_response: str


# ──────────────────────────── Agents (lazy singletons) ────────

_sql_agent = None
_rag_agent = None


def get_sql_agent():
    global _sql_agent
    if _sql_agent is None:
        _sql_agent = create_sql_agent_instance()
    return _sql_agent


def get_rag_agent():
    global _rag_agent
    if _rag_agent is None:
        _rag_agent = create_rag_agent()
    return _rag_agent


# ──────────────────────────── Nodes ────────────────────────────

def classify_query(state: RouterState) -> RouterState:
    """Use LLM to classify the query as sql, rag, or both."""
    llm = get_llm(temperature=0)

    history_str = ""
    if state.get("history"):
        history_str = "Recent Conversation History:\n"
        for msg in state["history"][-4:]:  # Last 4 messages for context
            role = "User" if msg["role"] == "user" else "Assistant"
            history_str += f"{role}: {msg['content']}\n"
        history_str += "\n"

    classification_prompt = f"""Classify the following customer support query into one of three categories:

1. "sql" - The query is about specific customer data, support tickets, products, account details,
   or anything that would be stored in a structured database. Examples:
   - "Show me Ema's profile"
   - "What are the open support tickets?"
   - "How many premium customers do we have?"

2. "rag" - The query is about company policies, procedures, terms, refund policies, privacy policies,
   or anything found in official policy documents. Examples:
   - "What is the refund policy?"
   - "How long is the warranty period?"
   - "What are the terms of service?"

3. "both" - The query needs information from both the database AND policy documents. Examples:
   - "Does customer Ema qualify for a refund based on our policy?"
   - "What is the support SLA for premium customers?"

{history_str}Query: {state["query"]}

Respond with ONLY one word: sql, rag, or both"""

    classification = "sql"  # Fallback default
    for _attempt in range(2):
        try:
            response = llm.invoke(classification_prompt)
            content = response.content
            if isinstance(content, list):
                content = " ".join([str(block.get("text", block)) if isinstance(block, dict) else str(block) for block in content])
            result = str(content).strip().lower()
            
            # Substring matching for verbose LLM outputs
            if "both" in result:
                classification = "both"
                break
            elif "rag" in result:
                classification = "rag"
                break
            elif "sql" in result:
                classification = "sql"
                break
        except Exception as e:
            import logging
            logging.warning(f"Classification attempt {_attempt} failed: {e}")

    return {**state, "classification": classification}


def _invoke_agent_with_retry(agent, query: str, history: list = None, max_retries: int = 2):
    """Invoke a LangChain agent with retry on empty model output errors.

    Local models (LM Studio) occasionally return empty content which causes
    LangChain to raise 'model output must contain either output text or tool calls'.
    This helper retries the invocation before giving up.
    """
    from langchain_core.messages import HumanMessage, AIMessage
    
    lc_messages = []
    if history:
        for msg in history:
            if msg["role"] == "user":
                lc_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                lc_messages.append(AIMessage(content=msg["content"]))
                
    lc_messages.append(HumanMessage(content=query))
    
    last_error = None
    for attempt in range(max_retries):
        try:
            result = agent.invoke(
                {"messages": lc_messages}
            )
            content = result["messages"][-1].content
            if isinstance(content, list):
                content = " ".join(
                    [str(block.get("text", block)) if isinstance(block, dict) else str(block) for block in content]
                )
            response = str(content).strip()
            if response:
                return response
            # Empty but no exception — retry
            last_error = "Model returned an empty response"
        except Exception as e:
            last_error = str(e)
            if "empty" not in last_error.lower() and "model output" not in last_error.lower():
                # Non-retriable error
                raise
    raise RuntimeError(last_error)


def run_sql_agent(state: RouterState) -> RouterState:
    """Execute the SQL agent on the query."""
    agent = get_sql_agent()
    try:
        response = _invoke_agent_with_retry(agent, state["query"], state.get("history", []))
    except Exception as e:
        response = f"Error querying database: {str(e)}"
    return {**state, "sql_response": response}


def run_rag_agent(state: RouterState) -> RouterState:
    """Execute the RAG agent on the query."""
    agent = get_rag_agent()
    try:
        response = _invoke_agent_with_retry(agent, state["query"], state.get("history", []))
    except Exception as e:
        response = f"Error searching policy documents: {str(e)}"
    return {**state, "rag_response": response}


def synthesize_response(state: RouterState) -> RouterState:
    """Synthesize the final response from agent outputs."""
    classification = state["classification"]
    sql_resp = state.get("sql_response", "")
    rag_resp = state.get("rag_response", "")

    if classification == "sql":
        return {**state, "final_response": sql_resp}
    elif classification == "rag":
        return {**state, "final_response": rag_resp}
    else:
        # Both — synthesize with LLM
        llm = get_llm(temperature=0.3)
        synthesis_prompt = f"""You are a customer support assistant. Combine the following information
from our database and policy documents to provide a comprehensive answer.

User Question: {state["query"]}

Database Information:
{sql_resp}

Policy Document Information:
{rag_resp}

Provide a clear, unified response that integrates both sources of information."""

        result = llm.invoke(synthesis_prompt)
        content = result.content
        if isinstance(content, list):
            content = " ".join([str(block.get("text", block)) if isinstance(block, dict) else str(block) for block in content])

        return {**state, "final_response": str(content)}


# ──────────────────────────── Routing Logic ────────────────────

def route_after_classification(state: RouterState) -> str:
    """Determine next node based on classification."""
    classification = state["classification"]
    if classification == "sql":
        return "sql_agent"
    elif classification == "rag":
        return "rag_agent"
    else:
        return "both_agents"


def run_both_agents(state: RouterState) -> RouterState:
    """Run both SQL and RAG agents sequentially for 'both' classification."""
    state = run_sql_agent(state)
    state = run_rag_agent(state)
    return state


# ──────────────────────────── Graph ────────────────────────────

def build_router_graph():
    """Build and compile the LangGraph router."""
    graph = StateGraph(RouterState)

    # Add nodes
    graph.add_node("classify", classify_query)
    graph.add_node("sql_agent", run_sql_agent)
    graph.add_node("rag_agent", run_rag_agent)
    graph.add_node("both_agents", run_both_agents)
    graph.add_node("synthesize", synthesize_response)

    # Add edges
    graph.add_edge(START, "classify")
    
    graph.add_conditional_edges(
        "classify",
        route_after_classification,
        {
            "sql_agent": "sql_agent",
            "rag_agent": "rag_agent",
            "both_agents": "both_agents",
        },
    )
    graph.add_edge("sql_agent", "synthesize")
    graph.add_edge("rag_agent", "synthesize")
    graph.add_edge("both_agents", "synthesize")
    graph.add_edge("synthesize", END)

    # Compile with memory for multi-turn conversations
    checkpointer = InMemorySaver()
    compiled = graph.compile(checkpointer=checkpointer)
    return compiled


# Module-level singleton
_router = None


def get_router():
    """Get or create the router graph singleton."""
    global _router
    if _router is None:
        _router = build_router_graph()
    return _router


def reset_agents():
    """Clear all cached singletons so they are rebuilt with the current provider."""
    global _sql_agent, _rag_agent, _router
    _sql_agent = None
    _rag_agent = None
    _router = None


def query_router(question: str, history: list = None, thread_id: str = "default") -> str:
    """
    Route a question through the multi-agent system.

    Args:
        question: The user's natural language question
        history: List of previous conversation messages
        thread_id: Conversation thread ID for memory

    Returns:
        The final response string
    """
    # Security review input validation: Bound maximum input length to prevent DOS/RateLimit exhaustion
    if not isinstance(question, str):
        return "Error: Question must be a string."
    if len(question) > 1000:
        question = question[:1000]

    if history is None:
        history = []

    router = get_router()
    config = {"configurable": {"thread_id": thread_id}}

    result = router.invoke(
        {
            "history": history,
            "query": question,
            "classification": "",
            "sql_response": "",
            "rag_response": "",
            "final_response": "",
        },
        config,
    )
    return result["final_response"]
