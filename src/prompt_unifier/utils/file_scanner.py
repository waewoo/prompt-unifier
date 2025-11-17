"""File discovery utilities for scanning directories for markdown files.

This module provides the FileScanner class for recursively discovering
.md files in a directory structure.
"""

from pathlib import Path


class FileScanner:
    """Scans directories for markdown prompt files.

    The FileScanner discovers all .md files in a directory tree,
    performing recursive scanning and filtering by file extension.

    Examples:
        >>> scanner = FileScanner()
        >>> files = scanner.scan_directory(Path("./prompts"))
        >>> len(files)
        5
    """

    def scan_directory(self, directory: Path) -> list[Path]:
        """Scan a directory recursively for .md files.

        This method uses pathlib.Path.rglob() to recursively find all
        markdown files in the directory tree. Files are filtered to
        include only .md extensions (case-insensitive), resolved to
        absolute paths, and sorted for deterministic ordering.

        Args:
            directory: Path to the directory to scan (can be relative or absolute)

        Returns:
            List of absolute Path objects for all .md files found,
            sorted for deterministic ordering. Returns empty list if
            no .md files are found.

        Raises:
            FileNotFoundError: If the directory does not exist

        Examples:
            >>> scanner = FileScanner()
            >>> files = scanner.scan_directory(Path("./prompts"))
            >>> for file in files:
            ...     print(file.name)
            python-expert.md
            code-reviewer.md
        """
        # Resolve to absolute path
        directory = directory.resolve()

        # Check if directory exists
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        if not directory.is_dir():
            raise FileNotFoundError(f"Path is not a directory: {directory}")

        # Use rglob to recursively find all .md files (case-insensitive)
        md_files: list[Path] = []
        for file_path in directory.rglob("*"):
            # Check if it's a file (not directory) and has .md extension (case-insensitive)
            if (
                file_path.is_file()
                and file_path.suffix.lower() == ".md"
                and file_path.name.lower() != "readme.md"
            ):
                md_files.append(file_path.resolve())

        # Sort for deterministic ordering
        md_files.sort()

        return md_files
