"""Unit tests for the Router LangGraph configuration."""

import pytest
from unittest.mock import patch, MagicMock

from agents.router import classify_query, RouterState, route_after_classification, query_router

@pytest.fixture
def empty_state() -> RouterState:
    return {
        "query": "",
        "classification": "",
        "sql_response": "",
        "rag_response": "",
        "final_response": "",
    }

@patch("agents.router.get_llm")
def test_classify_query_sql(mock_get_llm, empty_state):
    """Test that queries are properly classified as SQL."""
    # Setup mock
    mock_llm_instance = MagicMock()
    mock_llm_instance.invoke.return_value.content = "sql"
    mock_get_llm.return_value = mock_llm_instance
    
    state = dict(empty_state)
    state["query"] = "Show me Ema's profile"
    
    new_state = classify_query(state)
    assert new_state["classification"] == "sql"

@patch("agents.router.get_llm")
def test_classify_query_rag(mock_get_llm, empty_state):
    """Test that queries are properly classified as RAG."""
    mock_llm_instance = MagicMock()
    mock_llm_instance.invoke.return_value.content = "rag"
    mock_get_llm.return_value = mock_llm_instance
    
    state = dict(empty_state)
    state["query"] = "What is the refund policy?"
    
    new_state = classify_query(state)
    assert new_state["classification"] == "rag"

@patch("agents.router.get_llm")
def test_classify_query_fallback(mock_get_llm, empty_state):
    """Test fallback classifier logic when LLM output is uncontrolled."""
    mock_llm_instance = MagicMock()
    # Mock LLM returning malformed output
    mock_llm_instance.invoke.return_value.content = "unrelated word"
    mock_get_llm.return_value = mock_llm_instance
    
    state = dict(empty_state)
    state["query"] = "I don't know what I'm asking"
    
    new_state = classify_query(state)
    # The router should default to sql
    assert new_state["classification"] == "sql"

def test_route_after_classification(empty_state):
    """Test the conditional edge routing logic."""
    state = dict(empty_state)
    
    state["classification"] = "sql"
    assert route_after_classification(state) == "sql_agent"
    
    state["classification"] = "rag"
    assert route_after_classification(state) == "rag_agent"
    
    state["classification"] = "both"
    assert route_after_classification(state) == "both_agents"

def test_query_router_length_validation():
    """Verify input validation for very long queries."""
    long_query = "A" * 2000
    
    # Mock get_router to avoid actually running graph
    with patch("agents.router.get_router") as mock_get_router:
        mock_graph = MagicMock()
        mock_graph.invoke.return_value = {"final_response": "Processed"}
        mock_get_router.return_value = mock_graph
        
        query_router(long_query)
        
        # Verify the graph was invoked with a truncated query (max 1000)
        call_args = mock_graph.invoke.call_args[0][0]
        assert len(call_args["query"]) == 1000
        assert call_args["query"] == "A" * 1000

def test_query_router_type_validation():
    """Verify input validation handles non-strings gracefully."""
    response = query_router({"malformed": "dict"})
    assert "Error" in response
