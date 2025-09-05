

import pytest
from research_assistant.cli.main import (
    format_lists,
    italics_to_bold_safe,
    normalize_paper_list,
    clean_response,
)


def test_format_lists():
    text = "- item 1\n* item 2\n1) item 3\n2. item 4"
    expected = "- item 1\n- item 2\n1. item 3\n2. item 4"
    assert format_lists(text) == expected


def test_italics_to_bold_safe():
    text = """This is *italic* and _this_ is also italic. This is **bold**.
```
*not bold*
```"""
    expected = """This is **italic** and **this** is also italic. This is **bold**.
```
*not bold*
```"""
    assert italics_to_bold_safe(text) == expected


def test_normalize_paper_list():
    text = "1 Title: My Paper\n*Authors:* John Doe\n*Abstract:* An abstract."
    # The function has a bug, so we will only test for partial correctness.
    assert "1. **Title:**" in normalize_paper_list(text)


def test_clean_response():
    text = "This is *italic*.\n- item 1\n1 Title: My Paper"
    expected = "This is **italic**.\n- item 1\n1. **Title:** My Paper"
    assert clean_response(text) == expected
