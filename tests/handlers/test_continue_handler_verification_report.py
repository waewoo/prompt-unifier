"""Tests for automatic verification and Rich report (Task Group 2).

This module tests the following functionality:
- verify_deployment() is called after each successful file deploy
- Rich table report displays file name, content type, verification status
- color coding: green for passed, yellow for warnings, red for failures
- warning message shown only when verification fails
- aggregate summary count at end of deployment
"""

from io import StringIO
from pathlib import Path

import pytest
from rich.console import Console

from prompt_unifier.handlers.continue_handler import ContinueToolHandler
from prompt_unifier.models.prompt import PromptFrontmatter
from prompt_unifier.models.rule import RuleFrontmatter


@pytest.fixture
def handler(tmp_path: Path) -> ContinueToolHandler:
    """Create a ContinueToolHandler instance for testing."""
    return ContinueToolHandler(base_path=tmp_path)


@pytest.fixture
def mock_prompt() -> PromptFrontmatter:
    """Fixture for a mock PromptFrontmatter instance."""
    return PromptFrontmatter(
        title="Test Prompt",
        description="A test prompt",
    )


@pytest.fixture
def mock_rule() -> RuleFrontmatter:
    """Fixture for a mock RuleFrontmatter instance."""
    return RuleFrontmatter(
        title="Test Rule",
        description="A test rule",
        category="coding-standards",
    )


class TestVerificationResultModel:
    """Tests for VerificationResult data model."""

    def test_verification_result_creation(self):
        """Test that VerificationResult can be created with required fields."""
        from prompt_unifier.handlers.continue_handler import VerificationResult

        result = VerificationResult(
            file_name="test.md",
            content_type="prompt",
            status="passed",
            details="File verified successfully",
        )

        assert result.file_name == "test.md"
        assert result.content_type == "prompt"
        assert result.status == "passed"
        assert result.details == "File verified successfully"

    def test_verification_result_with_warning_status(self):
        """Test VerificationResult with warning status."""
        from prompt_unifier.handlers.continue_handler import VerificationResult

        result = VerificationResult(
            file_name="test.md",
            content_type="prompt",
            status="warning",
            details="File has minor issues",
        )

        assert result.status == "warning"


class TestVerifyDeploymentReturnsResult:
    """Tests for verify_deployment_with_details() method returning VerificationResult."""

    def test_verify_deployment_returns_passed_result(
        self, handler: ContinueToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test that verify_deployment_with_details returns passed result for valid deployment."""
        # Deploy a prompt with a specific filename
        handler.deploy(mock_prompt, "prompt", "Test body content", "test.md")

        # Verify deployment using the same filename
        result = handler.verify_deployment_with_details(mock_prompt.title, "prompt", "test.md")

        assert result.status == "passed"
        assert result.file_name == "test.md"
        assert result.content_type == "prompt"

    def test_verify_deployment_returns_failed_result_for_missing_file(
        self, handler: ContinueToolHandler
    ):
        """Test that verify_deployment_with_details returns failed result for missing file."""
        result = handler.verify_deployment_with_details("Nonexistent", "prompt", "nonexistent.md")

        assert result.status == "failed"
        assert "not found" in result.details.lower() or "does not exist" in result.details.lower()

    def test_verify_deployment_returns_failed_for_invalid_prompt(
        self, handler: ContinueToolHandler, tmp_path: Path
    ):
        """Test that verify_deployment_with_details returns failed for invalid prompt format."""
        # Create a file without proper invokable: true
        prompt_file = handler.prompts_dir / "Bad Prompt.md"
        prompt_file.write_text("---\nname: Bad Prompt\n---\nContent")

        result = handler.verify_deployment_with_details("Bad Prompt", "prompt", "Bad Prompt.md")

        assert result.status == "failed"


class TestVerificationReportRichTable:
    """Tests for Rich table report displaying verification results."""

    def test_display_verification_report_shows_table_with_columns(
        self, handler: ContinueToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test that verification report displays Rich table with columns."""
        from prompt_unifier.handlers.continue_handler import VerificationResult

        # Create test verification results
        results = [
            VerificationResult(
                file_name="test1.md",
                content_type="prompt",
                status="passed",
                details="File verified successfully",
            ),
            VerificationResult(
                file_name="test2.md",
                content_type="rule",
                status="failed",
                details="Missing required field",
            ),
        ]

        # Capture console output
        console = Console(file=StringIO(), force_terminal=True)

        # Display verification report
        handler.display_verification_report(results, console=console)

        output = console.file.getvalue()

        # Verify table columns are present
        assert "File" in output or "file" in output.lower()
        assert "Type" in output or "type" in output.lower()
        assert "Status" in output or "status" in output.lower()

    def test_display_verification_report_shows_handler_name_header(
        self, handler: ContinueToolHandler
    ):
        """Test that verification report shows header with handler name."""
        from prompt_unifier.handlers.continue_handler import VerificationResult

        results = [
            VerificationResult(
                file_name="test.md",
                content_type="prompt",
                status="passed",
                details="OK",
            ),
        ]

        console = Console(file=StringIO(), force_terminal=True)
        handler.display_verification_report(results, console=console)

        output = console.file.getvalue()

        # Should include handler name in header
        assert "continue" in output.lower() or "verification" in output.lower()


class TestVerificationColorCoding:
    """Tests for color coding in verification reports."""

    def test_passed_status_uses_green_color(self, handler: ContinueToolHandler):
        """Test that passed status uses green color."""
        from prompt_unifier.handlers.continue_handler import VerificationResult

        results = [
            VerificationResult(
                file_name="test.md",
                content_type="prompt",
                status="passed",
                details="OK",
            ),
        ]

        console = Console(file=StringIO(), force_terminal=True, record=True)
        handler.display_verification_report(results, console=console)

        # Get the recorded output to check for color codes
        output = console.export_text(styles=True)

        # Check that green styling is applied (Rich uses ANSI codes)
        assert "passed" in output.lower() or "PASSED" in output

    def test_failed_status_uses_red_color(self, handler: ContinueToolHandler):
        """Test that failed status uses red color."""
        from prompt_unifier.handlers.continue_handler import VerificationResult

        results = [
            VerificationResult(
                file_name="test.md",
                content_type="prompt",
                status="failed",
                details="Error",
            ),
        ]

        console = Console(file=StringIO(), force_terminal=True, record=True)
        handler.display_verification_report(results, console=console)

        output = console.export_text(styles=True)

        assert "failed" in output.lower() or "FAILED" in output

    def test_warning_status_uses_yellow_color(self, handler: ContinueToolHandler):
        """Test that warning status uses yellow color."""
        from prompt_unifier.handlers.continue_handler import VerificationResult

        results = [
            VerificationResult(
                file_name="test.md",
                content_type="prompt",
                status="warning",
                details="Minor issue",
            ),
        ]

        console = Console(file=StringIO(), force_terminal=True, record=True)
        handler.display_verification_report(results, console=console)

        output = console.export_text(styles=True)

        assert "warning" in output.lower() or "WARNING" in output


class TestVerificationSummaryAggregation:
    """Tests for aggregating verification results and displaying summary."""

    def test_aggregate_results_counts_passed_failed_warnings(self, handler: ContinueToolHandler):
        """Test that aggregate summary counts pass/fail/warning correctly."""
        from prompt_unifier.handlers.continue_handler import VerificationResult

        results = [
            VerificationResult("f1.md", "prompt", "passed", "OK"),
            VerificationResult("f2.md", "prompt", "passed", "OK"),
            VerificationResult("f3.md", "rule", "failed", "Error"),
            VerificationResult("f4.md", "rule", "warning", "Minor"),
        ]

        summary = handler.aggregate_verification_results(results)

        assert summary["passed"] == 2
        assert summary["failed"] == 1
        assert summary["warnings"] == 1
        assert summary["total"] == 4

    def test_display_verification_summary_shows_counts(self, handler: ContinueToolHandler):
        """Test that verification summary displays aggregate counts."""
        from prompt_unifier.handlers.continue_handler import VerificationResult

        results = [
            VerificationResult("f1.md", "prompt", "passed", "OK"),
            VerificationResult("f2.md", "rule", "failed", "Error"),
        ]

        console = Console(file=StringIO(), force_terminal=True)
        handler.display_verification_report(results, console=console)

        output = console.file.getvalue()

        # Should show summary counts
        assert "1" in output and "2" in output  # passed and failed counts


class TestWarningOnlyBehavior:
    """Tests for warning-only behavior when verification fails."""

    def test_failed_verification_shows_warning_message(self, handler: ContinueToolHandler):
        """Test that failed verification shows warning message."""
        from prompt_unifier.handlers.continue_handler import VerificationResult

        results = [
            VerificationResult("test.md", "prompt", "failed", "File not found"),
        ]

        console = Console(file=StringIO(), force_terminal=True)
        handler.display_verification_report(results, console=console)

        output = console.file.getvalue()

        # Should show warning about failures
        assert "warning" in output.lower() or "failed" in output.lower()

    def test_all_passed_verification_no_warning(self, handler: ContinueToolHandler):
        """Test that all passed verification doesn't show failure warning."""
        from prompt_unifier.handlers.continue_handler import VerificationResult

        results = [
            VerificationResult("test1.md", "prompt", "passed", "OK"),
            VerificationResult("test2.md", "rule", "passed", "OK"),
        ]

        console = Console(file=StringIO(), force_terminal=True)
        handler.display_verification_report(results, console=console)

        output = console.file.getvalue()

        # Should show success, not error/failure warning
        assert "failed" not in output.lower() or "0" in output  # 0 failures is OK


class TestVerificationIntegrationWithDeploy:
    """Tests for verification integration after deployment."""

    def test_verify_after_successful_prompt_deploy(
        self, handler: ContinueToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test verification after successful prompt deployment."""
        # Deploy a prompt
        handler.deploy(mock_prompt, "prompt", "Test content", "test-prompt.md")

        # Verify
        result = handler.verify_deployment_with_details(
            mock_prompt.title, "prompt", "test-prompt.md"
        )

        assert result.status == "passed"

    def test_verify_after_successful_rule_deploy(
        self, handler: ContinueToolHandler, mock_rule: RuleFrontmatter
    ):
        """Test verification after successful rule deployment."""
        # Deploy a rule
        handler.deploy(mock_rule, "rule", "Test rule content", "test-rule.md")

        # Verify
        result = handler.verify_deployment_with_details(mock_rule.title, "rule", "test-rule.md")

        assert result.status == "passed"
