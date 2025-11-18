"""Path filtering utility for selective file syncing.

This module provides the PathFilter class for applying glob-style include/exclude
patterns to file paths during multi-repository sync operations.
"""

from pathlib import Path


class PathFilter:
    """Utility class for filtering file paths using glob patterns.

    This class provides static methods for applying include and exclude patterns
    to lists of file paths. Patterns are glob-style and use pathlib.Path.match().

    Examples:
        >>> files = ["prompts/python/example.md", "prompts/javascript/test.md"]
        >>> filtered = PathFilter.apply_filters(files, include_patterns=["**/python/**"])
        >>> "prompts/python/example.md" in filtered
        True
        >>> "prompts/javascript/test.md" in filtered
        False
    """

    @staticmethod
    def apply_filters(
        file_paths: list[str],
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
    ) -> list[str]:
        """Apply include and exclude glob patterns to filter file paths.

        Filtering logic:
        1. If include_patterns specified, only keep files matching at least one pattern
        2. Then apply exclude_patterns to remove files matching any exclude pattern

        Args:
            file_paths: List of file paths to filter
            include_patterns: Optional list of glob patterns - only include matching files
            exclude_patterns: Optional list of glob patterns - exclude matching files

        Returns:
            Filtered list of file paths

        Examples:
            >>> files = ["prompts/python/a.md", "prompts/js/b.md", "prompts/temp/c.md"]
            >>> # Include only python files
            >>> PathFilter.apply_filters(files, include_patterns=["**/python/**"])
            ['prompts/python/a.md']

            >>> # Exclude temp files
            >>> PathFilter.apply_filters(files, exclude_patterns=["**/temp/**"])
            ['prompts/python/a.md', 'prompts/js/b.md']

            >>> # Combine: include *.md, exclude temp
            >>> PathFilter.apply_filters(
            ...     files,
            ...     include_patterns=["**/*.md"],
            ...     exclude_patterns=["**/temp/**"]
            ... )
            ['prompts/python/a.md', 'prompts/js/b.md']
        """
        filtered_paths = file_paths.copy()

        # Step 1: Apply include patterns if specified
        if include_patterns:
            included = []
            for file_path in filtered_paths:
                path_obj = Path(file_path)
                # Check if file matches any include pattern
                if any(path_obj.match(pattern) for pattern in include_patterns):
                    included.append(file_path)
            filtered_paths = included

        # Step 2: Apply exclude patterns if specified
        if exclude_patterns:
            excluded = []
            for file_path in filtered_paths:
                path_obj = Path(file_path)
                # Exclude file if it matches any exclude pattern
                if not any(path_obj.match(pattern) for pattern in exclude_patterns):
                    excluded.append(file_path)
            filtered_paths = excluded

        return filtered_paths

    @staticmethod
    def matches_pattern(file_path: str, pattern: str) -> bool:
        """Check if a file path matches a glob pattern.

        Args:
            file_path: File path to check
            pattern: Glob pattern to match against

        Returns:
            True if file_path matches pattern, False otherwise

        Examples:
            >>> PathFilter.matches_pattern("prompts/python/example.md", "**/python/**")
            True
            >>> PathFilter.matches_pattern("prompts/javascript/test.md", "**/python/**")
            False
        """
        return Path(file_path).match(pattern)
