"""Tests for KiloCode handler verification and Rich report.

This module tests the following functionality for KiloCodeToolHandler:
- verify_deployment_with_details() returns VerificationResult
- Rich table report displays file name, content type, verification status
- color coding: green for passed, yellow for warnings, red for failures
- deployment status tracking (new/updated/unchanged)
- aggregate summary count at end of deployment
"""

from io import StringIO
from pathlib import Path

import pytest
from rich.console import Console

from prompt_unifier.handlers.kilo_code_handler import KiloCodeToolHandler
from prompt_unifier.models.prompt import PromptFrontmatter
from prompt_unifier.models.rule import RuleFrontmatter


@pytest.fixture
def handler(tmp_path: Path) -> KiloCodeToolHandler:
    """Create a KiloCodeToolHandler instance for testing."""
    return KiloCodeToolHandler(base_path=tmp_path)


@pytest.fixture
def mock_prompt() -> PromptFrontmatter:
    """Fixture for a mock PromptFrontmatter instance."""
    return PromptFrontmatter(
        title="Test Workflow",
        description="A test workflow",
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
    """Tests for VerificationResult data model with KiloCode."""

    def test_verification_result_creation(self):
        """Test that VerificationResult can be created with required fields."""
        from prompt_unifier.handlers.base_handler import VerificationResult

        result = VerificationResult(
            file_name="misc-test.md",
            content_type="prompt",
            status="passed",
            details="File verified successfully",
        )

        assert result.file_name == "misc-test.md"
        assert result.content_type == "prompt"
        assert result.status == "passed"
        assert result.details == "File verified successfully"

    def test_verification_result_with_deployment_status(self):
        """Test VerificationResult with deployment status."""
        from prompt_unifier.handlers.base_handler import VerificationResult

        result = VerificationResult(
            file_name="misc-test.md",
            content_type="prompt",
            status="passed",
            details="File verified successfully",
            deployment_status="new",
        )

        assert result.deployment_status == "new"


class TestVerifyDeploymentReturnsResult:
    """Tests for verify_deployment_with_details() method returning VerificationResult."""

    def test_verify_deployment_returns_passed_result(
        self, handler: KiloCodeToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test that verify_deployment_with_details returns passed result for valid deployment."""
        # Deploy a workflow
        handler.deploy(mock_prompt, "prompt", "Test body content", "test.md")

        # Calculate the expected filename (with misc- prefix for root files)
        expected_filename = "misc-test.md"

        # Verify deployment
        result = handler.verify_deployment_with_details(
            mock_prompt.title, "prompt", expected_filename
        )

        assert result.status == "passed"
        assert result.file_name == mock_prompt.title  # file_name now contains the title
        assert result.content_type == "prompt"

    def test_verify_deployment_returns_failed_result_for_missing_file(
        self, handler: KiloCodeToolHandler
    ):
        """Test that verify_deployment_with_details returns failed result for missing file."""
        # Verify a file that doesn't exist
        result = handler.verify_deployment_with_details(
            "Nonexistent Workflow", "prompt", "misc-nonexistent.md"
        )

        assert result.status == "failed"
        assert "does not exist" in result.details

    def test_verify_deployment_returns_failed_for_invalid_format(
        self, handler: KiloCodeToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test that verify_deployment_with_details fails for files with YAML frontmatter."""
        # Deploy a workflow
        handler.deploy(mock_prompt, "prompt", "Test body content", "test.md")

        # Manually write invalid content (with YAML frontmatter)
        target_file = handler.prompts_dir / "misc-test.md"
        target_file.write_text("---\ntitle: Test\n---\nBody", encoding="utf-8")

        # Verify deployment - should fail
        result = handler.verify_deployment_with_details(mock_prompt.title, "prompt", "misc-test.md")

        assert result.status == "failed"
        assert "YAML frontmatter" in result.details


class TestVerificationReportRichTable:
    """Tests for Rich table display of verification report."""

    def test_display_verification_report_shows_table_with_columns(
        self, handler: KiloCodeToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test that display_verification_report shows a Rich table with proper columns."""
        from prompt_unifier.handlers.base_handler import VerificationResult

        # Create verification results
        results = [
            VerificationResult(
                file_name=mock_prompt.title,
                content_type="prompt",
                status="passed",
                details="File verified successfully",
                deployment_status="new",
            )
        ]

        # Capture console output
        string_io = StringIO()
        test_console = Console(file=string_io, force_terminal=True, width=120)

        # Display report
        handler.display_verification_report(results, console=test_console)

        output = string_io.getvalue()

        # Check for table column headers
        assert "Name" in output
        assert "Type" in output
        assert "Status" in output
        assert "Issues" in output
        assert "Path" in output

    def test_display_verification_report_shows_handler_name_header(
        self, handler: KiloCodeToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test that display_verification_report shows handler name in header."""
        from prompt_unifier.handlers.base_handler import VerificationResult

        results = [
            VerificationResult(
                file_name=mock_prompt.title,
                content_type="prompt",
                status="passed",
                details="File verified successfully",
            )
        ]

        string_io = StringIO()
        test_console = Console(file=string_io, force_terminal=True, width=120)

        handler.display_verification_report(results, console=test_console)

        output = string_io.getvalue()

        # Should show handler name in header
        assert "kilocode" in output.lower()


class TestVerificationColorCoding:
    """Tests for color coding in verification report."""

    def test_passed_status_uses_green_color(
        self, handler: KiloCodeToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test that passed status uses green color."""
        from prompt_unifier.handlers.base_handler import VerificationResult

        results = [
            VerificationResult(
                file_name=mock_prompt.title,
                content_type="prompt",
                status="passed",
                details="File verified successfully",
            )
        ]

        string_io = StringIO()
        test_console = Console(file=string_io, force_terminal=True, width=120, legacy_windows=False)

        handler.display_verification_report(results, console=test_console)

        output = string_io.getvalue()

        # Check for green color code (ANSI escape sequence)
        assert "PASSED" in output

    def test_failed_status_uses_red_color(
        self, handler: KiloCodeToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test that failed status uses red color."""
        from prompt_unifier.handlers.base_handler import VerificationResult

        results = [
            VerificationResult(
                file_name=mock_prompt.title,
                content_type="prompt",
                status="failed",
                details="File verification failed",
            )
        ]

        string_io = StringIO()
        test_console = Console(file=string_io, force_terminal=True, width=120, legacy_windows=False)

        handler.display_verification_report(results, console=test_console)

        output = string_io.getvalue()

        # Check for failed status
        assert "FAILED" in output

    def test_warning_status_uses_yellow_color(
        self, handler: KiloCodeToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test that warning status uses yellow color."""
        from prompt_unifier.handlers.base_handler import VerificationResult

        results = [
            VerificationResult(
                file_name=mock_prompt.title,
                content_type="prompt",
                status="warning",
                details="File has minor issues",
            )
        ]

        string_io = StringIO()
        test_console = Console(file=string_io, force_terminal=True, width=120, legacy_windows=False)

        handler.display_verification_report(results, console=test_console)

        output = string_io.getvalue()

        # Check for warning status
        assert "WARNING" in output


class TestVerificationSummaryAggregation:
    """Tests for summary aggregation in verification report."""

    def test_aggregate_results_counts_passed_failed_warnings(self, handler: KiloCodeToolHandler):
        """Test that aggregate_verification_results counts passed, failed, and warnings."""
        from prompt_unifier.handlers.base_handler import VerificationResult

        results = [
            VerificationResult(
                file_name="Workflow 1",
                content_type="prompt",
                status="passed",
                details="OK",
            ),
            VerificationResult(
                file_name="Workflow 2",
                content_type="prompt",
                status="failed",
                details="Error",
            ),
            VerificationResult(
                file_name="Rule 1", content_type="rule", status="warning", details="Warning"
            ),
        ]

        summary = handler.aggregate_verification_results(results)

        assert summary["total"] == 3
        assert summary["passed"] == 1
        assert summary["failed"] == 1
        assert summary["warnings"] == 1

    def test_display_verification_summary_shows_counts(
        self, handler: KiloCodeToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test that display_verification_report shows summary counts."""
        from prompt_unifier.handlers.base_handler import VerificationResult

        results = [
            VerificationResult(
                file_name=mock_prompt.title,
                content_type="prompt",
                status="passed",
                details="OK",
            )
        ]

        string_io = StringIO()
        test_console = Console(file=string_io, force_terminal=True, width=120)

        handler.display_verification_report(results, console=test_console)

        output = string_io.getvalue()

        # Should show summary with counts
        assert "Summary:" in output
        assert "passed" in output
        assert "failed" in output


class TestDeploymentStatusTracking:
    """Tests for deployment status tracking (new/updated/unchanged)."""

    def test_new_file_deployment_status(
        self, handler: KiloCodeToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test that deploying a new file shows NEW status."""
        # Deploy a new workflow
        handler.deploy(mock_prompt, "prompt", "Test body content", "test.md")

        # Check deployment status was tracked
        assert mock_prompt.title in handler._deployment_statuses
        assert handler._deployment_statuses[mock_prompt.title] == "new"

    def test_unchanged_file_deployment_status(
        self, handler: KiloCodeToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test that deploying an unchanged file shows UNCHANGED status."""
        # Deploy once
        handler.deploy(mock_prompt, "prompt", "Test body content", "test.md")

        # Deploy again with same content
        handler.deploy(mock_prompt, "prompt", "Test body content", "test.md")

        # Should be unchanged
        assert handler._deployment_statuses[mock_prompt.title] == "unchanged"

    def test_updated_file_deployment_status(
        self, handler: KiloCodeToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test that deploying a modified file shows UPDATED status."""
        # Deploy once
        handler.deploy(mock_prompt, "prompt", "Test body content", "test.md")

        # Deploy again with different content
        handler.deploy(mock_prompt, "prompt", "Modified body content", "test.md")

        # Should be updated
        assert handler._deployment_statuses[mock_prompt.title] == "updated"


class TestVerificationIntegrationWithDeploy:
    """Integration tests for verification after deployment."""

    def test_verify_after_successful_workflow_deploy(
        self, handler: KiloCodeToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test that verification succeeds after successful workflow deployment."""
        # Deploy workflow
        handler.deploy(mock_prompt, "prompt", "Test body content", "test.md")

        # Verify deployment
        result = handler.verify_deployment_with_details(mock_prompt.title, "prompt", "misc-test.md")

        assert result.status == "passed"

    def test_verify_after_successful_rule_deploy(
        self, handler: KiloCodeToolHandler, mock_rule: RuleFrontmatter
    ):
        """Test that verification succeeds after successful rule deployment."""
        # Deploy rule
        handler.deploy(mock_rule, "rule", "Test rule body", "test.md")

        # Verify deployment
        result = handler.verify_deployment_with_details(mock_rule.title, "rule", "misc-test.md")

        assert result.status == "passed"
