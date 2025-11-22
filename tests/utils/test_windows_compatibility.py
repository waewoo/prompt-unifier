"""Tests for Windows compatibility utilities.

This module tests cross-platform path normalization, UTF-8 encoding,
symlink handling, and file locking behavior to ensure tests pass
on both Windows and Linux platforms.
"""

import os
import platform
import sys
from pathlib import Path, PureWindowsPath

import pytest


class TestPathNormalization:
    """Tests for path normalization utilities."""

    def test_normalize_path_converts_windows_separators(self) -> None:
        """Test that Windows-style paths are normalized to POSIX format."""
        from prompt_unifier.utils.path_helpers import normalize_path_for_comparison

        # Use PureWindowsPath to simulate a Windows path regardless of OS
        windows_path = PureWindowsPath("prompts\\example\\test.md")
        result = normalize_path_for_comparison(windows_path)

        assert "\\" not in result
        assert result == "prompts/example/test.md"

    def test_normalize_path_preserves_forward_slashes(self) -> None:
        """Test that POSIX-style paths remain unchanged."""
        from prompt_unifier.utils.path_helpers import normalize_path_for_comparison

        posix_path = Path("prompts/example/test.md")
        result = normalize_path_for_comparison(posix_path)

        assert result == "prompts/example/test.md"

    def test_normalize_path_handles_string_input(self) -> None:
        """Test that string paths are correctly normalized."""
        from prompt_unifier.utils.path_helpers import normalize_path_for_comparison

        path_str = "prompts/rules/test.md"
        result = normalize_path_for_comparison(path_str)

        assert result == "prompts/rules/test.md"

    def test_normalize_path_handles_absolute_paths(self, tmp_path: Path) -> None:
        """Test that absolute paths are correctly normalized."""
        from prompt_unifier.utils.path_helpers import normalize_path_for_comparison

        abs_path = tmp_path / "prompts" / "test.md"
        result = normalize_path_for_comparison(abs_path)

        assert "\\" not in result
        assert "prompts/test.md" in result

    def test_normalize_path_handles_relative_paths(self) -> None:
        """Test that relative paths with parent references are normalized."""
        from prompt_unifier.utils.path_helpers import normalize_path_for_comparison

        rel_path = Path("../prompts/test.md")
        result = normalize_path_for_comparison(rel_path)

        assert "\\" not in result
        # The path should contain forward slashes
        assert "/" in result or result == "test.md"

    def test_normalize_path_handles_empty_path(self) -> None:
        """Test that empty path is handled gracefully."""
        from prompt_unifier.utils.path_helpers import normalize_path_for_comparison

        result = normalize_path_for_comparison("")
        assert result == "."


class TestUTF8Encoding:
    """Tests for UTF-8 encoding utilities."""

    def test_file_write_with_utf8_encoding(self, tmp_path: Path) -> None:
        """Test that files with UTF-8 content are written correctly."""
        test_file = tmp_path / "test_utf8.md"
        content = "Test content with emojis: 🎉🚀 and accents: eaeceu"

        test_file.write_text(content, encoding="utf-8")

        assert test_file.exists()
        read_content = test_file.read_text(encoding="utf-8")
        assert read_content == content

    def test_file_read_with_utf8_encoding(self, tmp_path: Path) -> None:
        """Test that files are read with explicit UTF-8 encoding."""
        test_file = tmp_path / "test_read.md"
        content = "Content with special chars: cafe, naive, resume"

        test_file.write_text(content, encoding="utf-8")

        with open(test_file, encoding="utf-8") as f:
            read_content = f.read()

        assert read_content == content

    def test_open_with_explicit_encoding(self, tmp_path: Path) -> None:
        """Test that open() with explicit encoding works correctly."""
        test_file = tmp_path / "test_open.md"
        content = "Special characters: x^2, y^2"

        with open(test_file, "w", encoding="utf-8") as f:
            f.write(content)

        with open(test_file, encoding="utf-8") as f:
            read_content = f.read()

        assert read_content == content

    def test_non_ascii_filename_handling(self, tmp_path: Path) -> None:
        """Test handling of files with non-ASCII characters."""
        test_file = tmp_path / "test_file.md"
        content = "Chinese: zhongwen, Japanese: nihongo"

        test_file.write_text(content, encoding="utf-8")
        read_content = test_file.read_text(encoding="utf-8")

        assert read_content == content


class TestSymlinkHandling:
    """Tests for symlink handling and skip markers."""

    def test_skipif_marker_skips_on_windows(self) -> None:
        """Test that skipif marker correctly detects Windows platform."""
        is_windows = platform.system() == "Windows"

        if is_windows:
            pytest.skip("This test is skipped on Windows")

        # On Linux, this test should run
        assert platform.system() != "Windows"

    def test_platform_detection(self) -> None:
        """Test platform detection for conditional test skipping."""
        current_platform = platform.system()

        assert current_platform in ["Windows", "Linux", "Darwin"]

    @pytest.mark.skipif(
        platform.system() == "Windows", reason="Symlinks require elevated privileges on Windows"
    )
    def test_symlink_creation(self, tmp_path: Path) -> None:
        """Test that symlink creation works on non-Windows platforms."""
        target = tmp_path / "target.txt"
        target.write_text("Target content", encoding="utf-8")

        symlink = tmp_path / "symlink.txt"
        symlink.symlink_to(target)

        assert symlink.is_symlink()
        assert symlink.read_text(encoding="utf-8") == "Target content"

    @pytest.mark.skipif(
        platform.system() == "Windows", reason="Symlinks require elevated privileges on Windows"
    )
    def test_symlink_resolution(self, tmp_path: Path) -> None:
        """Test that symlink resolution works correctly."""
        target = tmp_path / "target.md"
        target.write_text("Resolved content", encoding="utf-8")

        symlink = tmp_path / "link.md"
        symlink.symlink_to(target)

        resolved = symlink.resolve()
        assert resolved == target.resolve()


class TestFileLocking:
    """Tests for file locking and context manager behavior."""

    def test_context_manager_closes_file_handle(self, tmp_path: Path) -> None:
        """Test that context manager properly closes file handles."""
        test_file = tmp_path / "test_lock.txt"

        with open(test_file, "w", encoding="utf-8") as f:
            f.write("Test content")

        # File should be accessible after context manager exits
        assert test_file.read_text(encoding="utf-8") == "Test content"

    def test_file_can_be_deleted_after_context_manager(self, tmp_path: Path) -> None:
        """Test that files can be deleted after context manager closes."""
        test_file = tmp_path / "deletable.txt"

        with open(test_file, "w", encoding="utf-8") as f:
            f.write("Content to delete")

        # Should be able to delete without file locking errors
        test_file.unlink()
        assert not test_file.exists()

    def test_file_can_be_renamed_after_context_manager(self, tmp_path: Path) -> None:
        """Test that files can be renamed after context manager closes."""
        original = tmp_path / "original.txt"
        renamed = tmp_path / "renamed.txt"

        with open(original, "w", encoding="utf-8") as f:
            f.write("Content to rename")

        # Should be able to rename without file locking errors
        original.rename(renamed)
        assert renamed.exists()
        assert not original.exists()

    def test_path_write_text_allows_subsequent_operations(self, tmp_path: Path) -> None:
        """Test that Path.write_text allows subsequent file operations."""
        test_file = tmp_path / "write_text.txt"

        test_file.write_text("Initial content", encoding="utf-8")

        # Should be able to read and overwrite
        content = test_file.read_text(encoding="utf-8")
        test_file.write_text(content + " modified", encoding="utf-8")

        assert "modified" in test_file.read_text(encoding="utf-8")

    def test_backup_restore_scenario(self, tmp_path: Path) -> None:
        """Test backup and restore scenario without file locking issues."""
        original = tmp_path / "config.yaml"
        backup = tmp_path / "config.yaml.bak"

        # Create original file
        original.write_text("original: true", encoding="utf-8")

        # Create backup
        backup.write_text(original.read_text(encoding="utf-8"), encoding="utf-8")

        # Modify original
        original.write_text("modified: true", encoding="utf-8")

        # Restore from backup
        original.write_text(backup.read_text(encoding="utf-8"), encoding="utf-8")

        assert original.read_text(encoding="utf-8") == "original: true"


class TestPlatformSpecificBehavior:
    """Tests for platform-specific behavior patterns."""

    def test_os_name_detection(self) -> None:
        """Test that os.name correctly identifies the platform."""
        if sys.platform.startswith("win"):
            assert os.name == "nt"
        else:
            assert os.name == "posix"

    def test_path_separator(self) -> None:
        """Test path separator detection."""
        if platform.system() == "Windows":
            assert os.sep == "\\"
        else:
            assert os.sep == "/"

    def test_pathlib_handles_separators(self, tmp_path: Path) -> None:
        """Test that pathlib correctly handles path separators."""
        nested = tmp_path / "dir1" / "dir2" / "file.txt"
        nested.parent.mkdir(parents=True, exist_ok=True)
        nested.write_text("content", encoding="utf-8")

        # Path should be valid regardless of platform
        assert nested.exists()
        assert nested.is_file()
