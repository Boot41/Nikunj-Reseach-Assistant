
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from research_assistant.mcp.arxiv_server import (
    search_tool,
    read_abstract_tool,
    download_pdf_tool,
    list_recent_tool,
)
import datetime

@pytest.mark.asyncio
async def test_search_tool():
    with patch('research_assistant.mcp.arxiv_server.arxiv.Search', new_callable=MagicMock) as mock_search:
        mock_result = MagicMock()
        mock_result.title = "Test Paper"
        mock_result.authors = [MagicMock(name='Author 1')]
        mock_result.summary = "A summary"
        mock_result.published = datetime.datetime.now()
        mock_result.get_short_id.return_value = "1234.5678"
        mock_result.pdf_url = "http://example.com/test.pdf"
        mock_search.return_value.results.return_value = [mock_result]

        result = await search_tool("test query", max_results=1)

        assert "papers" in result
        assert len(result["papers"]) == 1
        assert result["papers"][0]["title"] == "Test Paper"

@pytest.mark.asyncio
async def test_read_abstract_tool_found():
    with patch('research_assistant.mcp.arxiv_server.arxiv.Search', new_callable=MagicMock) as mock_search:
        mock_result = MagicMock()
        mock_result.entry_id = "http://arxiv.org/abs/1234.5678v1"
        mock_result.title = "Test Paper"
        mock_result.authors = [MagicMock(name='Author 1')]
        mock_result.summary = "A summary"
        mock_result.published = datetime.datetime.now()
        mock_search.return_value.results.return_value = iter([mock_result])

        result = await read_abstract_tool("1234.5678")

        assert result["title"] == "Test Paper"

@pytest.mark.asyncio
async def test_read_abstract_tool_not_found():
    with patch('research_assistant.mcp.arxiv_server.arxiv.Search', new_callable=MagicMock) as mock_search:
        mock_search.return_value.results.return_value = iter([])

        result = await read_abstract_tool("not-found-id")

        assert "error" in result
        assert result["error"] == "Paper not found"

@pytest.mark.asyncio
async def test_download_pdf_tool_found():
    with patch('research_assistant.mcp.arxiv_server.arxiv.Search', new_callable=MagicMock) as mock_search:
        mock_result = MagicMock()
        mock_result.download_pdf = MagicMock()
        mock_search.return_value.results.return_value = iter([mock_result])

        result = await download_pdf_tool("1234.5678")

        assert "pdf_path" in result
        mock_result.download_pdf.assert_called_once()

@pytest.mark.asyncio
async def test_download_pdf_tool_not_found():
    with patch('research_assistant.mcp.arxiv_server.arxiv.Search', new_callable=MagicMock) as mock_search:
        mock_search.return_value.results.return_value = iter([])

        result = await download_pdf_tool("not-found-id")

        assert "error" in result
        assert result["error"] == "Paper not found"

@pytest.mark.asyncio
async def test_list_recent_tool():
    with patch('research_assistant.mcp.arxiv_server.arxiv.Search', new_callable=MagicMock) as mock_search:
        mock_result = MagicMock()
        mock_result.title = "Recent Paper"
        mock_result.authors = [MagicMock(name='Author 1')]
        mock_result.summary = "A summary"
        mock_result.published = datetime.datetime.now()
        mock_result.get_short_id.return_value = "1234.5678"
        mock_result.pdf_url = "http://example.com/test.pdf"
        mock_search.return_value.results.return_value = [mock_result]

        result = await list_recent_tool("cs.AI", max_results=1)

        assert "papers" in result
        assert len(result["papers"]) == 1
        assert result["papers"][0]["title"] == "Recent Paper"
