"""Tests for RichTableFormatter validation table and SCAFF scoring."""

from pathlib import Path
from unittest.mock import MagicMock

from rich.table import Table

from prompt_unifier.models.validation import ValidationResult, ValidationSummary
from prompt_unifier.output.rich_table_formatter import RichTableFormatter


class TestRichTableFormatterScaff:
    """Tests for SCAFF scoring formatting in RichTableFormatter."""

    def test_format_validation_table_basic(self):
        """Test basic validation table formatting without SCAFF."""
        formatter = RichTableFormatter()

        result = MagicMock(spec=ValidationResult)
        result.status = "passed"
        result.title = "Test"
        result.file = Path("test.md")
        result.errors = []
        result.warnings = []
        result.scaff_score = None

        summary = MagicMock(spec=ValidationSummary)
        summary.results = [result]

        table = formatter.format_validation_table(summary, show_scaff=False)
        assert isinstance(table, Table)
        assert table.row_count == 1
        # Check columns count (Name, Status, Issues, Path) = 4
        assert len(table.columns) == 4

    def test_format_validation_table_with_scaff_high_score(self):
        """Test validation table with high SCAFF score (Green)."""
        formatter = RichTableFormatter()

        result = MagicMock(spec=ValidationResult)
        result.status = "passed"
        result.title = "High Score"
        result.file = Path("high.md")
        result.errors = []
        result.warnings = []

        scaff = MagicMock()
        scaff.total_score = 90
        c1 = MagicMock()
        c1.component_name = "specific"
        c1.score = 20
        scaff.components = [c1]

        result.scaff_score = scaff

        summary = MagicMock(spec=ValidationSummary)
        summary.results = [result]

        table = formatter.format_validation_table(summary, show_scaff=True)
        assert isinstance(table, Table)
        assert table.row_count == 1
        # Check columns count (Name, Status, SCAFF, S, C, A, F, F, Issues, Path) = 10
        assert len(table.columns) == 10

    def test_format_validation_table_with_scaff_medium_score(self):
        """Test validation table with medium SCAFF score (Yellow)."""
        formatter = RichTableFormatter()

        result = MagicMock(spec=ValidationResult)
        result.status = "passed"
        result.title = "Medium Score"
        result.file = Path("medium.md")
        result.errors = []
        result.warnings = []

        scaff = MagicMock()
        scaff.total_score = 60
        c1 = MagicMock()
        c1.component_name = "specific"
        c1.score = 15
        scaff.components = [c1]

        result.scaff_score = scaff

        summary = MagicMock(spec=ValidationSummary)
        summary.results = [result]

        table = formatter.format_validation_table(summary, show_scaff=True)
        assert isinstance(table, Table)

    def test_format_validation_table_with_scaff_low_score(self):
        """Test validation table with low SCAFF score (Red)."""
        formatter = RichTableFormatter()

        result = MagicMock(spec=ValidationResult)
        result.status = "failed"
        result.title = "Low Score"
        result.file = Path("low.md")
        result.errors = ["error"]
        result.warnings = ["warning"]

        scaff = MagicMock()
        scaff.total_score = 40
        c1 = MagicMock()
        c1.component_name = "specific"
        c1.score = 5
        scaff.components = [c1]

        result.scaff_score = scaff

        summary = MagicMock(spec=ValidationSummary)
        summary.results = [result]

        table = formatter.format_validation_table(summary, show_scaff=True)
        assert isinstance(table, Table)

    def test_format_validation_table_no_title(self):
        """Test validation table when title is missing."""
        formatter = RichTableFormatter()

        result = MagicMock(spec=ValidationResult)
        result.status = "passed"
        result.title = None
        result.file = Path("no_title.md")
        result.errors = []
        result.warnings = []
        result.scaff_score = None

        summary = MagicMock(spec=ValidationSummary)
        summary.results = [result]

        table = formatter.format_validation_table(summary, show_scaff=False)
        assert isinstance(table, Table)
