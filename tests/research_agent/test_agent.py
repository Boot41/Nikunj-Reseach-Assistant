
import pytest
from unittest.mock import patch

# Mock the StdioConnectionParams to avoid actual subprocess creation
@patch('google.adk.tools.mcp_tool.mcp_session_manager.StdioConnectionParams')
def test_agent_creation(mock_stdio_params):
    """Tests that the root_agent is created without errors."""
    try:
        from research_assistant.research_agent.agent import root_agent
        assert root_agent is not None
        assert root_agent.name == "research_agent"
    except Exception as e:
        pytest.fail(f"Agent creation failed with an exception: {e}")
