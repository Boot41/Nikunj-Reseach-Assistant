import pytest
from unittest.mock import patch, MagicMock, mock_open
import os
from research_assistant.mcp.pdf_parser import pdf_to_markdown, convert_http_to_markdown

@patch('research_assistant.mcp.pdf_parser.md.convert_uri')
def test_pdf_to_markdown(mock_convert_uri, tmp_path):
    # Arrange
    mock_result = MagicMock()
    mock_result.markdown = "# Test Markdown"
    mock_convert_uri.return_value = mock_result

    local_path = tmp_path / "test.pdf"
    local_path.touch()

    m = mock_open()
    with patch("builtins.open", m):
        # Act
        result_path = pdf_to_markdown(str(local_path))

        # Assert
        abs_path = os.path.abspath(local_path)
        mock_convert_uri.assert_called_once_with(f"file://{abs_path}")
        
        save_path = f"/home/nikunjagrwl/Documents/Research-assistant/markdown/{local_path.stem}.md"
        m.assert_called_once_with(save_path, "w", encoding="utf-8")
        handle = m()
        handle.write.assert_called_once_with("# Test Markdown")
        assert result_path == os.path.abspath(save_path)

@patch('research_assistant.mcp.pdf_parser.md.convert_uri')
def test_convert_http_to_markdown(mock_convert_uri):
    # Arrange
    mock_result = MagicMock()
    mock_result.markdown = "# Web Content"
    mock_convert_uri.return_value = mock_result

    url = "https://example.com/paper.pdf"

    m = mock_open()
    with patch("builtins.open", m):
        # Act
        result_path = convert_http_to_markdown(url)

        # Assert
        mock_convert_uri.assert_called_once_with(url)

        save_path = "/home/nikunjagrwl/Documents/Research-assistant/markdown/paper.md"
        m.assert_called_once_with(save_path, "w", encoding="utf-8")
        handle = m()
        handle.write.assert_called_once_with("# Web Content")
        assert result_path == os.path.abspath(save_path)