"""Tests for code excerpt extraction utility.

This module tests the ExcerptFormatter utility which extracts context lines
around error locations in files for display in validation output.
"""

import pytest

from prompt_unifier.utils.excerpt import ExcerptFormatter


@pytest.fixture
def excerpt_formatter() -> ExcerptFormatter:
    """Create an ExcerptFormatter instance for testing."""
    return ExcerptFormatter()


@pytest.fixture
def sample_file_content() -> str:
    """Create sample file content for testing."""
    return """line 1: name: test-prompt
line 2: description: A test prompt
line 3: version: 1.0.0
line 4: >>>
line 5: This is the content
line 6: with multiple lines
line 7: of prompt text"""


def test_extract_excerpt_with_context(excerpt_formatter: ExcerptFormatter) -> None:
    """Test extracting a 3-line excerpt around an error line (±1 context)."""
    # Arrange
    file_content = """name: test-prompt
description: Test
>>>
Content line 1
Content line 2
Content line 3"""

    # Act - Extract line 5 (Content line 2) with ±1 context
    result = excerpt_formatter.extract_excerpt(file_content, line_number=5, context_lines=1)

    # Assert
    assert "4 | Content line 1" in result
    assert "5 | Content line 2" in result
    assert "6 | Content line 3" in result
    # Should show 3 lines total (line 5 ± 1)


def test_excerpt_at_file_start(excerpt_formatter: ExcerptFormatter) -> None:
    """Test excerpt extraction at the start of the file (lines 1-3)."""
    # Arrange
    file_content = """name: test-prompt
description: Test
version: 1.0.0
>>>
Content here"""

    # Act - Extract line 1 with ±1 context (should handle boundary)
    result = excerpt_formatter.extract_excerpt(file_content, line_number=1, context_lines=1)

    # Assert
    assert "1 | name: test-prompt" in result
    assert "2 | description: Test" in result
    # Should not try to show line 0 (doesn't exist)


def test_excerpt_at_file_end(excerpt_formatter: ExcerptFormatter) -> None:
    """Test excerpt extraction at the end of the file (last 3 lines)."""
    # Arrange
    file_content = """name: test-prompt
description: Test
>>>
Content line 1
Content line 2
Last line here"""

    # Act - Extract last line (line 6) with ±1 context
    result = excerpt_formatter.extract_excerpt(file_content, line_number=6, context_lines=1)

    # Assert
    assert "5 | Content line 2" in result
    assert "6 | Last line here" in result
    # Should not try to show line 7 (doesn't exist)


def test_excerpt_with_line_numbers(excerpt_formatter: ExcerptFormatter) -> None:
    """Test that excerpt includes line numbers in format 'N | content'."""
    # Arrange
    file_content = """name: test-prompt
description: Test
>>>
Content here"""

    # Act
    result = excerpt_formatter.extract_excerpt(file_content, line_number=2, context_lines=1)

    # Assert
    assert "1 |" in result  # Line number prefix
    assert "2 |" in result
    assert "3 |" in result
    assert "name: test-prompt" in result
    assert "description: Test" in result


def test_excerpt_single_line_context(excerpt_formatter: ExcerptFormatter) -> None:
    """Test excerpt with context_lines=0 (only the error line itself)."""
    # Arrange
    file_content = """name: test-prompt
description: Test
>>>
Content here"""

    # Act
    result = excerpt_formatter.extract_excerpt(file_content, line_number=2, context_lines=0)

    # Assert
    assert "2 | description: Test" in result
    # Should only show line 2, no context lines
    assert "1 |" not in result
    assert "3 |" not in result


def test_excerpt_larger_context(excerpt_formatter: ExcerptFormatter) -> None:
    """Test excerpt with larger context (e.g., context_lines=2)."""
    # Arrange
    file_content = """line 1
line 2
line 3
line 4
line 5
line 6
line 7"""

    # Act - Extract line 4 with ±2 context (5 lines total)
    result = excerpt_formatter.extract_excerpt(file_content, line_number=4, context_lines=2)

    # Assert
    assert "2 | line 2" in result
    assert "3 | line 3" in result
    assert "4 | line 4" in result
    assert "5 | line 5" in result
    assert "6 | line 6" in result
    # Should show lines 2-6 (line 4 ± 2)


def test_excerpt_handles_empty_lines(excerpt_formatter: ExcerptFormatter) -> None:
    """Test that excerpt correctly handles empty lines in file content."""
    # Arrange
    file_content = """name: test-prompt

description: Test

>>>"""

    # Act
    result = excerpt_formatter.extract_excerpt(file_content, line_number=3, context_lines=1)

    # Assert
    assert "2 |" in result  # Empty line should still have line number
    assert "3 | description: Test" in result
    assert "4 |" in result  # Empty line


def test_excerpt_formatting_multi_line_string(excerpt_formatter: ExcerptFormatter) -> None:
    """Test that extract_excerpt returns a properly formatted multi-line string."""
    # Arrange
    file_content = """line 1
line 2
line 3
line 4
line 5"""

    # Act
    result = excerpt_formatter.extract_excerpt(file_content, line_number=3, context_lines=1)

    # Assert
    lines = result.strip().split("\n")
    assert len(lines) == 3  # Should have 3 lines (line 3 ± 1)
    assert all("|" in line for line in lines)  # All lines should have pipe separator
