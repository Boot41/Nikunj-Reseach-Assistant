
import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock
from research_assistant.mcp.quiz_server import (
    load_quizzes,
    QuizManager,
    list_tools,
    call_tool,
)

@pytest.fixture
def mock_quiz_file(tmp_path):
    return tmp_path / "quizzes.json"

def test_load_quizzes_empty_file(mock_quiz_file):
    mock_quiz_file.write_text("")
    with patch('research_assistant.mcp.quiz_server.QUIZ_FILE', mock_quiz_file):
        assert load_quizzes() == {}

def test_load_quizzes_invalid_json(mock_quiz_file):
    mock_quiz_file.write_text("{{")
    with patch('research_assistant.mcp.quiz_server.QUIZ_FILE', mock_quiz_file):
        assert load_quizzes() == {}


@pytest.fixture
def manager(mock_quiz_file):
    with patch('research_assistant.mcp.quiz_server.QUIZ_FILE', mock_quiz_file):
        yield QuizManager()

def test_create_quiz_already_exists(manager):
    manager.create_quiz("Test Quiz")
    result = manager.create_quiz("Test Quiz")
    assert result == "Quiz 'Test Quiz' created."

def test_add_question_quiz_not_found(manager):
    result = manager.add_question("Non Existent Quiz", "q", ["o"], 0)
    assert result == "Quiz 'Non Existent Quiz' does not exist."

@pytest.mark.asyncio
@patch('research_assistant.mcp.quiz_server.adk_to_mcp_tool_type')
async def test_list_tools(mock_adk_to_mcp):
    mock_adk_to_mcp.return_value = MagicMock()
    tools = await list_tools()
    assert len(tools) == 2
    assert mock_adk_to_mcp.call_count == 2

@pytest.mark.asyncio
async def test_call_tool_success():
    with patch('research_assistant.mcp.quiz_server.quiz_tools') as mock_quiz_tools:
        mock_tool = MagicMock()
        mock_tool.run_async = AsyncMock(return_value={"result": "success"})
        mock_quiz_tools.__getitem__.return_value = mock_tool
        mock_quiz_tools.__contains__.return_value = True

        result = await call_tool("create_quiz_in_file", {})

        assert result[0].text == '''{
  "result": "success"
}'''
        mock_tool.run_async.assert_called_once()

@pytest.mark.asyncio
async def test_call_tool_not_found():
    with patch('research_assistant.mcp.quiz_server.quiz_tools') as mock_quiz_tools:
        mock_quiz_tools.__contains__.return_value = False
        result = await call_tool("non_existent_tool", {})
        assert result[0].text == "Tool not found"

@pytest.mark.asyncio
async def test_call_tool_exception():
    with patch('research_assistant.mcp.quiz_server.quiz_tools') as mock_quiz_tools:
        mock_tool = MagicMock()
        mock_tool.run_async = AsyncMock(side_effect=Exception("Test Error"))
        mock_quiz_tools.__getitem__.return_value = mock_tool
        mock_quiz_tools.__contains__.return_value = True

        result = await call_tool("create_quiz_in_file", {})

        assert "Error: Test Error" in result[0].text
