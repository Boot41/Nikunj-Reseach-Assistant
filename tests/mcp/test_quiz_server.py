import pytest
import json
from unittest.mock import patch, mock_open
from research_assistant.mcp.quiz_server import (
    QuizManager,
    load_quizzes,
    save_quizzes,
    create_quiz_in_file,
    add_question_to_quiz,
    reload_quizzes
)

@pytest.fixture
def mock_quiz_file(tmp_path):
    return tmp_path / "quizzes.json"

@pytest.fixture
def manager(mock_quiz_file):
    with patch('research_assistant.mcp.quiz_server.QUIZ_FILE', mock_quiz_file):
        yield QuizManager()

def test_load_quizzes_no_file(mock_quiz_file):
    with patch('research_assistant.mcp.quiz_server.QUIZ_FILE', mock_quiz_file):
        assert load_quizzes() == {}

def test_load_quizzes_empty_file(mock_quiz_file):
    mock_quiz_file.write_text("")
    with patch('research_assistant.mcp.quiz_server.QUIZ_FILE', mock_quiz_file):
        assert load_quizzes() == {}

def test_load_quizzes_invalid_json(mock_quiz_file):
    mock_quiz_file.write_text("invalid json")
    with patch('research_assistant.mcp.quiz_server.QUIZ_FILE', mock_quiz_file):
        assert load_quizzes() == {}

def test_save_quizzes(mock_quiz_file):
    data = {"test_quiz": {"questions": []}}
    with patch('research_assistant.mcp.quiz_server.QUIZ_FILE', mock_quiz_file):
        save_quizzes(data)
        content = mock_quiz_file.read_text()
        assert json.loads(content) == data

def test_create_quiz(manager, mock_quiz_file):
    manager.create_quiz("New Quiz")
    assert "New Quiz" in manager.quizzes
    content = mock_quiz_file.read_text()
    assert "New Quiz" in json.loads(content)

def test_add_question(manager, mock_quiz_file):
    manager.create_quiz("Test Quiz")
    manager.add_question("Test Quiz", "What is 1+1?", ["1", "2"], 1)
    assert len(manager.quizzes["Test Quiz"]["questions"]) == 1
    content = mock_quiz_file.read_text()
    assert len(json.loads(content)["Test Quiz"]["questions"]) == 1

@pytest.mark.asyncio
async def test_create_quiz_in_file(manager):
    with patch('research_assistant.mcp.quiz_server.manager', manager):
        result = await create_quiz_in_file("Async Quiz")
        assert result == {"message": "Quiz created"}

@pytest.mark.asyncio
async def test_add_question_to_quiz(manager, mock_quiz_file):
    with patch('research_assistant.mcp.quiz_server.QUIZ_FILE', mock_quiz_file):
        with patch('research_assistant.mcp.quiz_server.manager', manager):
            reload_quizzes() # Ensure manager has fresh quizzes
            result = await add_question_to_quiz("My Quiz", "A question", ["A", "B"], 0)
            assert result == {"message": "Question added to quiz 'My Quiz'."}
            assert "My Quiz" in manager.quizzes
            assert len(manager.quizzes["My Quiz"]["questions"]) == 1