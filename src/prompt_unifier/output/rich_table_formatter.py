"""Rich table formatter for list and status commands."""

from typing import Any

from rich.syntax import Syntax
from rich.table import Table


class RichTableFormatter:
    """Formatter for generating Rich tables for list and status commands."""

    def format_list_table(self, items: list[tuple[Any, str, str]]) -> Table:
        """
        Format a list of items into a Rich table.

        Args:
            items: List of tuples (parsed_content, content_type, file_path).

        Returns:
            A Rich Table object.
        """
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="blue")
        table.add_column("Tags")
        table.add_column("Tools")
        table.add_column("Version", style="dim")

        for content, content_type, _ in items:
            name = content.title

            tags = ""
            if hasattr(content, "tags") and content.tags:
                tags = ", ".join(content.tags)

            tools = "All"  # Default if not specified, or logic to determine tools
            # In future, we might check handlers registry or content metadata if it restricts tools

            version = getattr(content, "version", "N/A")

            table.add_row(
                name,
                content_type,
                tags,
                tools,
                version,
            )

        return table

    def format_status_table(self, items: list[dict[str, Any]]) -> Table:
        """
        Format status results into a Rich table.

        Args:
            items: List of dicts with keys: name, type, handler, status, details.

        Returns:
            A Rich Table object.
        """
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="blue")
        table.add_column("Handler")
        table.add_column("Status")
        table.add_column("Details", style="dim")

        for item in items:
            status = item["status"]
            status_style = "green"
            if status == "outdated":
                status_style = "yellow"
            elif status == "missing":
                status_style = "red"
            elif status == "failed":
                status_style = "bold red"

            table.add_row(
                item["name"],
                item["type"],
                item["handler"],
                f"[{status_style}]{status.upper()}[/{status_style}]",
                item.get("details", ""),
            )

        return table

    def format_content_preview(self, content: str, language: str = "markdown") -> Syntax:
        """
        Format content as a syntax highlighted block.

        Args:
            content: The content to format.
            language: The language for syntax highlighting.

        Returns:
            A Rich Syntax object.
        """
        return Syntax(content, language, theme="monokai", line_numbers=True)
