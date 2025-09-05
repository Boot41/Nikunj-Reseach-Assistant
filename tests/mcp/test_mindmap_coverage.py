import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from research_assistant.mcp.mindmap import (
    list_tools,
    call_tool,
)

@pytest.mark.asyncio
@patch('research_assistant.mcp.mindmap.adk_to_mcp_tool_type')
async def test_list_tools(mock_adk_to_mcp):
    mock_adk_to_mcp.return_value = MagicMock()
    tools = await list_tools()
    assert len(tools) == 1
    mock_adk_to_mcp.assert_called_once()

@pytest.mark.asyncio
async def test_call_tool_success():
    with patch('research_assistant.mcp.mindmap.mindmap_tools') as mock_mindmap_tools:
        mock_tool = MagicMock()
        mock_tool.run_async = AsyncMock(return_value={"result": "success"})
        mock_mindmap_tools.__getitem__.return_value = mock_tool
        mock_mindmap_tools.__contains__.return_value = True

        result = await call_tool("generate_mindmap_tool", {})

        assert result[0].text == '''{
  "result": "success"
}'''
        mock_tool.run_async.assert_called_once()

@pytest.mark.asyncio
async def test_call_tool_not_found():
    with patch('research_assistant.mcp.mindmap.mindmap_tools') as mock_mindmap_tools:
        mock_mindmap_tools.__contains__.return_value = False
        result = await call_tool("non_existent_tool", {})
        assert result[0].text == "Tool not found"

@pytest.mark.asyncio
async def test_call_tool_exception():
    with patch('research_assistant.mcp.mindmap.mindmap_tools') as mock_mindmap_tools:
        mock_tool = MagicMock()
        mock_tool.run_async = AsyncMock(side_effect=Exception("Test Error"))
        mock_mindmap_tools.__getitem__.return_value = mock_tool
        mock_mindmap_tools.__contains__.return_value = True

        result = await call_tool("generate_mindmap_tool", {})

        assert "Error: Test Error" in result[0].text
