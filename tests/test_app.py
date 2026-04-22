import os
from unittest import mock
import pytest
from streamlit.testing.v1 import AppTest

# Mock the database setup and agent logic so the UI loads instantly without real DBs
@pytest.fixture(autouse=True)
def mock_dependencies():
    with mock.patch("app.setup_database") as mock_db, \
         mock.patch("agents.router.build_router_graph") as mock_graph_factory, \
         mock.patch("agents.rag_agent.get_vectorstore"):
        mock_db.return_value = "/tmp/mock.db"
        
        # Configure the graph mock to return a sensible response by default
        mock_graph = mock.MagicMock()
        mock_graph.invoke.return_value = {"final_response": "Mocked AI response"}
        mock_graph_factory.return_value = mock_graph
        
        yield

def test_app_loads_successfully():
    """Test that the Streamlit app loads and renders the main UI components."""
    at = AppTest.from_file("app.py", default_timeout=30)
    
    # We must patch os.environ directly for Streamlit tests sometimes,
    # or just let it run with defaults.
    at.run()
    
    # Check for no unhandled exceptions
    assert not at.exception
    
    # Verify main title exists
    assert any("AI Customer Support Assistant" in md.value for md in at.markdown)
    
    # Verify sidebar components
    assert any("⚙️ LLM Provider" in md.value for md in at.sidebar.markdown)
    assert any("📊 Database Stats" in md.value for md in at.sidebar.markdown)
    assert any("⚡ Quick Actions" in md.value for md in at.sidebar.markdown)

def test_app_chat_input():
    at = AppTest.from_file("app.py", default_timeout=30)
    at.run()
    
    # Find the chat input
    assert len(at.chat_input) > 0
    chat = at.chat_input[0]
    
    # Set chat value and run
    chat.set_value("Test message")
    at.run()
    
    # Verify message was added to chat history
    assert "Test message" in [msg.value for msg in at.markdown]
    assert "Mocked AI response" in [msg.value for msg in at.markdown]
