"""Tests for Rich table formatter."""

from unittest.mock import MagicMock

from rich.syntax import Syntax
from rich.table import Table

from prompt_unifier.output.rich_table_formatter import RichTableFormatter


class TestRichTableFormatter:
    """Tests for RichTableFormatter class."""

    def test_format_list_table_basic(self) -> None:
        """Test formatting a basic list table with items."""
        formatter = RichTableFormatter()

        # Create mock content objects
        content1 = MagicMock()
        content1.title = "Test Prompt"
        content1.tags = ["tag1", "tag2"]
        content1.version = "1.0.0"

        content2 = MagicMock()
        content2.title = "Another Prompt"
        content2.tags = []
        content2.version = "2.0.0"

        items = [
            (content1, "prompt", "/path/to/file1.md"),
            (content2, "rule", "/path/to/file2.md"),
        ]

        table = formatter.format_list_table(items)

        assert isinstance(table, Table)
        assert table.row_count == 2

    def test_format_list_table_empty(self) -> None:
        """Test formatting an empty list table."""
        formatter = RichTableFormatter()

        table = formatter.format_list_table([])

        assert isinstance(table, Table)
        assert table.row_count == 0

    def test_format_list_table_no_tags(self) -> None:
        """Test formatting with content that has no tags attribute."""
        formatter = RichTableFormatter()

        content = MagicMock()
        content.title = "No Tags Prompt"
        # Simulate no tags attribute
        del content.tags
        content.version = "1.0.0"

        items = [(content, "prompt", "/path/to/file.md")]

        table = formatter.format_list_table(items)

        assert isinstance(table, Table)
        assert table.row_count == 1

    def test_format_list_table_no_version(self) -> None:
        """Test formatting with content that has no version attribute."""
        formatter = RichTableFormatter()

        content = MagicMock(spec=["title", "tags"])
        content.title = "No Version Prompt"
        content.tags = ["tag"]

        items = [(content, "prompt", "/path/to/file.md")]

        table = formatter.format_list_table(items)

        assert isinstance(table, Table)
        assert table.row_count == 1

    def test_format_list_table_none_tags(self) -> None:
        """Test formatting with content that has None tags."""
        formatter = RichTableFormatter()

        content = MagicMock()
        content.title = "None Tags Prompt"
        content.tags = None
        content.version = "1.0.0"

        items = [(content, "prompt", "/path/to/file.md")]

        table = formatter.format_list_table(items)

        assert isinstance(table, Table)
        assert table.row_count == 1

    def test_format_status_table_basic(self) -> None:
        """Test formatting a basic status table."""
        formatter = RichTableFormatter()

        items = [
            {
                "name": "Test Prompt",
                "type": "prompt",
                "handler": "continue",
                "status": "deployed",
                "details": "All good",
            },
        ]

        table = formatter.format_status_table(items)

        assert isinstance(table, Table)
        assert table.row_count == 1

    def test_format_status_table_outdated_status(self) -> None:
        """Test formatting status table with outdated status (yellow)."""
        formatter = RichTableFormatter()

        items = [
            {
                "name": "Outdated Prompt",
                "type": "prompt",
                "handler": "continue",
                "status": "outdated",
                "details": "Needs update",
            },
        ]

        table = formatter.format_status_table(items)

        assert isinstance(table, Table)
        assert table.row_count == 1

    def test_format_status_table_missing_status(self) -> None:
        """Test formatting status table with missing status (red)."""
        formatter = RichTableFormatter()

        items = [
            {
                "name": "Missing Prompt",
                "type": "prompt",
                "handler": "continue",
                "status": "missing",
                "details": "Not found",
            },
        ]

        table = formatter.format_status_table(items)

        assert isinstance(table, Table)
        assert table.row_count == 1

    def test_format_status_table_failed_status(self) -> None:
        """Test formatting status table with failed status (bold red)."""
        formatter = RichTableFormatter()

        items = [
            {
                "name": "Failed Prompt",
                "type": "prompt",
                "handler": "continue",
                "status": "failed",
                "details": "Error occurred",
            },
        ]

        table = formatter.format_status_table(items)

        assert isinstance(table, Table)
        assert table.row_count == 1

    def test_format_status_table_multiple_statuses(self) -> None:
        """Test formatting status table with multiple different statuses."""
        formatter = RichTableFormatter()

        items = [
            {
                "name": "Deployed Item",
                "type": "prompt",
                "handler": "continue",
                "status": "deployed",
                "details": "OK",
            },
            {
                "name": "Outdated Item",
                "type": "rule",
                "handler": "cursor",
                "status": "outdated",
                "details": "Old version",
            },
            {
                "name": "Missing Item",
                "type": "prompt",
                "handler": "continue",
                "status": "missing",
                "details": "Not deployed",
            },
            {
                "name": "Failed Item",
                "type": "rule",
                "handler": "cursor",
                "status": "failed",
                "details": "Deploy error",
            },
        ]

        table = formatter.format_status_table(items)

        assert isinstance(table, Table)
        assert table.row_count == 4

    def test_format_status_table_no_details(self) -> None:
        """Test formatting status table with missing details field."""
        formatter = RichTableFormatter()

        items = [
            {
                "name": "No Details",
                "type": "prompt",
                "handler": "continue",
                "status": "deployed",
            },
        ]

        table = formatter.format_status_table(items)

        assert isinstance(table, Table)
        assert table.row_count == 1

    def test_format_status_table_empty(self) -> None:
        """Test formatting an empty status table."""
        formatter = RichTableFormatter()

        table = formatter.format_status_table([])

        assert isinstance(table, Table)
        assert table.row_count == 0

    def test_format_content_preview_default_language(self) -> None:
        """Test formatting content preview with default markdown language."""
        formatter = RichTableFormatter()

        content = "# Header\n\nSome **bold** text."

        syntax = formatter.format_content_preview(content)

        assert isinstance(syntax, Syntax)

    def test_format_content_preview_custom_language(self) -> None:
        """Test formatting content preview with custom language."""
        formatter = RichTableFormatter()

        content = "def hello():\n    print('Hello, World!')"

        syntax = formatter.format_content_preview(content, language="python")

        assert isinstance(syntax, Syntax)

    def test_format_content_preview_yaml(self) -> None:
        """Test formatting content preview with YAML language."""
        formatter = RichTableFormatter()

        content = "name: test\nversion: 1.0.0"

        syntax = formatter.format_content_preview(content, language="yaml")

        assert isinstance(syntax, Syntax)

    def test_format_content_preview_empty_content(self) -> None:
        """Test formatting empty content preview."""
        formatter = RichTableFormatter()

        syntax = formatter.format_content_preview("")

        assert isinstance(syntax, Syntax)
