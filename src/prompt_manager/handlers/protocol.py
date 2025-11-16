from pathlib import Path
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ToolHandler(Protocol):
    """
    Protocol for defining a ToolHandler.

    Any class implementing this protocol must provide the specified methods.
    """

    def deploy(
        self,
        content: Any,
        content_type: str,
        body: str = "",
        source_filename: str | None = None,
        relative_path: Path | None = None,
    ) -> None:
        """
        Deploys a given content (prompt or rule) to the specific AI tool.

        Args:
            content: The content object (PromptFrontmatter or RuleFrontmatter) to deploy.
            content_type: The type of content ("prompt" or "rule").
            body: The body content as a string.
            source_filename: Original filename (without path) to preserve in destination.
                           If None, uses content.title as filename.
            relative_path: Relative path from prompts/ or rules/ directory to preserve
                          subdirectory structure in deployment. If None, deploys to root.
        """
        ...

    def get_status(self) -> str:
        """
        Returns the current status of the tool handler.

        Returns:
            A string representing the status (e.g., "active", "inactive", "error").
        """
        ...

    def get_name(self) -> str:
        """
        Returns the unique name of the tool handler.

        Returns:
            A string representing the name (e.g., "continue", "cursor").
        """
        ...

    def rollback(self) -> None:
        """
        Rolls back the deployment in case of failure.
        """
        ...

    def clean_orphaned_files(self, deployed_filenames: set[str]) -> int:
        """
        Remove files in handler directories that are not in the deployed set.

        Args:
            deployed_filenames: Set of filenames (including extension) that were deployed.

        Returns:
            Number of files removed.
        """
        ...
