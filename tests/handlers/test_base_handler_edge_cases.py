"""Tests for BaseToolHandler exception handling and edge cases."""

from pathlib import Path
from unittest.mock import patch

import pytest

from prompt_unifier.handlers.base_handler import BaseToolHandler


class MockToolHandler(BaseToolHandler):
    """Mock implementation of BaseToolHandler for testing."""

    def __init__(self, base_path: Path):
        super().__init__()
        self.name = "mock"
        self.base_path = base_path
        self.tool_dir_constant = ".mock"
        self.prompts_dir = self.base_path / self.tool_dir_constant / "prompts"
        self.rules_dir = self.base_path / self.tool_dir_constant / "rules"

    def deploy(self, content, content_type, body="", source_filename=None, relative_path=None):
        pass

    def verify_deployment_with_details(self, content_name, content_type, file_name):
        pass


@pytest.fixture
def mock_handler(tmp_path: Path) -> MockToolHandler:
    """Create a MockToolHandler instance."""
    return MockToolHandler(tmp_path)


class TestBaseToolHandlerEdgeCases:
    """Tests for edge cases and exceptions in BaseToolHandler."""

    def test_determine_deployment_status_os_error(self, mock_handler: MockToolHandler):
        """Test _determine_deployment_status handles OSError (lines 111-113)."""
        target_file = mock_handler.prompts_dir / "test.md"
        mock_handler.prompts_dir.mkdir(parents=True, exist_ok=True)
        target_file.touch()

        # Simulate OSError when reading file
        with patch("pathlib.Path.read_text", side_effect=OSError("Read error")):
            status = mock_handler._determine_deployment_status(target_file, "content")
            assert status == "updated"

    def test_determine_deployment_status_unicode_error(self, mock_handler: MockToolHandler):
        """Test _determine_deployment_status handles UnicodeDecodeError (lines 111-113)."""
        target_file = mock_handler.prompts_dir / "test.md"
        mock_handler.prompts_dir.mkdir(parents=True, exist_ok=True)
        target_file.touch()

        # Simulate UnicodeDecodeError
        with patch(
            "pathlib.Path.read_text",
            side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "invalid"),
        ):
            status = mock_handler._determine_deployment_status(target_file, "content")
            assert status == "updated"

    def test_remove_empty_directories_os_error(self, mock_handler: MockToolHandler):
        """Test _remove_empty_directories handles OSError (line 140)."""
        mock_handler.prompts_dir.mkdir(parents=True, exist_ok=True)
        empty_dir = mock_handler.prompts_dir / "empty"
        empty_dir.mkdir()

        # Simulate OSError when removing directory
        with patch("pathlib.Path.rmdir", side_effect=OSError("Delete error")):
            mock_handler._remove_empty_directories(mock_handler.prompts_dir)
            # Should catch exception and continue
            assert empty_dir.exists()

    def test_rollback_warning(self, mock_handler: MockToolHandler):
        """Test rollback logs warning (line 284)."""
        with patch("prompt_unifier.handlers.base_handler.logger") as mock_logger:
            mock_handler.rollback()
            mock_logger.warning.assert_called_with(
                "Rollback called but backup functionality has been removed"
            )

    def test_extract_title_from_md_file_exceptions(self, mock_handler: MockToolHandler):
        """Test _extract_title_from_md_file handles read errors (lines 370->365)."""
        test_file = mock_handler.prompts_dir / "test.md"
        mock_handler.prompts_dir.mkdir(parents=True, exist_ok=True)
        test_file.touch()

        # OSError
        with patch("pathlib.Path.read_text", side_effect=OSError("Read error")):
            title = mock_handler._extract_title_from_md_file(test_file)
            assert title is None

        # UnicodeDecodeError
        with patch(
            "pathlib.Path.read_text",
            side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "invalid"),
        ):
            title = mock_handler._extract_title_from_md_file(test_file)
            assert title is None

    def test_compare_content_hashes_exceptions(self, mock_handler: MockToolHandler):
        """Test _compare_content_hashes handles exceptions (line 496)."""
        target_file = mock_handler.prompts_dir / "test.md"
        mock_handler.prompts_dir.mkdir(parents=True, exist_ok=True)
        target_file.touch()

        # OSError
        with patch("pathlib.Path.read_text", side_effect=OSError("Read error")):
            status = mock_handler._compare_content_hashes("content", target_file)
            assert status == "error"

        # UnicodeDecodeError
        with patch(
            "pathlib.Path.read_text",
            side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "invalid"),
        ):
            status = mock_handler._compare_content_hashes("content", target_file)
            assert status == "error"
