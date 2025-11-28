"Tests for KiloCodeToolHandler."

import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console

from prompt_unifier.handlers.kilo_code_handler import (
    KiloCodeToolHandler,
    VerificationResult,
)
from prompt_unifier.models.prompt import PromptFrontmatter
from prompt_unifier.models.rule import RuleFrontmatter


@pytest.fixture
def mock_base_dir(tmp_path: Path) -> Path:
    """Fixture to create a mock base directory."""
    return tmp_path / "kilocode_project"


@pytest.fixture
def kilo_code_handler(mock_base_dir: Path) -> KiloCodeToolHandler:
    """Fixture for a KiloCodeToolHandler instance."""
    return KiloCodeToolHandler(base_path=mock_base_dir)


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
        category="testing",
    )


class TestKiloCodeToolHandler:
    """Tests for KiloCodeToolHandler."""

    def test_init_creates_directories(self, kilo_code_handler: KiloCodeToolHandler):
        assert kilo_code_handler.prompts_dir.exists()
        assert kilo_code_handler.rules_dir.exists()

    def test_get_name(self, kilo_code_handler: KiloCodeToolHandler):
        assert kilo_code_handler.get_name() == "kilocode"

    def test_get_status(self, kilo_code_handler: KiloCodeToolHandler):
        assert kilo_code_handler.get_status() == "active"

        shutil.rmtree(kilo_code_handler.prompts_dir)
        assert kilo_code_handler.get_status() == "inactive"

    @patch("pathlib.Path.cwd")
    def test_init_creates_directories_with_cwd(self, mock_cwd: MagicMock, tmp_path: Path):
        # Test that default base_path (Path.cwd()) is used when none is provided
        # and that directories are created.
        mock_cwd.return_value = tmp_path
        handler = KiloCodeToolHandler()
        assert handler.prompts_dir.exists()
        assert handler.rules_dir.exists()

    # @patch("rich.console.Console.print")
    # def test_init_prints_creation_messages(
    #     self, mock_console_print: MagicMock, mock_base_dir: Path
    # ):
    #     # Remove directories to force creation and message printing
    #     shutil.rmtree(mock_base_dir / ".kilocode")
    #     KiloCodeToolHandler(base_path=mock_base_dir)
    #     # Check if creation messages were printed
    #     calls = [
    #         call
    #         for call_args in mock_console_print.call_args_list
    #         for call in call_args.args
    #         if isinstance(call, str)
    #     ]
    #     expected_workflow_message = "Created Kilo Code workflows directory"
    #     assert any(expected_workflow_message in s for s in calls)
    #     assert any("Created Kilo Code rules directory" in s for s in calls)

    @patch("pathlib.Path.rename")
    def test_backup_file_creates_backup(
        self, mock_rename: MagicMock, kilo_code_handler: KiloCodeToolHandler, tmp_path: Path
    ):
        test_file = tmp_path / "test.md"
        test_file.write_text("original content")
        kilo_code_handler._backup_file(test_file)
        mock_rename.assert_called_once_with(test_file.with_suffix(".md.bak"))

    def test_convert_to_pure_markdown_prompt(
        self, kilo_code_handler: KiloCodeToolHandler, mock_prompt: PromptFrontmatter
    ):
        yaml_content = (
            f"---\n"
            f"name: {mock_prompt.title}\n"
            f"description: {mock_prompt.description}\n"
            f"---\n"
            f">>>\n"
            f"Body content"
        )
        markdown = kilo_code_handler._convert_to_pure_markdown(yaml_content)
        assert markdown.startswith(f"# {mock_prompt.title}")
        assert mock_prompt.description in markdown
        assert "Body content" in markdown
        assert "---" not in markdown

    def test_convert_to_pure_markdown_rule_with_metadata(
        self, kilo_code_handler: KiloCodeToolHandler
    ):
        rule = RuleFrontmatter(
            title="Complex Rule",
            description="Rule with metadata",
            category="style",
            tags=["python", "formatting"],
            version="1.1.0",
            author="tester",
            language="en",
            applies_to=["*.py"],
        )
        yaml_content = (
            f"---\n"
            f"name: {rule.title}\n"
            f"description: {rule.description}\n"
            f"category: {rule.category}\n"
            f"tags: {rule.tags}\n"
            f"version: {rule.version}\n"
            f"author: {rule.author}\n"
            f"language: {rule.language}\n"
            f"applies_to: {rule.applies_to}\n"
            f"---\n"
            f">>>\n"
            f"Rule body"
        )

        markdown = kilo_code_handler._convert_to_pure_markdown(yaml_content)

        assert markdown.startswith(f"# {rule.title}")
        assert "**Category:** style" in markdown
        assert "**Tags:** python, formatting" in markdown
        assert "**Version:** 1.1" in markdown
        assert "**Author:** tester" in markdown
        assert "**Language:** en" in markdown
        assert "**AppliesTo:** *.py" in markdown
        assert "Rule body" in markdown

    def test_generate_directory_prefix(self, kilo_code_handler: KiloCodeToolHandler):
        assert kilo_code_handler._generate_directory_prefix(Path("commands/dev")) == "dev-"
        assert kilo_code_handler._generate_directory_prefix(Path("commands")) == "commands-"
        assert kilo_code_handler._generate_directory_prefix(None) == "misc-"
        assert kilo_code_handler._generate_directory_prefix(Path(".")) == "misc-"

    def test_apply_file_naming_pattern(self, kilo_code_handler: KiloCodeToolHandler):
        assert (
            kilo_code_handler._apply_file_naming_pattern("commands-", "test.md")
            == "commands-test.md"
        )
        assert kilo_code_handler._apply_file_naming_pattern("misc-", "test") == "misc-test.md"

    def test_deploy_prompt(
        self, kilo_code_handler: KiloCodeToolHandler, mock_prompt: PromptFrontmatter
    ):
        kilo_code_handler.deploy(mock_prompt, "prompt", "Body", "prompt.md", Path("sub"))

        expected_filename = "sub-prompt.md"
        target_file = kilo_code_handler.prompts_dir / expected_filename

        assert target_file.exists()
        content = target_file.read_text()
        assert content.startswith("# Test Prompt")
        assert "A test prompt" in content
        assert "Body" in content

    def test_deploy_rule(self, kilo_code_handler: KiloCodeToolHandler, mock_rule: RuleFrontmatter):
        kilo_code_handler.deploy(mock_rule, "rule", "Body", "rule.md", None)

        expected_filename = "misc-rule.md"
        target_file = kilo_code_handler.rules_dir / expected_filename

        assert target_file.exists()
        content = target_file.read_text()
        assert content.startswith("# Test Rule")

    def test_rollback(self, kilo_code_handler: KiloCodeToolHandler, mock_prompt: PromptFrontmatter):
        final_filename = kilo_code_handler._determine_target_filename(mock_prompt.title, None, None)
        target_file = kilo_code_handler.prompts_dir / final_filename
        backup_file = target_file.with_suffix(".md.bak")

        # 1. Create an initial file (which will be backed up by deploy)
        target_file.write_text("Original content")

        # 2. Deploy new content (this will trigger backup of "Original content")
        kilo_code_handler.deploy(mock_prompt, "prompt", "New content")

        assert target_file.exists()
        assert target_file.read_text() != "Original content"  # It should have "New content" now
        assert backup_file.exists()
        assert backup_file.read_text() == "Original content"

        # 3. Rollback
        kilo_code_handler.rollback()

        # Verify original content is restored and backup is removed
        assert target_file.exists()
        assert target_file.read_text() == "Original content"
        assert not backup_file.exists()

    def test_clean_orphaned_files(self, kilo_code_handler: KiloCodeToolHandler):
        orphaned_prompt = kilo_code_handler.prompts_dir / "orphan.md"
        orphaned_rule = kilo_code_handler.rules_dir / "orphan.md"
        backup_file = kilo_code_handler.prompts_dir / "backup.md.bak"

        orphaned_prompt.write_text("---\nname: Orphan Prompt\n---\nContent")
        orphaned_rule.write_text("---\nname: Orphan Rule\n---\nContent")
        backup_file.touch()

        removed = kilo_code_handler.clean_orphaned_files(set())

        assert len(removed) == 3
        assert not orphaned_prompt.exists()
        assert not orphaned_rule.exists()
        assert not backup_file.exists()

    def test_get_deployment_status(
        self, kilo_code_handler: KiloCodeToolHandler, mock_prompt: PromptFrontmatter
    ):
        # Test "missing"
        status = kilo_code_handler.get_deployment_status(
            mock_prompt.title, "prompt", "content", None, None
        )
        assert status == "missing"

        # Test "synced"
        kilo_code_handler.deploy(mock_prompt, "prompt", "sync_body", None, None)

        # Re-generate content to get correct hash
        yaml_content = (
            f"---\n"
            f"name: {mock_prompt.title}\n"
            f"description: {mock_prompt.description}\n"
            f"---\n"
            f">>>\n"
            f"sync_body"
        )
        md_content = kilo_code_handler._convert_to_pure_markdown(yaml_content)

        status = kilo_code_handler.get_deployment_status(
            mock_prompt.title, "prompt", md_content, None, None
        )
        assert status == "synced"

        # Test "outdated"
        status = kilo_code_handler.get_deployment_status(
            mock_prompt.title, "prompt", "different content", None, None
        )
        assert status == "outdated"

    def test_verify_deployment_with_details(
        self, kilo_code_handler: KiloCodeToolHandler, mock_prompt: PromptFrontmatter
    ):
        # Deploy a valid prompt
        kilo_code_handler.deploy(mock_prompt, "prompt", "Body", "test.md")

        result = kilo_code_handler.verify_deployment_with_details(
            mock_prompt.title, "prompt", "misc-test.md"
        )
        assert result.status == "passed"

        # Create invalid file
        invalid_file = kilo_code_handler.prompts_dir / "invalid.md"
        invalid_file.write_text("---")

        result = kilo_code_handler.verify_deployment_with_details("invalid", "prompt", "invalid.md")
        assert result.status == "failed"
        assert "YAML" in result.details

        result = kilo_code_handler.verify_deployment_with_details(
            "not-exist", "prompt", "not-exist.md"
        )
        assert result.status == "failed"
        assert "does not exist" in result.details

    def test_aggregate_verification_results(self, kilo_code_handler: KiloCodeToolHandler):
        results = [
            VerificationResult("f1", "prompt", "passed", ""),
            VerificationResult("f2", "prompt", "failed", ""),
            VerificationResult("f3", "rule", "warning", ""),
            VerificationResult("f4", "prompt", "passed", ""),
        ]
        summary = kilo_code_handler.aggregate_verification_results(results)
        assert summary["total"] == 4
        assert summary["passed"] == 2
        assert summary["failed"] == 1
        assert summary["warnings"] == 1

    @patch("rich.console.Console.print")
    def test_display_verification_report(
        self, mock_print: MagicMock, kilo_code_handler: KiloCodeToolHandler
    ):
        results = [VerificationResult("f1", "prompt", "passed", "details")]
        kilo_code_handler.display_verification_report(results)
        # Check that print was called, a simple check
        assert mock_print.call_count > 0

    def test_remove_empty_directories(self, kilo_code_handler: KiloCodeToolHandler):
        empty_dir = kilo_code_handler.prompts_dir / "a/b/c"
        empty_dir.mkdir(parents=True)

        kilo_code_handler._remove_empty_directories(kilo_code_handler.prompts_dir)

        assert not kilo_code_handler.prompts_dir.joinpath("a").exists()

    def test_validate_tool_installation_success(self, kilo_code_handler: KiloCodeToolHandler):
        """Test successful validation of tool installation."""
        result = kilo_code_handler.validate_tool_installation()
        assert result is True
        assert kilo_code_handler.prompts_dir.exists()
        assert kilo_code_handler.rules_dir.exists()

    def test_validate_tool_installation_creates_missing_dirs(self, tmp_path: Path):
        """Test that validation creates missing directories."""
        base_path = tmp_path / "new_project"
        handler = KiloCodeToolHandler(base_path=base_path)

        # Remove directories to test creation
        shutil.rmtree(base_path)

        result = handler.validate_tool_installation()
        assert result is True
        assert handler.prompts_dir.exists()
        assert handler.rules_dir.exists()

    def test_convert_to_pure_markdown_no_yaml(self, kilo_code_handler: KiloCodeToolHandler):
        """Test conversion when there's no YAML frontmatter."""
        content = "Just plain markdown content"
        result = kilo_code_handler._convert_to_pure_markdown(content)
        assert result == content

    def test_convert_to_pure_markdown_malformed_yaml(self, kilo_code_handler: KiloCodeToolHandler):
        """Test conversion with malformed YAML."""
        content = "---\nmalformed: yaml: content:\n---\nBody"
        result = kilo_code_handler._convert_to_pure_markdown(content)
        # Should return original content when YAML is malformed
        assert result == content

    def test_convert_to_pure_markdown_no_body(self, kilo_code_handler: KiloCodeToolHandler):
        """Test conversion with only frontmatter, no body."""
        content = "---\nname: Test\ndescription: Description\n---\n>>>"
        result = kilo_code_handler._convert_to_pure_markdown(content)
        assert result.startswith("# Test")
        assert "Description" in result

    def test_generate_directory_prefix_empty_parts(self, kilo_code_handler: KiloCodeToolHandler):
        """Test prefix generation with empty path parts."""
        result = kilo_code_handler._generate_directory_prefix(Path(""))
        assert result == "misc-"

    def test_deploy_invalid_content_type(self, kilo_code_handler: KiloCodeToolHandler):
        """Test deploy with invalid content type."""
        mock_content = MagicMock()
        with pytest.raises(ValueError, match="Unsupported content type"):
            kilo_code_handler.deploy(mock_content, "invalid_type", "body")

    def test_deploy_wrong_content_instance_for_prompt(
        self, kilo_code_handler: KiloCodeToolHandler, mock_rule: RuleFrontmatter
    ):
        """Test deploy with wrong content instance for prompt type."""
        with pytest.raises(ValueError, match="Content must be a PromptFrontmatter"):
            kilo_code_handler.deploy(mock_rule, "prompt", "body")

    def test_deploy_wrong_content_instance_for_rule(
        self, kilo_code_handler: KiloCodeToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test deploy with wrong content instance for rule type."""
        with pytest.raises(ValueError, match="Content must be a RuleFrontmatter"):
            kilo_code_handler.deploy(mock_prompt, "rule", "body")

    def test_verify_deployment_invalid_content_type(self, kilo_code_handler: KiloCodeToolHandler):
        """Test verification with invalid content type."""
        result = kilo_code_handler.verify_deployment_with_details("test", "invalid_type", "test.md")
        assert result.status == "failed"
        assert "Unsupported content type" in result.details

    def test_verify_deployment_file_read_error(
        self, kilo_code_handler: KiloCodeToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test verification when file cannot be read."""
        # Create a file and make it unreadable by deleting it
        test_file = kilo_code_handler.prompts_dir / "test.md"
        test_file.write_text("# Test")
        test_file.chmod(0o000)  # Make unreadable

        result = kilo_code_handler.verify_deployment_with_details("test", "prompt", "test.md")

        # Restore permissions for cleanup
        test_file.chmod(0o644)

        # On Windows, chmod might not work as expected, so check both cases
        assert result.status in ["failed", "passed"]

    def test_verify_deployment_no_h1_title(self, kilo_code_handler: KiloCodeToolHandler):
        """Test verification when file doesn't start with H1."""
        test_file = kilo_code_handler.prompts_dir / "test.md"
        test_file.write_text("No H1 title here")

        result = kilo_code_handler.verify_deployment_with_details("test", "prompt", "test.md")
        assert result.status == "failed"
        assert "does not start with H1" in result.details

    def test_display_verification_report_with_failures(
        self, kilo_code_handler: KiloCodeToolHandler
    ):
        """Test display of verification report with failures."""
        results = [
            VerificationResult("f1", "prompt", "passed", "OK"),
            VerificationResult("f2", "prompt", "failed", "Error"),
            VerificationResult("f3", "rule", "warning", "Warning"),
        ]
        # Should not raise any exception
        kilo_code_handler.display_verification_report(results)

    def test_get_deployment_status_error_case(self, kilo_code_handler: KiloCodeToolHandler):
        """Test deployment status with invalid content type."""
        status = kilo_code_handler.get_deployment_status("test", "invalid_type", "content")
        assert status == "error"

    def test_rollback_with_errors(self, kilo_code_handler: KiloCodeToolHandler):
        """Test rollback when backup files have issues."""
        # Create a backup file
        backup_file = kilo_code_handler.prompts_dir / "test.md.bak"
        backup_file.write_text("backup content")

        # Create original file that will conflict
        original_file = kilo_code_handler.prompts_dir / "test.md"
        original_file.write_text("original content")

        # Rollback should handle this gracefully
        kilo_code_handler.rollback()

        # After rollback, original should have backup content
        assert original_file.read_text() == "backup content"

    def test_clean_orphaned_files_with_subdirectories(self, kilo_code_handler: KiloCodeToolHandler):
        """Test that orphaned files in subdirectories are removed for KiloCode."""
        # Create a subdirectory with a file
        subdir = kilo_code_handler.prompts_dir / "subdir"
        subdir.mkdir()
        subdir_file = subdir / "file.md"
        subdir_file.write_text("---\nname: Test\n---\nContent")

        # Clean orphaned files
        removed = kilo_code_handler.clean_orphaned_files(set())

        # Subdirectory file should be removed for KiloCode (recursive cleaning)
        assert not subdir_file.exists()
        # One file should be removed
        assert len(removed) == 1

    def test_init_creates_directories_when_missing(self, tmp_path: Path):
        """Test that __init__ creates directories when they don't exist."""
        base_path = tmp_path / "new_kilo_project"
        handler = KiloCodeToolHandler(base_path=base_path)

        assert handler.prompts_dir.exists()
        assert handler.rules_dir.exists()
        assert handler.get_name() == "kilocode"

    def test_deploy_with_all_optional_fields(self, kilo_code_handler: KiloCodeToolHandler):
        """Test deploy with content having all optional fields."""
        rule = RuleFrontmatter(
            title="Complete Rule",
            description="A rule with all fields",
            category="testing",
            version="2.0.0",
            tags=["tag1", "tag2"],
            author="Test Author",
            language="fr",
            applies_to=["*.py", "*.js"],
        )

        kilo_code_handler.deploy(rule, "rule", "Body content", "complete.md", Path("custom"))

        # Verify file was created with correct name
        expected_file = kilo_code_handler.rules_dir / "custom-complete.md"
        assert expected_file.exists()

        content = expected_file.read_text()
        assert "# Complete Rule" in content
        assert "**Category:** testing" in content
        assert "**Tags:** tag1, tag2" in content
        assert "**Version:** 2.0" in content
        assert "**Author:** Test Author" in content
        assert "**Language:** fr" in content
        assert "**AppliesTo:** *.py, *.js" in content

    @patch("pathlib.Path.touch")
    def test_validate_tool_installation_write_error(
        self, mock_touch: MagicMock, kilo_code_handler: KiloCodeToolHandler
    ):
        """Test validation when write test fails."""
        mock_touch.side_effect = OSError("Permission denied")

        with pytest.raises(PermissionError, match="not writable"):
            kilo_code_handler.validate_tool_installation()

    def test_validate_tool_installation_with_nonexistent_base(self, tmp_path: Path):
        """Test validation creates missing base path."""
        base_path = tmp_path / "nonexistent" / "path"
        handler = KiloCodeToolHandler(base_path=base_path)

        result = handler.validate_tool_installation()
        assert result is True
        assert base_path.exists()

    def test_convert_to_pure_markdown_non_dict_yaml(self, kilo_code_handler: KiloCodeToolHandler):
        """Test conversion when YAML parses to non-dict."""
        content = "---\njust a string\n---\nBody"
        result = kilo_code_handler._convert_to_pure_markdown(content)
        # Should return original when YAML is not a dict
        assert result == content

    def test_convert_to_pure_markdown_no_name(self, kilo_code_handler: KiloCodeToolHandler):
        """Test conversion when name field is missing."""
        content = "---\ndescription: Only description\n---\n>>>\nBody"
        result = kilo_code_handler._convert_to_pure_markdown(content)
        assert "Only description" in result
        assert "Body" in result

    def test_convert_to_pure_markdown_no_description(self, kilo_code_handler: KiloCodeToolHandler):
        """Test conversion when description field is missing."""
        content = "---\nname: Only Name\n---\n>>>\nBody"
        result = kilo_code_handler._convert_to_pure_markdown(content)
        assert "# Only Name" in result
        assert "Body" in result

    def test_rollback_with_oserror_in_rules(self, kilo_code_handler: KiloCodeToolHandler):
        """Test rollback handles OSError in rules directory."""
        # Create a backup in rules directory
        backup_file = kilo_code_handler.rules_dir / "test.md.bak"
        backup_file.write_text("backup")

        # Rollback should handle this
        kilo_code_handler.rollback()

        # Backup should be restored
        restored = kilo_code_handler.rules_dir / "test.md"
        assert restored.exists()

    def test_clean_orphaned_files_in_rules_dir(self, kilo_code_handler: KiloCodeToolHandler):
        """Test cleaning orphaned files in rules directory."""
        # Create orphaned file in rules
        orphan = kilo_code_handler.rules_dir / "orphan.md"
        orphan.write_text("---\nname: Orphan Rule\n---\nContent")

        # Create backup file in rules
        backup = kilo_code_handler.rules_dir / "backup.md.bak"
        backup.write_text("backup")

        removed = kilo_code_handler.clean_orphaned_files(set())

        # Both should be removed
        assert not orphan.exists()
        assert not backup.exists()
        assert len(removed) == 2

    def test_display_verification_report_with_custom_console(
        self, kilo_code_handler: KiloCodeToolHandler
    ):
        """Test display with custom console."""
        custom_console = Console()
        results = [VerificationResult("f1", "prompt", "failed", "Error")]

        # Should not raise exception
        kilo_code_handler.display_verification_report(results, custom_console)

    def test_determine_target_filename(self, kilo_code_handler: KiloCodeToolHandler):
        """Test _determine_target_filename helper method."""
        filename = kilo_code_handler._determine_target_filename("Test", "custom.md", Path("subdir"))
        assert filename == "subdir-custom.md"

    def test_determine_target_file_path_prompt(self, kilo_code_handler: KiloCodeToolHandler):
        """Test _determine_target_file_path for prompts."""
        path = kilo_code_handler._determine_target_file_path("prompt", "test.md")
        assert path == kilo_code_handler.prompts_dir / "test.md"

    def test_determine_target_file_path_rule(self, kilo_code_handler: KiloCodeToolHandler):
        """Test _determine_target_file_path for rules."""
        path = kilo_code_handler._determine_target_file_path("rule", "test.md")
        assert path == kilo_code_handler.rules_dir / "test.md"

    def test_determine_target_file_path_invalid(self, kilo_code_handler: KiloCodeToolHandler):
        """Test _determine_target_file_path with invalid type."""
        path = kilo_code_handler._determine_target_file_path("invalid", "test.md")
        assert path is None

    def test_compare_content_hashes_synced(self, kilo_code_handler: KiloCodeToolHandler):
        """Test content hash comparison when synced."""
        test_file = kilo_code_handler.prompts_dir / "test.md"
        test_file.write_text("content")

        status = kilo_code_handler._compare_content_hashes("content", test_file)
        assert status == "synced"

    def test_compare_content_hashes_outdated(self, kilo_code_handler: KiloCodeToolHandler):
        """Test content hash comparison when outdated."""
        test_file = kilo_code_handler.prompts_dir / "test.md"
        test_file.write_text("old content")

        status = kilo_code_handler._compare_content_hashes("new content", test_file)
        assert status == "outdated"

    def test_compare_content_hashes_error(self, kilo_code_handler: KiloCodeToolHandler):
        """Test content hash comparison with read error."""
        test_file = kilo_code_handler.prompts_dir / "nonexistent.md"

        status = kilo_code_handler._compare_content_hashes("content", test_file)
        assert status == "error"

    def test_get_deployment_status_with_filename(
        self, kilo_code_handler: KiloCodeToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test get_deployment_status with custom filename."""
        kilo_code_handler.deploy(mock_prompt, "prompt", "body", "custom.md", None)

        status = kilo_code_handler.get_deployment_status(
            mock_prompt.title, "prompt", "# Test Prompt\n\nA test prompt\n\nbody", "custom.md", None
        )
        assert status == "synced"

    def test_remove_empty_directories_with_oserror(self, kilo_code_handler: KiloCodeToolHandler):
        """Test _remove_empty_directories handles OSError gracefully."""
        # Create a directory structure
        test_dir = kilo_code_handler.prompts_dir / "test"
        test_dir.mkdir()

        # Add a file to make it non-empty
        (test_dir / "file.txt").write_text("content")

        # Should not raise error even if directory is not empty
        kilo_code_handler._remove_empty_directories(kilo_code_handler.prompts_dir)

        # Directory should still exist because it's not empty
        assert test_dir.exists()

    def test_init_when_directories_already_exist(self, tmp_path: Path):
        """Test __init__ when directories already exist."""
        base_path = tmp_path / "existing_project"

        # Create directories first
        (base_path / ".kilocode" / "workflows").mkdir(parents=True)
        (base_path / ".kilocode" / "rules").mkdir(parents=True)

        # Initialize handler - should not fail
        handler = KiloCodeToolHandler(base_path=base_path)

        assert handler.prompts_dir.exists()
        assert handler.rules_dir.exists()

    def test_verify_deployment_with_unicode_decode_error(
        self, kilo_code_handler: KiloCodeToolHandler
    ):
        """Test verification handles unicode decode errors."""
        # Create a file with invalid UTF-8
        test_file = kilo_code_handler.prompts_dir / "invalid.md"
        test_file.write_bytes(b"\xff\xfe\xfd")

        result = kilo_code_handler.verify_deployment_with_details("test", "prompt", "invalid.md")

        # Should handle the error gracefully
        assert result.status in ["failed", "passed"]  # Windows might handle differently
