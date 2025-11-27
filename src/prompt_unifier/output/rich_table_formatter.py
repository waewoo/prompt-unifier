"""Rich table formatter for list and status commands."""

from typing import Any

from rich.syntax import Syntax
from rich.table import Table

from prompt_unifier.models.validation import ValidationSummary

HEADER_STYLE = "bold magenta"


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
        table = Table(show_header=True, header_style=HEADER_STYLE)
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
        table = Table(show_header=True, header_style=HEADER_STYLE)
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="blue")
        table.add_column("Handler")
        table.add_column("Status")
        table.add_column(
            "File Path", style="dim", min_width=40, overflow="fold"
        )  # Adjusted column definition
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
                item.get("file_path", ""),
                item.get("details", ""),
            )

        return table

    def format_validation_table(
        self, summary: ValidationSummary, show_scaff: bool = False
    ) -> Table:
        """
        Format validation summary into a Rich table.

        Args:
            summary: ValidationSummary object.
            show_scaff: Whether to show SCAFF score columns.

        Returns:
            A Rich Table object.
        """
        table = Table(show_header=True, header_style=HEADER_STYLE)
        table.add_column("File", style="cyan")
        table.add_column("Status")

        if show_scaff:
            table.add_column("SCAFF", justify="right")
            # Add columns for each SCAFF component (abbreviated)
            table.add_column("Spec", justify="right", header_style="dim")
            table.add_column("Cont", justify="right", header_style="dim")
            table.add_column("Act", justify="right", header_style="dim")
            table.add_column("Fmt", justify="right", header_style="dim")
            table.add_column("Foc", justify="right", header_style="dim")

        table.add_column("Issues", style="dim")
        table.add_column("Path", style="dim", overflow="fold")

        for result in summary.results:
            # Status
            status_style = "green" if result.status == "passed" else "bold red"
            status_text = f"[{status_style}]{result.status.upper()}[/{status_style}]"

            row_items = [result.file.name, status_text]

            if show_scaff:
                row_items.extend(self._format_scaff_columns(result))

            # Issues
            issues_parts = []
            if result.errors:
                issues_parts.append(f"[bold red]{len(result.errors)} errors[/bold red]")
            if result.warnings:
                issues_parts.append(f"[yellow]{len(result.warnings)} warnings[/yellow]")

            issues_text = ", ".join(issues_parts) if issues_parts else "None"
            row_items.append(issues_text)

            # Path
            row_items.append(str(result.file))

            table.add_row(*row_items)

        return table

    def _format_scaff_columns(self, result: Any) -> list[str]:
        """Format SCAFF score columns for a result row."""
        scaff_text = "N/A"
        comp_scores = ["-"] * 5

        if result.scaff_score:
            # Total Score
            score = result.scaff_score.total_score
            score_style = "green"
            if score < 50:
                score_style = "red"
            elif score < 80:
                score_style = "yellow"
            scaff_text = f"[{score_style}]{score}[/{score_style}]"

            # Component Scores
            # Map component names to scores
            comp_map = {c.component_name.lower(): c.score for c in result.scaff_score.components}

            def _fmt_score(name: str, scores: dict[str, int] = comp_map) -> str:
                s = scores.get(name, 0)
                # Max score is 20 per component
                style = "green"
                if s < 10:
                    style = "red"
                elif s < 20:
                    style = "yellow"
                return f"[{style}]{s}[/{style}]"

            comp_scores = [
                _fmt_score("specific"),
                _fmt_score("contextual"),
                _fmt_score("actionable"),
                _fmt_score("formatted"),
                _fmt_score("focused"),
            ]

        return [scaff_text, *comp_scores]

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
