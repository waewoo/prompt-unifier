"""Tests for ContinueToolHandler."""

import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from prompt_unifier.handlers.continue_handler import ContinueToolHandler
from prompt_unifier.models.prompt import PromptFrontmatter
from prompt_unifier.models.rule import RuleFrontmatter


@pytest.fixture
def mock_home_dir(tmp_path: Path) -> Path:
    """Fixture to create a mock home directory."""
    return tmp_path / "home"


@pytest.fixture
def continue_handler(mock_home_dir: Path) -> ContinueToolHandler:
    """Fixture for a ContinueToolHandler instance."""
    return ContinueToolHandler(base_path=mock_home_dir)


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


class TestContinueToolHandler:
    """Tests for ContinueToolHandler."""

    def test_init_creates_directories(self, continue_handler: ContinueToolHandler):
        assert continue_handler.prompts_dir.exists()
        assert continue_handler.rules_dir.exists()

    @patch("pathlib.Path.rename")
    def test_backup_file_creates_backup(
        self, mock_rename: MagicMock, continue_handler: ContinueToolHandler, tmp_path: Path
    ):
        test_file = tmp_path / "test.md"
        test_file.write_text("original content")
        continue_handler._backup_file(test_file)
        mock_rename.assert_called_once_with(test_file.with_suffix(".md.bak"))

    @patch("pathlib.Path.rename")
    def test_backup_file_does_not_backup_if_not_exists(
        self, mock_rename: MagicMock, continue_handler: ContinueToolHandler, tmp_path: Path
    ):
        test_file = tmp_path / "non_existent.md"
        continue_handler._backup_file(test_file)
        mock_rename.assert_not_called()

    def test_process_prompt_content_adds_invokable(
        self, continue_handler: ContinueToolHandler, mock_prompt: PromptFrontmatter
    ):
        processed_content = continue_handler._process_prompt_content(
            mock_prompt, "This is the content body."
        )
        # Verify the generated content directly
        assert "name: Test Prompt" in processed_content
        assert "description: A test prompt" in processed_content
        assert "invokable: true" in processed_content
        assert "This is the content body." in processed_content

    def test_process_prompt_content_retains_invokable_true(
        self, continue_handler: ContinueToolHandler, mock_prompt: PromptFrontmatter
    ):
        mock_prompt.invokable = True
        processed_content = continue_handler._process_prompt_content(
            mock_prompt, "This is the content body."
        )
        # Verify the generated content directly
        assert "name: Test Prompt" in processed_content
        assert "description: A test prompt" in processed_content
        assert "invokable: true" in processed_content
        assert "This is the content body." in processed_content

    def test_process_prompt_content_overwrites_invokable_false(
        self, continue_handler: ContinueToolHandler, mock_prompt: PromptFrontmatter
    ):
        mock_prompt.invokable = False
        processed_content = continue_handler._process_prompt_content(
            mock_prompt, "This is the content body."
        )
        # Verify the generated content directly
        assert "name: Test Prompt" in processed_content
        assert "description: A test prompt" in processed_content
        assert "invokable: true" in processed_content
        assert "This is the content body." in processed_content

    def test_process_rule_content(
        self, continue_handler: ContinueToolHandler, mock_rule: RuleFrontmatter
    ):
        processed_content = continue_handler._process_rule_content(
            mock_rule, "This is the content body."
        )
        # Verify the generated content directly
        assert "name: Test Rule" in processed_content
        assert "description: A test rule" in processed_content
        assert "alwaysApply: false" in processed_content
        assert "category: coding-standards" in processed_content
        assert "version: 1.0.0" in processed_content
        assert "This is the content body." in processed_content

    def test_deploy_prompt_creates_file(
        self, continue_handler: ContinueToolHandler, mock_prompt: PromptFrontmatter
    ):
        continue_handler.deploy(mock_prompt, "prompt", "This is the content body.")
        target_file = continue_handler.prompts_dir / f"{mock_prompt.title}.md"
        assert target_file.exists()
        content = target_file.read_text()
        # Verify the generated content directly
        assert "name: Test Prompt" in content
        assert "description: A test prompt" in content
        assert "invokable: true" in content
        assert "This is the content body." in content

    def test_deploy_rule_creates_file(
        self, continue_handler: ContinueToolHandler, mock_rule: RuleFrontmatter
    ):
        continue_handler.deploy(mock_rule, "rule", "This is the content body.")
        target_file = continue_handler.rules_dir / f"{mock_rule.title}.md"
        assert target_file.exists()
        content = target_file.read_text()
        # Verify the generated content directly
        assert "name: Test Rule" in content
        assert "description: A test rule" in content
        assert "alwaysApply: false" in content
        assert "category: coding-standards" in content
        assert "version: 1.0.0" in content
        assert "This is the content body." in content

    def test_deploy_with_unsupported_type_raises_error(
        self, continue_handler: ContinueToolHandler, mock_prompt: PromptFrontmatter
    ):
        with pytest.raises(ValueError, match="Unsupported content type"):
            continue_handler.deploy(mock_prompt, "unsupported", "This is the content body.")

    def test_deploy_with_wrong_content_type_raises_error(
        self, continue_handler: ContinueToolHandler, mock_prompt: PromptFrontmatter
    ):
        with pytest.raises(ValueError, match="Content must be a RuleFrontmatter instance"):
            continue_handler.deploy(mock_prompt, "rule", "This is the content body.")

    def test_get_status_active(self, continue_handler: ContinueToolHandler):
        assert continue_handler.get_status() == "active"

    def test_get_status_inactive(self, continue_handler: ContinueToolHandler, mock_home_dir: Path):
        import shutil

        shutil.rmtree(continue_handler.prompts_dir)
        assert continue_handler.get_status() == "inactive"

    def test_get_name(self, continue_handler: ContinueToolHandler):
        assert continue_handler.get_name() == "continue"

    def test_verify_deployment_prompt_success(
        self, continue_handler: ContinueToolHandler, mock_prompt: PromptFrontmatter
    ):
        continue_handler.deploy(mock_prompt, "prompt", "This is the content body.")
        assert continue_handler.verify_deployment(mock_prompt.title, "prompt") is True

    def test_verify_deployment_rule_success(
        self, continue_handler: ContinueToolHandler, mock_rule: RuleFrontmatter
    ):
        continue_handler.deploy(mock_rule, "rule", "This is the content body.")
        assert continue_handler.verify_deployment(mock_rule.title, "rule") is True

    def test_verify_deployment_not_found(self, continue_handler: ContinueToolHandler):
        assert continue_handler.verify_deployment("non-existent", "prompt") is False

    def test_verify_deployment_prompt_missing_invokable(
        self, continue_handler: ContinueToolHandler, mock_prompt: PromptFrontmatter
    ):
        # Deploy a prompt without invokable: true (simulate external creation)
        target_file = continue_handler.prompts_dir / f"{mock_prompt.title}.md"
        target_file.write_text(f"---\ntitle: {mock_prompt.title}\n---\nThis is the content body.")
        assert continue_handler.verify_deployment(mock_prompt.title, "prompt") is False

    def test_deploy_prompt_with_existing_file_creates_backup(
        self, continue_handler: ContinueToolHandler, mock_prompt: PromptFrontmatter
    ):
        target_file = continue_handler.prompts_dir / f"{mock_prompt.title}.md"
        target_file.write_text("initial content")
        backup_file = target_file.with_suffix(".md.bak")

        continue_handler.deploy(mock_prompt, "prompt", "This is the content body.")

        assert target_file.exists()
        assert backup_file.exists()
        assert backup_file.read_text() == "initial content"

    def test_verify_deployment_invalid_content_type(self, tmp_path: Path):
        """Test verify_deployment with invalid content type."""
        handler = ContinueToolHandler(base_path=tmp_path)
        result = handler.verify_deployment("test", "invalid_type")
        assert result is False

    def test_verify_deployment_rule_missing_file(self, tmp_path: Path):
        """Test verify_deployment for a rule that doesn't exist."""
        handler = ContinueToolHandler(base_path=tmp_path)
        result = handler.verify_deployment("non_existent_rule", "rule")
        assert result is False

    def test_verify_deployment_rule_invalid_format(self, tmp_path: Path):
        """Test verify_deployment for a rule with invalid format."""
        handler = ContinueToolHandler(base_path=tmp_path)

        # Create a rule file without valid YAML format
        rule_file = handler.rules_dir / "test_rule.md"
        rule_file.write_text("Invalid content without frontmatter")

        result = handler.verify_deployment("test_rule", "rule")
        assert result is True  # Rules don't have strict validation like prompts

    def test_verify_deployment_prompt_invalid_yaml(self, tmp_path: Path):
        """Test verify_deployment for a prompt with invalid YAML."""
        handler = ContinueToolHandler(base_path=tmp_path)

        # Create a prompt file with invalid YAML
        prompt_file = handler.prompts_dir / "test_prompt.md"
        prompt_file.write_text("""---
nom: test
  description: test
invalid yaml
---
content""")

        result = handler.verify_deployment("test_prompt", "prompt")
        assert result is False  # Invalid YAML should fail

    def test_verify_deployment_prompt_no_invokable_field(self, tmp_path: Path):
        """Test verify_deployment for a prompt without invokable field."""
        handler = ContinueToolHandler(base_path=tmp_path)

        # Create a prompt file without invokable field
        prompt_file = handler.prompts_dir / "test_prompt.md"
        prompt_file.write_text("""---
name: test_prompt
description: A test prompt
---
content""")

        result = handler.verify_deployment("test_prompt", "prompt")
        assert result is False  # Missing invokable field

    def test_verify_deployment_prompt_invokable_false(self, tmp_path: Path):
        """Test verify_deployment for a prompt with invokable: false."""
        handler = ContinueToolHandler(base_path=tmp_path)

        # Create a prompt file with invokable: false
        prompt_file = handler.prompts_dir / "test_prompt.md"
        prompt_file.write_text("""---
name: test_prompt
description: A test prompt
invokable: false
---
content""")

        result = handler.verify_deployment("test_prompt", "prompt")
        assert result is False  # invokable should be true

    def test_rollback_multiple_files(self, tmp_path: Path):
        """Test rollback with multiple backup files."""
        handler = ContinueToolHandler(base_path=tmp_path)

        # Create multiple files with backups
        prompt_file1 = handler.prompts_dir / "prompt1.md"
        prompt_file2 = handler.prompts_dir / "prompt2.md"
        rule_file1 = handler.rules_dir / "rule1.md"

        # Create original files
        prompt_file1.write_text("original prompt 1")
        prompt_file2.write_text("original prompt 2")
        rule_file1.write_text("original rule 1")

        # Create backups
        prompt_backup1 = prompt_file1.with_suffix(".md.bak")
        prompt_backup2 = prompt_file2.with_suffix(".md.bak")
        rule_backup1 = rule_file1.with_suffix(".md.bak")

        prompt_backup1.write_text("backup prompt 1")
        prompt_backup2.write_text("backup prompt 2")
        rule_backup1.write_text("backup rule 1")

        # Rename originals to simulate backup
        prompt_file1.rename(prompt_backup1.with_suffix(".tmp"))
        prompt_file2.rename(prompt_backup2.with_suffix(".tmp"))
        rule_file1.rename(rule_backup1.with_suffix(".tmp"))

        # Create new files (simulating deployment)
        prompt_file1.write_text("new prompt 1")
        prompt_file2.write_text("new prompt 2")
        rule_file1.write_text("new rule 1")

        # Execute rollback
        handler.rollback()

        # Verify backups were restored
        assert prompt_file1.read_text() == "backup prompt 1"
        assert prompt_file2.read_text() == "backup prompt 2"
        assert rule_file1.read_text() == "backup rule 1"

        # Verify backups were removed
        assert not prompt_backup1.exists()
        assert not prompt_backup2.exists()
        assert not rule_backup1.exists()

    def test_rollback_no_backups(self, tmp_path: Path):
        """Test rollback when there are no backups."""
        handler = ContinueToolHandler(base_path=tmp_path)

        # Ensure there are no backups
        for backup in handler.prompts_dir.glob("*.bak"):
            backup.unlink()
        for backup in handler.rules_dir.glob("*.bak"):
            backup.unlink()

        # Execute rollback - should not crash
        handler.rollback()

        # Verify there are still no backups
        assert len(list(handler.prompts_dir.glob("*.bak"))) == 0
        assert len(list(handler.rules_dir.glob("*.bak"))) == 0

    def test_rollback_mixed_backups(self, tmp_path: Path):
        """Test rollback with mixed backups (some exist, some don't)."""
        handler = ContinueToolHandler(base_path=tmp_path)

        # Create only one backup
        prompt_file = handler.prompts_dir / "prompt1.md"
        prompt_backup = prompt_file.with_suffix(".md.bak")

        prompt_backup.write_text("backup content")
        prompt_file.write_text("new content")

        # Execute rollback
        handler.rollback()

        # Verify backup was restored
        assert prompt_file.read_text() == "backup content"
        assert not prompt_backup.exists()

    def test_process_prompt_content_with_all_fields(self, tmp_path: Path):
        """Test _process_prompt_content with all optional fields."""
        handler = ContinueToolHandler(base_path=tmp_path)

        prompt = PromptFrontmatter(
            title="Complete Prompt",
            description="A complete prompt with all fields",
            category="testing",
            version="2.0.0",
            tags=["python", "test"],
            author="Test Author",
            language="en",
        )

        processed = handler._process_prompt_content(prompt, "Test content")

        # Verify all fields are present
        assert "name: Complete Prompt" in processed
        assert "description: A complete prompt with all fields" in processed
        assert "category: testing" in processed
        assert "version: 2.0.0" in processed
        assert "tags:" in processed and "python" in processed and "test" in processed
        assert "author: Test Author" in processed
        assert "language: en" in processed
        assert "invokable: true" in processed
        assert "Test content" in processed

    def test_process_rule_content_with_all_fields(self, tmp_path: Path):
        """Test _process_rule_content with all optional fields."""
        handler = ContinueToolHandler(base_path=tmp_path)

        rule = RuleFrontmatter(
            title="Complete Rule",
            description="A complete rule with all fields",
            category="coding-standards",
            version="1.5.0",
            tags=["python", "style"],
            author="Rule Author",
            language="fr",
            applies_to=["*.py", "*.js"],
        )

        processed = handler._process_rule_content(rule, "Rule content")

        # Verify all fields are present
        assert "name: Complete Rule" in processed
        assert "description: A complete rule with all fields" in processed
        assert "category: coding-standards" in processed
        assert "version: 1.5.0" in processed
        assert "tags:" in processed and "python" in processed and "style" in processed
        assert "author: Rule Author" in processed
        assert "language: fr" in processed
        assert "globs:" in processed and "*.py" in processed and "*.js" in processed
        assert "alwaysApply: false" in processed
        assert "Rule content" in processed

    def test_deploy_prompt_with_complex_content(self, tmp_path: Path):
        """Test deploy with a prompt having complex content."""
        handler = ContinueToolHandler(base_path=tmp_path)

        prompt = PromptFrontmatter(
            title="Complex Prompt",
            description="A prompt with special characters and multiline content",
            version="1.0.0",
        )

        complex_content = """This is a complex prompt with:
- Special characters: àáâãäåæçèéêë
- Code blocks:
```python
def hello():
    print("Hello, world!")
```
- Multiple paragraphs

And more content here."""

        handler.deploy(prompt, "prompt", complex_content)

        # Verify file was created
        target_file = handler.prompts_dir / "Complex Prompt.md"
        assert target_file.exists()

        # Verify content
        content = target_file.read_text()
        assert "name: Complex Prompt" in content
        assert "invokable: true" in content
        assert complex_content in content

    def test_deploy_rule_with_complex_content(self, tmp_path: Path):
        """Test deploy with a rule having complex content."""
        handler = ContinueToolHandler(base_path=tmp_path)

        rule = RuleFrontmatter(
            title="Complex Rule",
            description="A rule with special characters and multiline content",
            category="coding-standards",
            applies_to=["*.py", "*.java", "*.cpp"],
            version="2.0.0",
        )

        complex_content = """This is a complex rule with:
- Special characters: àáâãäåæçèéêë
- Code examples:
```python
# This is a comment
def function():
    pass
```
- Multiple sections

More content here."""

        handler.deploy(rule, "rule", complex_content)

        # Verify file was created
        target_file = handler.rules_dir / "Complex Rule.md"
        assert target_file.exists()

        # Verify content
        content = target_file.read_text()
        assert "name: Complex Rule" in content
        assert "globs:" in content and "*.py" in content
        assert complex_content in content

    def test_backup_file_with_special_characters(self, tmp_path: Path):
        """Test _backup_file with special file names."""
        handler = ContinueToolHandler(base_path=tmp_path)

        # Create a file with special characters
        special_file = handler.prompts_dir / "special-chars_123.md"
        special_file.write_text("content with special chars")

        # Create backup
        handler._backup_file(special_file)

        # Verify backup was created
        backup_file = special_file.with_suffix(".md.bak")
        assert backup_file.exists()
        assert backup_file.read_text() == "content with special chars"
        assert not special_file.exists()  # Original should have been renamed

    def test_get_status_with_missing_directories(self, tmp_path: Path):
        """Test get_status when directories are missing."""
        handler = ContinueToolHandler(base_path=tmp_path)

        # Remove directories
        if handler.prompts_dir.exists():
            shutil.rmtree(handler.prompts_dir)
        if handler.rules_dir.exists():
            shutil.rmtree(handler.rules_dir)

        status = handler.get_status()
        assert status == "inactive"

    def test_init_with_custom_base_path(self, tmp_path: Path):
        """Test initialization with custom base path."""
        custom_base = Path("/tmp/custom_home")
        handler = ContinueToolHandler(base_path=custom_base)

        # Verify paths are correct
        assert handler.base_path == custom_base
        assert handler.prompts_dir == custom_base / ".continue" / "prompts"
        assert handler.rules_dir == custom_base / ".continue" / "rules"

        # Verify directories were created
        assert handler.prompts_dir.exists()
        assert handler.rules_dir.exists()

    def test_deploy_with_empty_content(self, tmp_path: Path):
        """Test deploy with empty content."""
        handler = ContinueToolHandler(base_path=tmp_path)

        prompt = PromptFrontmatter(
            title="Empty Content Prompt", description="A prompt with empty content", version="1.0.0"
        )

        handler.deploy(prompt, "prompt", "")

        # Verify file was created
        target_file = handler.prompts_dir / "Empty Content Prompt.md"
        assert target_file.exists()

        # Verify content
        content = target_file.read_text()
        assert "name: Empty Content Prompt" in content
        assert content.endswith("\n---\n")  # Body should be empty after separator

    def test_deploy_with_unicode_content(self, tmp_path: Path):
        """Test deploy with unicode content."""
        handler = ContinueToolHandler(base_path=tmp_path)

        prompt = PromptFrontmatter(
            title="Unicode Prompt", description="A prompt with unicode content", version="1.0.0"
        )

        unicode_content = "Content with unicode characters: 🚀 🎉 💻 àáâãäåæçèéêë"

        handler.deploy(prompt, "prompt", unicode_content)

        # Verify file was created
        target_file = handler.prompts_dir / "Unicode Prompt.md"
        assert target_file.exists()

        # Verify content
        content = target_file.read_text()
        assert unicode_content in content

    def test_process_prompt_content_yaml_order(self, tmp_path: Path):
        """Test that YAML field order is respected."""
        handler = ContinueToolHandler(base_path=tmp_path)

        prompt = PromptFrontmatter(
            title="Order Test",
            description="Testing field order",
            category="testing",
            version="1.0.0",
            tags=["test"],
        )

        processed = handler._process_prompt_content(prompt, "content")

        # Order should be: name, description, invokable, then optional fields
        lines = processed.split("\n")

        # Find positions of key fields
        name_idx = next(i for i, line in enumerate(lines) if line.startswith("name:"))
        desc_idx = next(i for i, line in enumerate(lines) if line.startswith("description:"))
        inv_idx = next(i for i, line in enumerate(lines) if line.startswith("invokable:"))

        # Verify basic order
        assert name_idx < desc_idx < inv_idx

    def test_process_rule_content_yaml_order(self, tmp_path: Path):
        """Test that YAML field order is respected for rules."""
        handler = ContinueToolHandler(base_path=tmp_path)

        rule = RuleFrontmatter(
            title="Rule Order Test",
            description="Testing rule field order",
            category="testing",
            version="1.0.0",
            applies_to=["*.py"],
        )

        processed = handler._process_rule_content(rule, "content")

        # Order should be: name, description, globs, alwaysApply, then optional fields
        lines = processed.split("\n")

        # Find positions of key fields
        name_idx = next(i for i, line in enumerate(lines) if line.startswith("name:"))
        desc_idx = next(i for i, line in enumerate(lines) if line.startswith("description:"))
        globs_idx = next(i for i, line in enumerate(lines) if line.startswith("globs:"))
        always_idx = next(i for i, line in enumerate(lines) if line.startswith("alwaysApply:"))

        # Verify basic order
        assert name_idx < desc_idx < globs_idx < always_idx


class TestFilenamePreservation:
    """Tests for preserving original filenames during deployment."""

    def test_deploy_prompt_with_source_filename(
        self, continue_handler: ContinueToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test that deploy preserves original filename when provided."""
        source_filename = "Python Code Refactoring Expert.md"
        continue_handler.deploy(
            mock_prompt, "prompt", "Body content", source_filename=source_filename
        )

        # Should use source filename, not title
        target_file = continue_handler.prompts_dir / source_filename
        assert target_file.exists()

        # Should NOT create file with title-based name
        title_based_file = continue_handler.prompts_dir / f"{mock_prompt.title}.md"
        assert not title_based_file.exists() or title_based_file == target_file

    def test_deploy_rule_with_source_filename(
        self, continue_handler: ContinueToolHandler, mock_rule: RuleFrontmatter
    ):
        """Test that deploy preserves original filename for rules."""
        source_filename = "backend-python-packages.md"
        continue_handler.deploy(mock_rule, "rule", "Body content", source_filename=source_filename)

        # Should use source filename
        target_file = continue_handler.rules_dir / source_filename
        assert target_file.exists()

        # Should NOT create file with title-based name
        title_based_file = continue_handler.rules_dir / f"{mock_rule.title}.md"
        assert not title_based_file.exists() or title_based_file == target_file

    def test_deploy_without_source_filename_uses_title(
        self, continue_handler: ContinueToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test backward compatibility: without source_filename, uses title."""
        continue_handler.deploy(mock_prompt, "prompt", "Body content")

        # Should fall back to title-based naming
        target_file = continue_handler.prompts_dir / f"{mock_prompt.title}.md"
        assert target_file.exists()

    def test_deploy_source_filename_without_extension_adds_md(
        self, continue_handler: ContinueToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test that .md extension is added if missing."""
        source_filename = "my-custom-prompt"
        continue_handler.deploy(
            mock_prompt, "prompt", "Body content", source_filename=source_filename
        )

        # Should add .md extension
        target_file = continue_handler.prompts_dir / "my-custom-prompt.md"
        assert target_file.exists()

    def test_deploy_source_filename_with_spaces(
        self, continue_handler: ContinueToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test that filenames with spaces are preserved."""
        source_filename = "My Custom Prompt With Spaces.md"
        continue_handler.deploy(
            mock_prompt, "prompt", "Body content", source_filename=source_filename
        )

        # Should preserve spaces in filename
        target_file = continue_handler.prompts_dir / source_filename
        assert target_file.exists()
        assert " " in target_file.name

    def test_deploy_source_filename_with_special_chars(
        self, continue_handler: ContinueToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test that special characters in filenames are preserved."""
        source_filename = "Python-Code_Refactoring.Expert.md"
        continue_handler.deploy(
            mock_prompt, "prompt", "Body content", source_filename=source_filename
        )

        # Should preserve special chars
        target_file = continue_handler.prompts_dir / source_filename
        assert target_file.exists()
        assert target_file.name == source_filename


class TestCleanOrphanedFiles:
    """Tests for cleaning orphaned files in destination."""

    def test_clean_orphaned_prompts(
        self, continue_handler: ContinueToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test that orphaned prompts are removed."""
        # Deploy a prompt
        continue_handler.deploy(mock_prompt, "prompt", "Body")

        # Create an orphaned prompt
        orphaned_file = continue_handler.prompts_dir / "orphaned-prompt.md"
        orphaned_file.write_text("orphaned content")

        # Clean with only the deployed file in the set
        deployed = {f"{mock_prompt.title}.md"}
        removed = continue_handler.clean_orphaned_files(deployed)

        assert removed == 1
        assert not orphaned_file.exists()

    def test_clean_orphaned_rules(
        self, continue_handler: ContinueToolHandler, mock_rule: RuleFrontmatter
    ):
        """Test that orphaned rules are removed."""
        # Deploy a rule
        continue_handler.deploy(mock_rule, "rule", "Body")

        # Create an orphaned rule
        orphaned_file = continue_handler.rules_dir / "orphaned-rule.md"
        orphaned_file.write_text("orphaned content")

        # Clean with only the deployed file in the set
        deployed = {f"{mock_rule.title}.md"}
        removed = continue_handler.clean_orphaned_files(deployed)

        assert removed == 1
        assert not orphaned_file.exists()

    def test_clean_preserves_deployed_files(
        self, continue_handler: ContinueToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test that deployed files are not removed during clean."""
        # Deploy a prompt
        continue_handler.deploy(mock_prompt, "prompt", "Body")
        deployed_file = continue_handler.prompts_dir / f"{mock_prompt.title}.md"

        # Clean with the deployed file in the set
        deployed = {f"{mock_prompt.title}.md"}
        removed = continue_handler.clean_orphaned_files(deployed)

        assert removed == 0
        assert deployed_file.exists()

    def test_clean_multiple_orphaned_files(self, continue_handler: ContinueToolHandler):
        """Test cleaning multiple orphaned files."""
        # Create multiple orphaned files
        orphaned_prompt1 = continue_handler.prompts_dir / "orphan1.md"
        orphaned_prompt2 = continue_handler.prompts_dir / "orphan2.md"
        orphaned_rule = continue_handler.rules_dir / "orphan-rule.md"

        orphaned_prompt1.write_text("content1")
        orphaned_prompt2.write_text("content2")
        orphaned_rule.write_text("rule content")

        # Clean with empty deployed set
        removed = continue_handler.clean_orphaned_files(set())

        assert removed == 3
        assert not orphaned_prompt1.exists()
        assert not orphaned_prompt2.exists()
        assert not orphaned_rule.exists()

    def test_clean_with_no_orphaned_files(
        self, continue_handler: ContinueToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test that clean returns 0 when no orphaned files exist."""
        # Deploy a prompt
        continue_handler.deploy(mock_prompt, "prompt", "Body")

        # Clean with the deployed file in the set
        deployed = {f"{mock_prompt.title}.md"}
        removed = continue_handler.clean_orphaned_files(deployed)

        assert removed == 0

    def test_clean_with_source_filename_preservation(
        self, continue_handler: ContinueToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test clean works with preserved source filenames."""
        # Deploy with custom source filename
        source_filename = "Custom Prompt Name.md"
        continue_handler.deploy(mock_prompt, "prompt", "Body", source_filename)

        # Create an orphaned file
        orphaned = continue_handler.prompts_dir / "orphaned.md"
        orphaned.write_text("orphaned")

        # Clean - should keep the custom-named file
        deployed = {source_filename}
        removed = continue_handler.clean_orphaned_files(deployed)

        assert removed == 1
        assert (continue_handler.prompts_dir / source_filename).exists()
        assert not orphaned.exists()

    def test_clean_removes_backup_files(
        self, continue_handler: ContinueToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test that clean removes .bak backup files."""
        # Deploy a prompt
        continue_handler.deploy(mock_prompt, "prompt", "Body")

        # Create backup files manually
        backup_prompt = continue_handler.prompts_dir / "old-backup.md.bak"
        backup_rule = continue_handler.rules_dir / "rule-backup.md.bak"
        backup_prompt.write_text("old backup content")
        backup_rule.write_text("old rule backup")

        # Clean with the deployed file
        deployed = {f"{mock_prompt.title}.md"}
        removed = continue_handler.clean_orphaned_files(deployed)

        # Should remove both .bak files
        assert removed == 2
        assert not backup_prompt.exists()
        assert not backup_rule.exists()
        # Deployed file should still exist
        assert (continue_handler.prompts_dir / f"{mock_prompt.title}.md").exists()

    def test_clean_removes_backup_files_recursively_but_preserves_md_in_subdirectories(
        self, continue_handler: ContinueToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test that clean recursively removes .bak files but preserves .md in subdirectories.

        This behavior preserves files from previous deployments with different tag filters.
        """
        # Deploy a prompt (in root directory)
        continue_handler.deploy(mock_prompt, "prompt", "Body")

        # Create subdirectories in prompts and rules dirs
        subdir_prompts = continue_handler.prompts_dir / "subdir"
        subdir_rules = continue_handler.rules_dir / "subdir"
        subdir_prompts.mkdir()
        subdir_rules.mkdir()

        # Create .md files in subdirectories (should be preserved)
        (subdir_prompts / "nested.md").write_text("nested content")
        (subdir_rules / "nested-rule.md").write_text("nested rule")

        # Create backup files in subdirectories (should be removed)
        (subdir_prompts / "backup.md.bak").write_text("backup")
        (subdir_rules / "backup-rule.md.bak").write_text("backup rule")

        # Create orphaned .md file in root (should be removed)
        (continue_handler.prompts_dir / "orphan.md").write_text("orphan")

        # Clean with the deployed file (only root level file)
        deployed = {f"{mock_prompt.title}.md"}
        removed = continue_handler.clean_orphaned_files(deployed)

        # Should remove: 2 .bak files in subdirs + 1 orphaned .md in root = 3 files
        assert removed == 3
        assert subdir_prompts.exists()  # Directory remains
        assert subdir_rules.exists()  # Directory remains
        # .md files in subdirectories are PRESERVED (for tag filter compatibility)
        assert (subdir_prompts / "nested.md").exists()
        assert (subdir_rules / "nested-rule.md").exists()
        # .bak files in subdirectories are REMOVED
        assert not (subdir_prompts / "backup.md.bak").exists()
        assert not (subdir_rules / "backup-rule.md.bak").exists()
        # Orphaned .md in root is REMOVED
        assert not (continue_handler.prompts_dir / "orphan.md").exists()

    def test_clean_ignores_non_md_and_non_bak_files(
        self, continue_handler: ContinueToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test that clean ignores files that are not .md or .bak."""
        # Deploy a prompt
        continue_handler.deploy(mock_prompt, "prompt", "Body")

        # Create various non-.md, non-.bak files
        (continue_handler.prompts_dir / "README.txt").write_text("readme")
        (continue_handler.prompts_dir / "config.json").write_text("{}")
        (continue_handler.rules_dir / "notes.txt").write_text("notes")

        # Clean with the deployed file
        deployed = {f"{mock_prompt.title}.md"}
        removed = continue_handler.clean_orphaned_files(deployed)

        # Non-.md and non-.bak files should be ignored
        assert removed == 0
        assert (continue_handler.prompts_dir / "README.txt").exists()
        assert (continue_handler.prompts_dir / "config.json").exists()
        assert (continue_handler.rules_dir / "notes.txt").exists()


class TestRuleContentProcessingEdgeCases:
    """Test rule content processing with various field combinations."""

    def test_process_rule_with_applies_to_globs(self, tmp_path: Path):
        """Test processing rule with applies_to globs."""
        from prompt_unifier.models.rule import RuleFrontmatter

        handler = ContinueToolHandler(base_path=tmp_path)

        # Create a rule with applies_to field
        rule_with_globs = RuleFrontmatter(
            title="glob-rule",
            description="A rule with globs",
            category="coding-standards",
            applies_to=["*.py", "*.js"],
        )

        body = "This is the rule body"
        processed = handler._process_rule_content(rule_with_globs, body)

        # Verify globs field is present
        assert "name: glob-rule" in processed
        assert "description: A rule with globs" in processed
        assert "globs:" in processed
        assert "*.py" in processed or "'*.py'" in processed
        assert "*.js" in processed or "'*.js'" in processed
        assert body in processed

    def test_process_rule_with_author_and_language(self, tmp_path: Path):
        """Test processing rule with author and language fields."""
        from prompt_unifier.models.rule import RuleFrontmatter

        handler = ContinueToolHandler(base_path=tmp_path)

        # Create a rule with author and language
        rule = RuleFrontmatter(
            title="authored-rule",
            description="A rule with author",
            category="coding-standards",
            author="Test Author",
            language="python",
        )

        body = "Rule content"
        processed = handler._process_rule_content(rule, body)

        # Verify author and language are included
        assert "author: Test Author" in processed
        assert "language: python" in processed
        assert "name: authored-rule" in processed


class TestDeploymentErrorHandling:
    """Test error handling in deployment."""

    def test_deploy_with_wrong_content_type_for_prompt(self, tmp_path: Path):
        """Test deploy raises error when prompt content doesn't match content_type."""
        from prompt_unifier.models.rule import RuleFrontmatter

        handler = ContinueToolHandler(base_path=tmp_path)

        # Try to deploy a rule as a prompt (wrong type)
        rule = RuleFrontmatter(
            title="test-rule",
            description="A test rule",
            category="coding-standards",
        )

        with pytest.raises(ValueError, match="Content must be a PromptFrontmatter instance"):
            handler.deploy(rule, "prompt", "Body content")

    def test_deploy_with_wrong_content_type_for_rule(self, tmp_path: Path):
        """Test deploy raises error when rule content doesn't match content_type."""
        from prompt_unifier.models.prompt import PromptFrontmatter

        handler = ContinueToolHandler(base_path=tmp_path)

        # Try to deploy a prompt as a rule (wrong type)
        prompt = PromptFrontmatter(
            title="test-prompt",
            description="A test prompt",
        )

        with pytest.raises(ValueError, match="Content must be a RuleFrontmatter instance"):
            handler.deploy(prompt, "rule", "Body content")

    def test_deploy_with_unsupported_content_type(self, tmp_path: Path):
        """Test deploy raises error for unsupported content type."""
        from prompt_unifier.models.prompt import PromptFrontmatter

        handler = ContinueToolHandler(base_path=tmp_path)

        prompt = PromptFrontmatter(
            title="test-prompt",
            description="A test prompt",
        )

        with pytest.raises(ValueError, match="Unsupported content type: unknown"):
            handler.deploy(prompt, "unknown", "Body content")
