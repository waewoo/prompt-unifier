"""Tests for FileScanner class for discovering markdown files."""

from pathlib import Path

import pytest

from prompt_manager.utils.file_scanner import FileScanner


class TestFileScanner:
    """Test suite for FileScanner class."""

    def test_scan_directory_finds_multiple_md_files(self, tmp_path: Path) -> None:
        """Test that scanner finds all .md files in a directory."""
        scanner = FileScanner()

        # Create multiple .md files
        (tmp_path / "file1.md").write_text("content1")
        (tmp_path / "file2.md").write_text("content2")
        (tmp_path / "file3.md").write_text("content3")

        results = scanner.scan_directory(tmp_path)

        assert len(results) == 3
        assert all(p.suffix == ".md" for p in results)
        # Check that results are sorted for deterministic ordering
        assert results == sorted(results)

    def test_scan_directory_recursive_subdirectories(self, tmp_path: Path) -> None:
        """Test that scanner recursively scans subdirectories."""
        scanner = FileScanner()

        # Create nested structure
        (tmp_path / "root.md").write_text("root content")
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "nested.md").write_text("nested content")
        subsubdir = subdir / "subsubdir"
        subsubdir.mkdir()
        (subsubdir / "deep.md").write_text("deep content")

        results = scanner.scan_directory(tmp_path)

        assert len(results) == 3
        assert tmp_path / "root.md" in results
        assert subdir / "nested.md" in results
        assert subsubdir / "deep.md" in results

    def test_scan_directory_ignores_non_md_files(self, tmp_path: Path) -> None:
        """Test that scanner ignores non-.md files."""
        scanner = FileScanner()

        # Create various file types
        (tmp_path / "valid.md").write_text("valid content")
        (tmp_path / "readme.txt").write_text("text file")
        (tmp_path / "config.yaml").write_text("yaml file")
        (tmp_path / "script.py").write_text("python file")
        # Should be included (case-insensitive)
        (tmp_path / "document.MD").write_text("uppercase MD")

        results = scanner.scan_directory(tmp_path)

        # Should find both .md and .MD (case-insensitive)
        assert len(results) == 2
        assert all(p.suffix.lower() == ".md" for p in results)

    def test_scan_directory_ignores_readme_files(self, tmp_path: Path) -> None:
        """Test that scanner ignores README.md files."""
        scanner = FileScanner()

        # Create various file types
        (tmp_path / "valid.md").write_text("valid content")
        (tmp_path / "README.md").write_text("readme content")
        (tmp_path / "readme.md").write_text("readme content lowercase")

        results = scanner.scan_directory(tmp_path)

        assert len(results) == 1
        assert "valid.md" in str(results[0])
        assert "README.md" not in str(results)
        assert "readme.md" not in str(results)

    def test_scan_directory_not_found_raises_error(self) -> None:
        """Test that scanning non-existent directory raises FileNotFoundError."""
        scanner = FileScanner()
        non_existent = Path("/path/that/does/not/exist")

        with pytest.raises(FileNotFoundError, match="Directory not found"):
            scanner.scan_directory(non_existent)

    def test_scan_directory_file_not_directory_raises_error(self, tmp_path: Path) -> None:
        """Test that scanning a file path (not directory) raises FileNotFoundError."""
        scanner = FileScanner()

        # Create a file instead of a directory
        file_path = tmp_path / "not_a_directory.txt"
        file_path.write_text("I am a file, not a directory")

        with pytest.raises(FileNotFoundError, match="Path is not a directory"):
            scanner.scan_directory(file_path)

    def test_scan_directory_empty_returns_empty_list(self, tmp_path: Path) -> None:
        """Test that empty directory returns empty list."""
        scanner = FileScanner()

        results = scanner.scan_directory(tmp_path)

        assert results == []

    def test_scan_directory_resolves_relative_to_absolute(self, tmp_path: Path) -> None:
        """Test that relative paths are resolved to absolute paths."""
        scanner = FileScanner()

        # Create a file
        (tmp_path / "test.md").write_text("content")

        # Get relative path
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path.parent)
            relative_path = Path(tmp_path.name)

            results = scanner.scan_directory(relative_path)

            assert len(results) == 1
            # Result should be absolute
            assert results[0].is_absolute()
            assert results[0] == tmp_path / "test.md"
        finally:
            os.chdir(original_cwd)
