
import pytest
from pathlib import Path
from research_assistant.mcp.markdown_reader import summarize_markdown_file

def test_summarize_markdown_file_success(tmp_path: Path):
    """
    Tests that summarize_markdown_file successfully reads and summarizes a file.
    """
    # Create a dummy markdown file
    content = """
# Title

This is the first paragraph.

This is the second paragraph.
    """
    file_path = tmp_path / "test.md"
    file_path.write_text(content)

    # Call the function
    summary = summarize_markdown_file(str(file_path))

    # Assert the expected output
    expected_summary = " ".join([
        "# Title",
        "This is the first paragraph.",
        "This is the second paragraph."
    ])
    assert summary == expected_summary

def test_summarize_markdown_file_not_found():
    """
    Tests that summarize_markdown_file raises FileNotFoundError for a non-existent file.
    """
    with pytest.raises(FileNotFoundError):
        summarize_markdown_file("non_existent_file.md")

def test_summarize_markdown_file_empty_file(tmp_path: Path):
    """
    Tests that summarize_markdown_file handles empty files gracefully.
    """
    file_path = tmp_path / "empty.md"
    file_path.write_text("")

    summary = summarize_markdown_file(str(file_path))
    assert summary == ""
