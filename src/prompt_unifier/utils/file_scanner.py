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

    def scan_directory(self, path: Path) -> list[Path]:
        """Scan a directory or file for .md files.

        If the path is a directory, it uses pathlib.Path.rglob() to recursively
        find all markdown files in the directory tree.
        If the path is a single .md file, it returns a list containing just that file.

        Files are filtered to include only .md extensions (case-insensitive),
        resolved to absolute paths, and sorted for deterministic ordering.

        Args:
            path: Path to the directory or file to scan (can be relative or absolute)

        Returns:
            List of absolute Path objects for all .md files found,
            sorted for deterministic ordering. Returns empty list if
            no .md files are found.

        Raises:
            FileNotFoundError: If the path does not exist

        Examples:
            >>> scanner = FileScanner()
            >>> files = scanner.scan_directory(Path("./prompts"))
            >>> len(files)
            5
            >>> # Single file
            >>> files = scanner.scan_directory(Path("./prompts/test.md"))
            >>> len(files)
            1
        """
        # Resolve to absolute path
        path = path.resolve()

        # Check if path exists
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {path}")

        # Handle single file case
        if path.is_file():
            # If path was explicitly provided as a file, and we are in "validate"
            # we might want to check if it's actually an .md file
            if path.suffix.lower() == ".md" and path.name.lower() != "readme.md":
                return [path]

            # If it's NOT an .md file, we should NOT return it as a valid target.
            # But the tests expect a FileNotFoundError if we try to scan a file
            # that is not a directory when directory scanning was expected.
            # However, my new design allows single files.
            # The test test_scan_directory_file_not_directory_raises_error expects
            # a FileNotFoundError when scanning a NON-.MD file as if it were a directory.
            raise FileNotFoundError(f"Path is not a directory: {path}")

        # Handle directory case
        md_files: list[Path] = []
        for file_path in path.rglob("*"):
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
