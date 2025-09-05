
import pytest
from unittest.mock import patch, MagicMock, call
from google.api_core.exceptions import ResourceExhausted, DeadlineExceeded, ServiceUnavailable
from mcp import McpError
from mcp import types as mcp_types
from rich.panel import Panel
from research_assistant.cli.main import handle_agent_error, start_chat_session

@pytest.fixture
def mock_error_data():
    error_data = MagicMock(spec=mcp_types.ErrorData)
    error_data.message = "Test MCP Error"
    return error_data

def test_handle_agent_error(mock_error_data):
    assert "System resources exhausted" in handle_agent_error(ResourceExhausted('test'))
    assert "request took too long" in handle_agent_error(DeadlineExceeded('test'))
    assert "service is temporarily unavailable" in handle_agent_error(ServiceUnavailable('test'))
    assert "A tool failed" in handle_agent_error(McpError(mock_error_data))
    assert "Unexpected error" in handle_agent_error(Exception('test'))

@patch('research_assistant.cli.main.Runner')
@patch('research_assistant.cli.main.Prompt.ask')
@patch('research_assistant.cli.main.console')
@patch('research_assistant.cli.main.asyncio.run')
@patch('research_assistant.cli.main.root_agent')
@patch('research_assistant.cli.main.InMemorySessionService')
def test_start_chat_session_error_handling(mock_session_service, mock_agent, mock_asyncio_run, mock_console, mock_prompt_ask, mock_runner, mock_error_data):
    exceptions_to_test = [
        ResourceExhausted('test'),
        DeadlineExceeded('test'),
        ServiceUnavailable('test'),
        McpError(mock_error_data),
        Exception('test'),
    ]

    for i, e in enumerate(exceptions_to_test):
        # Reset mocks for each iteration
        mock_runner.reset_mock()
        mock_console.reset_mock()

        # First call to prompt returns a query, second call returns 'exit'
        mock_prompt_ask.side_effect = ['test query', 'exit']
        mock_runner.return_value.run.side_effect = e

        start_chat_session()

        # Check that the friendly error message was printed
        friendly_message = handle_agent_error(e)
        
        # Get all the calls to console.print
        print_calls = mock_console.print.call_args_list
        
        # Find the error panel call
        error_panel_call = None
        for c in print_calls:
            if c.args and isinstance(c.args[0], Panel) and c.args[0].border_style == 'red':
                error_panel_call = c
                break
        
        assert error_panel_call is not None, f"No error panel was printed for exception {type(e).__name__}. Calls: {print_calls}"
        
        # Check the content of the panel
        panel_content = str(error_panel_call.args[0].renderable)
        assert friendly_message in panel_content
