import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from research_assistant.mcp.arxiv_server import (
    search_tool,
    read_abstract_tool,
    download_pdf_tool,
    list_recent_tool,
    list_tools,
    call_tool,
)

@pytest.mark.asyncio
async def test_search_tool_error():
    with patch('research_assistant.mcp.arxiv_server.arxiv.Search', side_effect=Exception("Test Error")):
        result = await search_tool("test query")
        assert "error" in result
        assert result["error"] == "Test Error"

@pytest.mark.asyncio
async def test_read_abstract_tool_error():
    with patch('research_assistant.mcp.arxiv_server.arxiv.Search', side_effect=Exception("Test Error")):
        result = await read_abstract_tool("test_id")
        assert "error" in result
        assert result["error"] == "Test Error"

@pytest.mark.asyncio
async def test_download_pdf_tool_error():
    with patch('research_assistant.mcp.arxiv_server.arxiv.Search', side_effect=Exception("Test Error")):
        result = await download_pdf_tool("test_id")
        assert "error" in result
        assert result["error"] == "Test Error"

@pytest.mark.asyncio
async def test_list_recent_tool_error():
    with patch('research_assistant.mcp.arxiv_server.arxiv.Search', side_effect=Exception("Test Error")):
        result = await list_recent_tool("cs.AI")
        assert "error" in result
        assert result["error"] == "Test Error"

@pytest.mark.asyncio
@patch('research_assistant.mcp.arxiv_server.adk_to_mcp_tool_type')
async def test_list_tools(mock_adk_to_mcp):
    mock_adk_to_mcp.return_value = MagicMock()
    tools = await list_tools()
    assert len(tools) == 5
    assert mock_adk_to_mcp.call_count == 5

@pytest.mark.asyncio
async def test_call_tool_success():
    with patch('research_assistant.mcp.arxiv_server.arxiv_tools') as mock_arxiv_tools:
        mock_tool = MagicMock()
        mock_tool.run_async = AsyncMock(return_value={"result": "success"})
        mock_arxiv_tools.__getitem__.return_value = mock_tool
        mock_arxiv_tools.__contains__.return_value = True

        result = await call_tool("search_tool", {})

        assert result[0].text == '''{
  "result": "success"
}'''
        mock_tool.run_async.assert_called_once()

@pytest.mark.asyncio
async def test_call_tool_not_found():
    with patch('research_assistant.mcp.arxiv_server.arxiv_tools') as mock_arxiv_tools:
        mock_arxiv_tools.__contains__.return_value = False
        result = await call_tool("non_existent_tool", {})
        assert result[0].text == "Tool not found"

@pytest.mark.asyncio
async def test_call_tool_exception():
    with patch('research_assistant.mcp.arxiv_server.arxiv_tools') as mock_arxiv_tools:
        mock_tool = MagicMock()
        mock_tool.run_async = AsyncMock(side_effect=Exception("Test Error"))
        mock_arxiv_tools.__getitem__.return_value = mock_tool
        mock_arxiv_tools.__contains__.return_value = True

        result = await call_tool("search_tool", {})

        assert "Error: Test Error" in result[0].text
