"""Tests for ContinueToolHandler with relative path support (Task Group 2)."""

from pathlib import Path

import pytest

from prompt_manager.handlers.continue_handler import ContinueToolHandler
from prompt_manager.models.prompt import PromptFrontmatter
from prompt_manager.models.rule import RuleFrontmatter


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


class TestRelativePathSupport:
    """Tests for relative path support in ContinueToolHandler.deploy."""

    def test_deploy_prompt_with_relative_path_creates_subdirectory(
        self, handler: ContinueToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test that deploy creates subdirectories based on relative_path."""
        relative_path = Path("backend/api")
        source_filename = "api-prompt.md"

        handler.deploy(
            mock_prompt,
            "prompt",
            "Test content",
            source_filename=source_filename,
            relative_path=relative_path,
        )

        # File should be created in subdirectory under prompts/
        expected_file = handler.prompts_dir / relative_path / source_filename
        assert expected_file.exists()
        assert "Test content" in expected_file.read_text()

    def test_deploy_rule_with_relative_path_creates_subdirectory(
        self, handler: ContinueToolHandler, mock_rule: RuleFrontmatter
    ):
        """Test that deploy creates subdirectories for rules based on relative_path."""
        relative_path = Path("security/authentication")
        source_filename = "auth-rule.md"

        handler.deploy(
            mock_rule,
            "rule",
            "Rule content",
            source_filename=source_filename,
            relative_path=relative_path,
        )

        # File should be created in subdirectory under rules/
        expected_file = handler.rules_dir / relative_path / source_filename
        assert expected_file.exists()
        assert "Rule content" in expected_file.read_text()

    def test_deploy_with_nested_relative_path(
        self, handler: ContinueToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test deploy with deeply nested relative paths."""
        relative_path = Path("backend/api/v2/endpoints")
        source_filename = "endpoint-prompt.md"

        handler.deploy(
            mock_prompt,
            "prompt",
            "Nested content",
            source_filename=source_filename,
            relative_path=relative_path,
        )

        expected_file = handler.prompts_dir / relative_path / source_filename
        assert expected_file.exists()

        # Verify all intermediate directories were created
        assert (handler.prompts_dir / "backend").exists()
        assert (handler.prompts_dir / "backend" / "api").exists()
        assert (handler.prompts_dir / "backend" / "api" / "v2").exists()
        assert (handler.prompts_dir / "backend" / "api" / "v2" / "endpoints").exists()

    def test_deploy_without_relative_path_uses_root(
        self, handler: ContinueToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test that deploy without relative_path deploys to root directory."""
        source_filename = "root-prompt.md"

        handler.deploy(
            mock_prompt,
            "prompt",
            "Root content",
            source_filename=source_filename,
            relative_path=None,
        )

        # File should be at root of prompts directory
        expected_file = handler.prompts_dir / source_filename
        assert expected_file.exists()

        # Should not create any subdirectories
        subdirs = [d for d in handler.prompts_dir.iterdir() if d.is_dir()]
        assert len(subdirs) == 0

    def test_deploy_with_empty_relative_path_uses_root(
        self, handler: ContinueToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test that deploy with empty Path() deploys to root directory."""
        source_filename = "root-prompt.md"

        handler.deploy(
            mock_prompt,
            "prompt",
            "Root content",
            source_filename=source_filename,
            relative_path=Path(),
        )

        # File should be at root of prompts directory
        expected_file = handler.prompts_dir / source_filename
        assert expected_file.exists()

    def test_deploy_preserves_subdirectory_structure_for_multiple_files(
        self, handler: ContinueToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test that multiple files in different subdirectories maintain structure."""
        # Deploy to backend/
        handler.deploy(
            mock_prompt,
            "prompt",
            "Backend content",
            source_filename="backend-prompt.md",
            relative_path=Path("backend"),
        )

        # Deploy to frontend/
        handler.deploy(
            mock_prompt,
            "prompt",
            "Frontend content",
            source_filename="frontend-prompt.md",
            relative_path=Path("frontend"),
        )

        # Deploy to root
        handler.deploy(
            mock_prompt,
            "prompt",
            "Root content",
            source_filename="root-prompt.md",
            relative_path=None,
        )

        # Verify all files exist in their respective locations
        assert (handler.prompts_dir / "backend" / "backend-prompt.md").exists()
        assert (handler.prompts_dir / "frontend" / "frontend-prompt.md").exists()
        assert (handler.prompts_dir / "root-prompt.md").exists()

    def test_deploy_with_relative_path_and_backup(
        self, handler: ContinueToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test that backup works correctly with relative paths."""
        relative_path = Path("backend")
        source_filename = "existing-prompt.md"

        # First deployment
        handler.deploy(
            mock_prompt,
            "prompt",
            "Original content",
            source_filename=source_filename,
            relative_path=relative_path,
        )

        # Second deployment (should create backup)
        handler.deploy(
            mock_prompt,
            "prompt",
            "Updated content",
            source_filename=source_filename,
            relative_path=relative_path,
        )

        target_file = handler.prompts_dir / relative_path / source_filename
        backup_file = target_file.with_suffix(".md.bak")

        assert target_file.exists()
        assert backup_file.exists()
        assert "Updated content" in target_file.read_text()
        assert "Original content" in backup_file.read_text()
