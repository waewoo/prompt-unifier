"""Tests for PathFilter utility class."""

from prompt_unifier.utils.path_filter import PathFilter


class TestPathFilter:
    """Tests for PathFilter class."""

    def test_matches_pattern_true(self) -> None:
        """Test that matches_pattern returns True for matching pattern."""
        result = PathFilter.matches_pattern("prompts/python/example.md", "**/python/**")
        assert result is True

    def test_matches_pattern_false(self) -> None:
        """Test that matches_pattern returns False for non-matching pattern."""
        result = PathFilter.matches_pattern("prompts/javascript/test.md", "**/python/**")
        assert result is False

    def test_matches_pattern_with_extension(self) -> None:
        """Test pattern matching with file extension."""
        assert PathFilter.matches_pattern("src/file.py", "**/*.py") is True
        assert PathFilter.matches_pattern("src/file.txt", "**/*.py") is False

    def test_matches_pattern_with_directory(self) -> None:
        """Test pattern matching with specific directory."""
        assert PathFilter.matches_pattern("tests/unit/test_foo.py", "**/unit/**") is True
        assert PathFilter.matches_pattern("tests/integration/test_bar.py", "**/unit/**") is False
