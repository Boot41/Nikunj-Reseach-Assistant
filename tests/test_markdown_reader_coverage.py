
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from research_assistant.mcp.markdown_reader import list_tools, call_tool, signal_handler, shutdown_event

@pytest.mark.asyncio
@patch('research_assistant.mcp.markdown_reader.adk_to_mcp_tool_type')
async def test_list_tools(mock_adk_to_mcp):
    mock_adk_to_mcp.return_value = MagicMock()
    tools = await list_tools()
    assert len(tools) == 1
    mock_adk_to_mcp.assert_called_once()

@pytest.mark.asyncio
async def test_call_tool_success():
    with patch('research_assistant.mcp.markdown_reader.md_tools') as mock_md_tools:
        mock_tool = MagicMock()
        mock_tool.run_async = AsyncMock(return_value={"result": "success"})
        mock_md_tools.__getitem__.return_value = mock_tool
        mock_md_tools.__contains__.return_value = True

        result = await call_tool("summarize_markdown_file", {})

        assert result[0].text == '{\n  "result": "success"\n}'
        mock_tool.run_async.assert_called_once()

@pytest.mark.asyncio
async def test_call_tool_not_found():
    with patch('research_assistant.mcp.markdown_reader.md_tools') as mock_md_tools:
        mock_md_tools.__contains__.return_value = False
        result = await call_tool("non_existent_tool", {})
        assert result[0].text == "Tool not found"

@pytest.mark.asyncio
async def test_call_tool_exception():
    with patch('research_assistant.mcp.markdown_reader.md_tools') as mock_md_tools:
        mock_tool = MagicMock()
        mock_tool.run_async = AsyncMock(side_effect=Exception("Test Error"))
        mock_md_tools.__getitem__.return_value = mock_tool
        mock_md_tools.__contains__.return_value = True

        result = await call_tool("summarize_markdown_file", {})

        assert "Error: Test Error" in result[0].text

def test_signal_handler():
    shutdown_event.clear()
    signal_handler(None, None)
    assert shutdown_event.is_set()

