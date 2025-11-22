"""Tests for ContinueToolHandler edge cases and error handling."""

from pathlib import Path
from unittest.mock import patch

import pytest

from prompt_unifier.handlers.continue_handler import (
    ContinueToolHandler,
    VerificationResult,
)
from prompt_unifier.models.prompt import PromptFrontmatter
from prompt_unifier.models.rule import RuleFrontmatter


@pytest.fixture
def handler_base_path(tmp_path: Path) -> Path:
    """Create a base path for handler testing."""
    return tmp_path / "handler_base"


@pytest.fixture
def handler(handler_base_path: Path) -> ContinueToolHandler:
    """Create a ContinueToolHandler instance."""
    return ContinueToolHandler(base_path=handler_base_path)


class TestValidateToolInstallationErrors:
    """Tests for validate_tool_installation error handling."""

    def test_validate_with_permission_error_on_write_test(self, tmp_path: Path):
        """Test validation fails when directory is not writable."""
        handler = ContinueToolHandler(base_path=tmp_path)

        # Mock the write test to raise PermissionError
        with patch.object(Path, "touch") as mock_touch:
            mock_touch.side_effect = PermissionError("Write test failed")

            with pytest.raises(PermissionError) as exc_info:
                handler.validate_tool_installation()

            assert "not writable" in str(exc_info.value)

    def test_validate_with_oserror_on_write_test(self, tmp_path: Path):
        """Test validation handles OSError during write test."""
        handler = ContinueToolHandler(base_path=tmp_path)

        # Mock the write test to raise OSError
        with patch.object(Path, "touch") as mock_touch:
            mock_touch.side_effect = OSError("Disk full")

            with pytest.raises(PermissionError) as exc_info:
                handler.validate_tool_installation()

            assert "not writable" in str(exc_info.value)

    def test_validate_with_permission_error_during_directory_creation(self, tmp_path: Path):
        """Test validation handles PermissionError during directory creation."""
        # Create handler first to set up directories
        handler = ContinueToolHandler(base_path=tmp_path)

        # Remove prompts_dir to trigger recreation
        import shutil

        shutil.rmtree(handler.prompts_dir)

        # Mock mkdir to raise PermissionError
        with patch.object(Path, "mkdir") as mock_mkdir:
            mock_mkdir.side_effect = PermissionError("Cannot create directory")

            with pytest.raises(PermissionError):
                handler.validate_tool_installation()


class TestRuleProcessingEdgeCases:
    """Tests for rule content processing edge cases."""

    def test_process_rule_with_description(self, handler: ContinueToolHandler):
        """Test processing rule with description field."""
        rule = RuleFrontmatter(
            title="Test Rule",
            description="Rule description",
            category="coding-standards",
        )

        result = handler._process_rule_content(rule, "Body content")

        assert "description: Rule description" in result
        assert "name: Test Rule" in result

    def test_process_rule_with_category(self, handler: ContinueToolHandler):
        """Test processing rule with category field."""
        rule = RuleFrontmatter(
            title="Test Rule",
            description="Description",
            category="coding-standards",
        )

        result = handler._process_rule_content(rule, "Body content")

        assert "category: coding-standards" in result

    def test_process_rule_with_version(self, handler: ContinueToolHandler):
        """Test processing rule with version field."""
        rule = RuleFrontmatter(
            title="Test Rule",
            description="Description",
            category="coding-standards",
            version="1.0.0",
        )

        result = handler._process_rule_content(rule, "Body content")

        assert "version: 1.0.0" in result


class TestVerificationEdgeCases:
    """Tests for deployment verification edge cases."""

    def test_verify_deployment_with_invalid_format(self, handler: ContinueToolHandler):
        """Test verification fails for file with invalid frontmatter format."""
        # Create file without proper frontmatter delimiters
        prompt_file = handler.prompts_dir / "invalid.md"
        prompt_file.write_text("No frontmatter here")

        result = handler.verify_deployment("invalid", "prompt")

        assert result is False

    def test_verify_deployment_with_unsupported_type(self, handler: ContinueToolHandler):
        """Test verification with unsupported content type returns False."""
        result = handler.verify_deployment("test", "unknown_type")

        assert result is False

    def test_verify_deployment_with_details_unsupported_type(self, handler: ContinueToolHandler):
        """Test verification_with_details for unsupported content type."""
        result = handler.verify_deployment_with_details("test", "unknown_type", "test.md")

        assert result.status == "failed"
        assert "Unsupported content type" in result.details

    def test_verify_deployment_with_details_file_read_error(self, handler: ContinueToolHandler):
        """Test verification_with_details handles file read errors."""
        # Create a file then mock read to fail
        prompt_file = handler.prompts_dir / "test.md"
        prompt_file.write_text("content")

        with patch.object(Path, "read_text") as mock_read:
            mock_read.side_effect = OSError("Read error")

            result = handler.verify_deployment_with_details("test", "prompt", "test.md")

            assert result.status == "failed"
            assert "Cannot read file" in result.details

    def test_verify_deployment_with_details_invalid_frontmatter_format(
        self, handler: ContinueToolHandler
    ):
        """Test verification_with_details for invalid frontmatter format."""
        prompt_file = handler.prompts_dir / "invalid.md"
        prompt_file.write_text("No proper frontmatter")

        result = handler.verify_deployment_with_details("invalid", "prompt", "invalid.md")

        assert result.status == "failed"
        assert "missing frontmatter delimiters" in result.details

    def test_verify_deployment_with_details_invalid_yaml_dict(self, handler: ContinueToolHandler):
        """Test verification_with_details for frontmatter that is not a dict."""
        prompt_file = handler.prompts_dir / "invalid.md"
        prompt_file.write_text("---\n- list item\n---\nContent")

        result = handler.verify_deployment_with_details("invalid", "prompt", "invalid.md")

        assert result.status == "failed"
        assert "not a dictionary" in result.details

    def test_verify_deployment_with_details_invalid_yaml_syntax(self, handler: ContinueToolHandler):
        """Test verification_with_details for invalid YAML syntax."""
        prompt_file = handler.prompts_dir / "invalid.md"
        prompt_file.write_text("---\ninvalid: yaml: syntax\n---\nContent")

        result = handler.verify_deployment_with_details("invalid", "prompt", "invalid.md")

        assert result.status == "failed"
        assert "Invalid YAML frontmatter" in result.details


class TestAggregateVerificationResults:
    """Tests for aggregate_verification_results edge cases."""

    def test_aggregate_with_warning_status(self, handler: ContinueToolHandler):
        """Test aggregation counts warning status correctly."""
        results = [
            VerificationResult("file1.md", "prompt", "passed", "OK"),
            VerificationResult("file2.md", "prompt", "warning", "Minor issue"),
            VerificationResult("file3.md", "prompt", "failed", "Error"),
        ]

        summary = handler.aggregate_verification_results(results)

        assert summary["passed"] == 1
        assert summary["warnings"] == 1
        assert summary["failed"] == 1
        assert summary["total"] == 3


class TestRemoveEmptyDirectoriesEdgeCases:
    """Tests for _remove_empty_directories error handling."""

    def test_remove_empty_directories_with_oserror(self, handler: ContinueToolHandler):
        """Test _remove_empty_directories handles OSError gracefully."""
        # Create nested empty directories
        empty_dir = handler.prompts_dir / "subdir"
        empty_dir.mkdir()

        # Mock rmdir to raise OSError
        with patch.object(Path, "rmdir") as mock_rmdir:
            mock_rmdir.side_effect = OSError("Cannot remove directory")

            # Should not raise, just skip
            handler._remove_empty_directories(handler.prompts_dir)


class TestRollbackEdgeCases:
    """Tests for rollback error handling."""

    def test_rollback_with_oserror_on_prompts(self, handler: ContinueToolHandler):
        """Test rollback handles OSError when restoring prompt backups."""
        # Create backup file
        backup_file = handler.prompts_dir / "test.md.bak"
        backup_file.write_text("backup content")

        # Mock rename to raise OSError
        with patch.object(Path, "rename") as mock_rename:
            mock_rename.side_effect = OSError("Cannot rename file")

            # Should not raise, just warn and continue
            handler.rollback()

    def test_rollback_with_filenotfound_on_rules(self, handler: ContinueToolHandler):
        """Test rollback handles FileNotFoundError when restoring rule backups."""
        # Create backup file
        backup_file = handler.rules_dir / "test.md.bak"
        backup_file.write_text("backup content")

        # Mock rename to raise FileNotFoundError
        with patch.object(Path, "rename") as mock_rename:
            mock_rename.side_effect = FileNotFoundError("File not found")

            # Should not raise, just warn and continue
            handler.rollback()

    def test_rollback_with_mixed_errors(self, handler: ContinueToolHandler):
        """Test rollback continues after errors in both directories."""
        # Create backup files in both directories
        prompts_backup = handler.prompts_dir / "prompt.md.bak"
        prompts_backup.write_text("prompt backup")
        rules_backup = handler.rules_dir / "rule.md.bak"
        rules_backup.write_text("rule backup")

        # Track calls to determine which directory is being processed
        call_count = [0]

        def side_effect_fn(*args):
            call_count[0] += 1
            if call_count[0] == 1:
                raise OSError("Prompt error")
            else:
                raise FileNotFoundError("Rule error")

        with patch.object(Path, "rename") as mock_rename:
            mock_rename.side_effect = side_effect_fn

            # Should not raise, process all files
            handler.rollback()


class TestPromptWithAllOptionalFields:
    """Tests for prompt processing with all optional fields."""

    def test_process_prompt_with_all_optional_fields(self, handler: ContinueToolHandler):
        """Test prompt processing includes all optional fields when present."""
        prompt = PromptFrontmatter(
            title="Full Prompt",
            description="Complete description",
            category="testing",
            version="2.0.0",
            tags=["python", "testing"],
            author="Test Author",
            language="python",
        )

        result = handler._process_prompt_content(prompt, "Body")

        assert "category: testing" in result
        assert "version: 2.0.0" in result
        assert "tags:" in result
        assert "author: Test Author" in result
        assert "language: python" in result
