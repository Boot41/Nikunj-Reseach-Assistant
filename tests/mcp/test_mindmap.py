import pytest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
from research_assistant.mcp.mindmap import summarize_md, generate_mindmap_tool
import json


def test_summarize_md_success(tmp_path: Path):
    content = "This is a test markdown file with some content."
    file_path = tmp_path / "test.md"
    file_path.write_text(content)

    summary = summarize_md(str(file_path))

    assert summary == content


def test_summarize_md_file_not_found():
    with pytest.raises(FileNotFoundError):
        summarize_md("non_existent_file.md")

@patch('research_assistant.mcp.mindmap.genai.Client')
def test_generate_mindmap_tool(mock_gemini_client, tmp_path: Path):
    # Arrange
    mock_response = MagicMock()
    mock_response.text = '{"Topic1": {"Subtopics": [], "Prerequisites": []}}'
    mock_gemini_client.return_value.models.generate_content.return_value = mock_response

    file_content = "Some markdown content"
    file_path = tmp_path / "test.md"
    file_path.write_text(file_content)

    # Mock open to capture the file writing
    m = mock_open()
    with patch("builtins.open", m):
        # Act
        result = generate_mindmap_tool(str(file_path))

        # Assert
        mock_gemini_client.return_value.models.generate_content.assert_called_once()
        expected_path = f"/home/nikunjagrwl/Documents/Research-assistant/mindmaps/{file_path.stem}_mindmap.json"
        m.assert_called_once_with(expected_path, "w")
        handle = m()
        written_data = handle.write.call_args[0][0]
        
        # The tool is doing json.dump on a string, so we expect a JSON-encoded string.
        assert written_data == json.dumps(mock_response.text, indent=2)

        assert result == mock_response.text