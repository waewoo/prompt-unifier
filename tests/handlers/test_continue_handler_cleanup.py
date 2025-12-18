"""Tests for ContinueToolHandler cleanup functionality."""

from pathlib import Path

import pytest

from prompt_unifier.handlers.continue_handler import ContinueToolHandler


@pytest.fixture
def handler(tmp_path: Path) -> ContinueToolHandler:
    """Create a ContinueToolHandler instance for testing."""
    return ContinueToolHandler(base_path=tmp_path)


class TestCleanup:
    """Tests for clean_orphaned_files in ContinueToolHandler."""

    def test_clean_orphaned_files_in_subdirectory(self, handler: ContinueToolHandler):
        """Test that orphaned files in subdirectories are removed."""
        # Setup: Create an orphaned file in a subdirectory
        subdir = handler.prompts_dir / "terraform"
        subdir.mkdir(parents=True)
        orphaned_file = subdir / "orphaned.md"
        orphaned_file.write_text("content")

        # Execute: Clean orphaned files (none deployed)
        results = handler.clean_orphaned_files(set())

        # Verify: File should be removed
        assert not orphaned_file.exists()

        # Verify: Result should be reported
        assert len(results) == 1
        assert results[0].file_name == "orphaned"
        assert results[0].status == "passed"

    def test_clean_orphaned_files_preserves_deployed_files_in_subdirectory(
        self, handler: ContinueToolHandler
    ):
        """Test that deployed files in subdirectories are NOT removed."""
        # Setup: Create a file that is "deployed"
        subdir = handler.prompts_dir / "terraform"
        subdir.mkdir(parents=True)
        deployed_file = subdir / "deployed.md"
        deployed_file.write_text("content")

        # Execute: Clean orphaned files (with this file in deployed list)
        # Note: deployed_filenames expects relative paths as strings
        deployed_filenames = {"terraform/deployed.md"}
        results = handler.clean_orphaned_files(deployed_filenames)

        # Verify: File should still exist
        assert deployed_file.exists()
        assert len(results) == 0

    def test_clean_orphaned_files_removes_empty_subdirectories(self, handler: ContinueToolHandler):
        """Test that empty subdirectories are removed after cleanup."""
        # Setup: Create an orphaned file in a subdirectory
        subdir = handler.prompts_dir / "terraform"
        subdir.mkdir(parents=True)
        orphaned_file = subdir / "orphaned.md"
        orphaned_file.write_text("content")

        # Execute: Clean orphaned files
        handler.clean_orphaned_files(set())

        # Verify: Directory should be removed
        assert not subdir.exists()
