"""Tests for ContinueToolHandler."""

import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from prompt_manager.handlers.continue_handler import ContinueToolHandler
from prompt_manager.models.prompt import PromptFrontmatter
from prompt_manager.models.rule import RuleFrontmatter


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

    def test_verify_deployment_invalid_content_type(self):
        """Test verify_deployment with invalid content type."""
        handler = ContinueToolHandler()
        result = handler.verify_deployment("test", "invalid_type")
        assert result is False

    def test_verify_deployment_rule_missing_file(self):
        """Test verify_deployment for a rule that doesn't exist."""
        handler = ContinueToolHandler()
        result = handler.verify_deployment("non_existent_rule", "rule")
        assert result is False

    def test_verify_deployment_rule_invalid_format(self):
        """Test verify_deployment for a rule with invalid format."""
        handler = ContinueToolHandler()

        # Create a rule file without valid YAML format
        rule_file = handler.rules_dir / "test_rule.md"
        rule_file.write_text("Invalid content without frontmatter")

        result = handler.verify_deployment("test_rule", "rule")
        assert result is True  # Rules don't have strict validation like prompts

    def test_verify_deployment_prompt_invalid_yaml(self):
        """Test verify_deployment for a prompt with invalid YAML."""
        handler = ContinueToolHandler()

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

    def test_verify_deployment_prompt_no_invokable_field(self):
        """Test verify_deployment for a prompt without invokable field."""
        handler = ContinueToolHandler()

        # Create a prompt file without invokable field
        prompt_file = handler.prompts_dir / "test_prompt.md"
        prompt_file.write_text("""---
name: test_prompt
description: A test prompt
---
content""")

        result = handler.verify_deployment("test_prompt", "prompt")
        assert result is False  # Missing invokable field

    def test_verify_deployment_prompt_invokable_false(self):
        """Test verify_deployment for a prompt with invokable: false."""
        handler = ContinueToolHandler()

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

    def test_rollback_multiple_files(self):
        """Test rollback with multiple backup files."""
        handler = ContinueToolHandler()

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

    def test_rollback_no_backups(self):
        """Test rollback when there are no backups."""
        handler = ContinueToolHandler()

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

    def test_rollback_mixed_backups(self):
        """Test rollback with mixed backups (some exist, some don't)."""
        handler = ContinueToolHandler()

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

    def test_process_prompt_content_with_all_fields(self):
        """Test _process_prompt_content with all optional fields."""
        handler = ContinueToolHandler()

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

    def test_process_rule_content_with_all_fields(self):
        """Test _process_rule_content with all optional fields."""
        handler = ContinueToolHandler()

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

    def test_deploy_prompt_with_complex_content(self):
        """Test deploy with a prompt having complex content."""
        handler = ContinueToolHandler()

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

    def test_deploy_rule_with_complex_content(self):
        """Test deploy with a rule having complex content."""
        handler = ContinueToolHandler()

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

    def test_backup_file_with_special_characters(self):
        """Test _backup_file with special file names."""
        handler = ContinueToolHandler()

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

    def test_get_status_with_missing_directories(self):
        """Test get_status when directories are missing."""
        handler = ContinueToolHandler()

        # Remove directories
        if handler.prompts_dir.exists():
            shutil.rmtree(handler.prompts_dir)
        if handler.rules_dir.exists():
            shutil.rmtree(handler.rules_dir)

        status = handler.get_status()
        assert status == "inactive"

    def test_init_with_custom_base_path(self):
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

    def test_deploy_with_empty_content(self):
        """Test deploy with empty content."""
        handler = ContinueToolHandler()

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

    def test_deploy_with_unicode_content(self):
        """Test deploy with unicode content."""
        handler = ContinueToolHandler()

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

    def test_process_prompt_content_yaml_order(self):
        """Test that YAML field order is respected."""
        handler = ContinueToolHandler()

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

    def test_process_rule_content_yaml_order(self):
        """Test that YAML field order is respected for rules."""
        handler = ContinueToolHandler()

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
