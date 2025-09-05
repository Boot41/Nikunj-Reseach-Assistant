
import pytest
from unittest.mock import patch, MagicMock
from research_assistant.cli.main import big_banner

@patch('research_assistant.cli.main.console.print')
def test_big_banner(mock_print):
    big_banner()
    assert mock_print.call_count == 2
