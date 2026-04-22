import os
from unittest import mock
import pytest
from langchain_core.documents import Document

# Mock chroma before importing rag_agent to prevent real initialization
with mock.patch("langchain_chroma.Chroma"):
    from agents.rag_agent import search_policy_documents, get_vectorstore, reset_rag

@pytest.fixture
def mock_vectorstore():
    with mock.patch("agents.rag_agent._vectorstore") as vs_mock:
        yield vs_mock

def test_search_policy_empty_store():
    with mock.patch("agents.rag_agent.get_vectorstore") as get_vs_mock:
        vs_instance = mock.MagicMock()
        vs_instance._collection.count.return_value = 0
        get_vs_mock.return_value = vs_instance
        
        result = search_policy_documents.invoke({"query": "test"})
        assert "No policy documents have been uploaded yet" in result

def test_search_policy_no_results():
    with mock.patch("agents.rag_agent.get_vectorstore") as get_vs_mock:
        vs_instance = mock.MagicMock()
        vs_instance._collection.count.return_value = 1
        vs_instance.similarity_search.return_value = []
        get_vs_mock.return_value = vs_instance
        
        result = search_policy_documents.invoke({"query": "test"})
        assert "No relevant policy information found" in result

def test_search_policy_with_results():
    with mock.patch("agents.rag_agent.get_vectorstore") as get_vs_mock:
        vs_instance = mock.MagicMock()
        vs_instance._collection.count.return_value = 1
        
        doc = Document(page_content="Policy detail", metadata={"source_file": "test.pdf", "page": 1})
        vs_instance.similarity_search.return_value = [doc]
        get_vs_mock.return_value = vs_instance
        
        result = search_policy_documents.invoke({"query": "test"})
        assert "Policy detail" in result
        assert "[Source 1: test.pdf, Page 1]" in result

def test_reset_rag():
    with mock.patch("chromadb.api.client.SharedSystemClient.clear_system_cache") as clear_mock:
        reset_rag()
        clear_mock.assert_called_once()
