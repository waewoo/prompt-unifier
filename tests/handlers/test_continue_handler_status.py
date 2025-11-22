"""Tests for ContinueToolHandler status logic."""

from pathlib import Path

import pytest

from prompt_unifier.handlers.continue_handler import ContinueToolHandler
from prompt_unifier.models.prompt import PromptFrontmatter


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


class TestContinueToolHandlerStatus:
    """Tests for ContinueToolHandler.get_deployment_status."""

    def test_get_deployment_status_synced(
        self, continue_handler: ContinueToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test status is 'synced' when content matches."""
        content_body = "This is the content body."

        # Deploy the prompt first
        continue_handler.deploy(mock_prompt, "prompt", content_body)

        # Get the processed content that would be generated
        processed_content = continue_handler._process_prompt_content(mock_prompt, content_body)

        # Check status
        status = continue_handler.get_deployment_status(
            mock_prompt.title, "prompt", processed_content
        )
        assert status == "synced"

    def test_get_deployment_status_outdated(
        self, continue_handler: ContinueToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test status is 'outdated' when content differs."""
        content_body = "This is the content body."

        # Deploy the prompt
        continue_handler.deploy(mock_prompt, "prompt", content_body)

        # Modify the deployed file manually
        target_file = continue_handler.prompts_dir / f"{mock_prompt.title}.md"
        target_file.write_text("Modified content")

        # Get the processed content that SHOULD be there
        processed_content = continue_handler._process_prompt_content(mock_prompt, content_body)

        # Check status
        status = continue_handler.get_deployment_status(
            mock_prompt.title, "prompt", processed_content
        )
        assert status == "outdated"

    def test_get_deployment_status_missing(
        self, continue_handler: ContinueToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test status is 'missing' when file does not exist."""
        content_body = "This is the content body."

        # Do NOT deploy

        # Get the processed content
        processed_content = continue_handler._process_prompt_content(mock_prompt, content_body)

        # Check status
        status = continue_handler.get_deployment_status(
            mock_prompt.title, "prompt", processed_content
        )
        assert status == "missing"

    def test_get_deployment_status_with_source_filename(
        self, continue_handler: ContinueToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test status check works with custom source filename."""
        content_body = "Body content"
        source_filename = "custom-name.md"

        # Deploy with custom filename
        continue_handler.deploy(
            mock_prompt, "prompt", content_body, source_filename=source_filename
        )

        processed_content = continue_handler._process_prompt_content(mock_prompt, content_body)

        # Check status using the source_filename
        status = continue_handler.get_deployment_status(
            mock_prompt.title, "prompt", processed_content, source_filename=source_filename
        )
        assert status == "synced"

    def test_get_deployment_status_whitespace_handling(
        self, continue_handler: ContinueToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test status check handles minor whitespace differences (optional, but good practice)."""
        # For now, we expect exact match or hash match, so whitespace changes = outdated
        # If we implement normalization later, this test would change.

        content_body = "Body content"
        continue_handler.deploy(mock_prompt, "prompt", content_body)

        target_file = continue_handler.prompts_dir / f"{mock_prompt.title}.md"
        original_text = target_file.read_text()
        target_file.write_text(original_text + "\n")  # Add newline

        processed_content = continue_handler._process_prompt_content(mock_prompt, content_body)

        status = continue_handler.get_deployment_status(
            mock_prompt.title, "prompt", processed_content
        )
        # Currently strict equality/hashing
        assert status == "outdated"
