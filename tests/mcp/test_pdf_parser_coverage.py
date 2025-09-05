import pytest
from unittest.mock import patch, MagicMock, AsyncMock, mock_open
import os
from research_assistant.mcp.pdf_parser import (
    convert_http_to_markdown,
    list_tools,
    call_tool,
)

@patch('research_assistant.mcp.pdf_parser.md.convert_uri')
def test_convert_http_to_markdown_no_filename(mock_convert_uri):
    # Arrange
    mock_result = MagicMock()
    mock_result.markdown = "# Web Content"
    mock_convert_uri.return_value = mock_result

    url = "https://example.com/"

    m = mock_open()
    with patch("builtins.open", m):
        # Act
        result_path = convert_http_to_markdown(url)

        # Assert
        mock_convert_uri.assert_called_once_with(url)

        save_path = "/home/nikunjagrwl/Documents/Research-assistant/markdown/downloaded_file.md"
        m.assert_called_once_with(save_path, "w", encoding="utf-8")
        m().write.assert_called_once_with("# Web Content")
        assert result_path == os.path.abspath(save_path)

@pytest.mark.asyncio
@patch('research_assistant.mcp.pdf_parser.adk_to_mcp_tool_type')
async def test_list_tools(mock_adk_to_mcp):
    mock_adk_to_mcp.return_value = MagicMock()
    tools = await list_tools()
    assert len(tools) == 2
    assert mock_adk_to_mcp.call_count == 2

@pytest.mark.asyncio
async def test_call_tool_success():
    with patch('research_assistant.mcp.pdf_parser.pdf_tools') as mock_pdf_tools:
        mock_tool = MagicMock()
        mock_tool.run_async = AsyncMock(return_value={"result": "success"})
        mock_pdf_tools.__getitem__.return_value = mock_tool
        mock_pdf_tools.__contains__.return_value = True

        result = await call_tool("pdf_to_markdown", {})

        assert result[0].text == '''{
  "result": "success"
}'''
        mock_tool.run_async.assert_called_once()

@pytest.mark.asyncio
async def test_call_tool_not_found():
    with patch('research_assistant.mcp.pdf_parser.pdf_tools') as mock_pdf_tools:
        mock_pdf_tools.__contains__.return_value = False
        result = await call_tool("non_existent_tool", {})
        assert result[0].text == "Tool not found"

@pytest.mark.asyncio
async def test_call_tool_exception():
    with patch('research_assistant.mcp.pdf_parser.pdf_tools') as mock_pdf_tools:
        mock_tool = MagicMock()
        mock_tool.run_async = AsyncMock(side_effect=Exception("Test Error"))
        mock_pdf_tools.__getitem__.return_value = mock_tool
        mock_pdf_tools.__contains__.return_value = True

        result = await call_tool("pdf_to_markdown", {})

        assert "Error: Test Error" in result[0].text