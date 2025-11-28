"""Base handler class with shared functionality for tool handlers."""

import logging
from abc import ABC
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from rich.console import Console
from rich.table import Table

from prompt_unifier.constants import BAK_GLOB_PATTERN
from prompt_unifier.handlers.handler_utils import console
from prompt_unifier.handlers.protocol import ToolHandler

logger = logging.getLogger(__name__)

# Color constants for verification reports
ERROR_COLOR = "red"
WARNING_COLOR = "yellow"
SUCCESS_COLOR = "green"


@dataclass
class VerificationResult:
    """Data class for storing verification result details."""

    file_name: str
    content_type: str
    status: str  # "passed", "failed", "warning"
    details: str
    deployment_status: str = "unknown"  # "new", "updated", "unchanged", "unknown"


class BaseToolHandler(ToolHandler, ABC):
    """
    Abstract base class for tool handlers.

    Provides common functionality for:
    - File backup and restoration
    - Directory management and cleanup
    - Verification reporting
    - Deployment status checking

    Subclasses must implement:
    - __init__: Initialize handler-specific directories
    - deploy: Deploy content to tool-specific format
    - verify_deployment_with_details: Verify deployment with tool-specific checks
    """

    def __init__(self) -> None:
        """
        Initialize base handler.

        Subclasses should set:
        - self.name: Handler name (str)
        - self.base_path: Base path for deployment (Path)
        - self.prompts_dir: Directory for prompts (Path)
        - self.rules_dir: Directory for rules (Path)
        - self.tool_dir_constant: Tool directory constant (str) - e.g., ".continue" or ".kilocode"
        """
        # These must be set by subclasses
        self.name: str
        self.base_path: Path
        self.prompts_dir: Path
        self.rules_dir: Path
        self.tool_dir_constant: str

    def get_name(self) -> str:
        """
        Returns the name of the handler.

        Returns:
            Handler name
        """
        return self.name

    def get_status(self) -> str:
        """
        Returns the status of the handler.

        Returns:
            "active" if directories exist, "inactive" otherwise
        """
        if self.prompts_dir.exists() and self.rules_dir.exists():
            return "active"
        return "inactive"

    def _backup_file(self, file_path: Path) -> None:
        """Creates a backup of the given file.

        Args:
            file_path: Path to file to backup
        """
        if file_path.exists():
            backup_path = file_path.with_suffix(file_path.suffix + ".bak")
            file_path.rename(backup_path)
            logger.debug(f"Backed up {file_path.name} to {backup_path.name}")

    def _determine_deployment_status(self, target_file_path: Path, new_content: str) -> str:
        """
        Determine if the deployment is new, updated, or unchanged.

        Args:
            target_file_path: Path where the file will be deployed.
            new_content: The new content to be deployed.

        Returns:
            Status string: "new", "updated", or "unchanged".
        """
        if not target_file_path.exists():
            return "new"

        try:
            existing_content = target_file_path.read_text(encoding="utf-8")
            if existing_content == new_content:
                return "unchanged"
            return "updated"
        except (OSError, UnicodeDecodeError):
            # If we can't read the file, consider it as being updated
            return "updated"

    def _remove_empty_directories(self, base_dir: Path) -> None:
        """
        Removes empty directories within the base directory, walking bottom-up.

        Args:
            base_dir: The base directory to clean up empty subdirectories from.
        """
        # Walk the directory tree bottom-up to remove empty directories
        # We need to collect all directories first, then sort them by depth (deepest first)
        all_dirs = []
        for dir_path in base_dir.rglob("*"):
            if dir_path.is_dir():
                all_dirs.append(dir_path)

        # Sort by depth (deepest first) to ensure we remove nested empty dirs first
        all_dirs.sort(key=lambda p: len(p.parts), reverse=True)

        for dir_path in all_dirs:
            try:
                # Check if directory is empty
                if not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    console.print(f"[dim]Removed empty directory: {dir_path}[/dim]")
            except OSError:
                # Directory not empty or other issue, skip
                pass

    def validate_tool_installation(self) -> bool:
        """
        Validates that the tool installation is accessible.

        Checks that:
        1. base_path exists or can be created
        2. Tool directory exists or can be created
        3. Required subdirectories (prompts/, rules/) are accessible

        Returns:
            bool: True if validation succeeds

        Raises:
            PermissionError: If directories cannot be created due to permissions
            OSError: If directories cannot be created for other reasons
        """
        try:
            # Check if base_path exists and is accessible
            if not self.base_path.exists():
                console.print(
                    f"[yellow]Base path does not exist, attempting to create: "
                    f"{self.base_path}[/yellow]"
                )
                self.base_path.mkdir(parents=True, exist_ok=True)
                console.print(f"[green]Created base path: {self.base_path}[/green]")

            # Check if tool directory exists
            tool_dir = self.base_path / self.tool_dir_constant
            if not tool_dir.exists():
                console.print(
                    f"[yellow]{self.name.capitalize()} directory does not exist, "
                    f"attempting to create: {tool_dir}[/yellow]"
                )
                tool_dir.mkdir(parents=True, exist_ok=True)
                console.print(
                    f"[green]Created {self.name.capitalize()} directory: {tool_dir}[/green]"
                )

            # Verify prompts and rules directories are accessible
            if not self.prompts_dir.exists():
                self.prompts_dir.mkdir(parents=True, exist_ok=True)
                console.print(f"[green]Created prompts directory: {self.prompts_dir}[/green]")

            if not self.rules_dir.exists():
                self.rules_dir.mkdir(parents=True, exist_ok=True)
                console.print(f"[green]Created rules directory: {self.rules_dir}[/green]")

            # Verify directories are writable by attempting to create a test file
            test_file = self.prompts_dir / ".write_test"
            try:
                test_file.touch()
                test_file.unlink()
            except OSError as e:
                console.print(
                    f"[red]Error: {self.name.capitalize()} installation at "
                    f"{self.base_path} is not writable[/red]"
                )
                console.print(f"[red]Details: {e}[/red]")
                raise PermissionError(
                    f"{self.name.capitalize()} installation at {self.base_path} "
                    f"is not writable: {e}"
                ) from e

            console.print(
                f"[green]{self.name.capitalize()} installation validated at: "
                f"{self.base_path}[/green]"
            )
            return True

        except PermissionError as e:
            console.print(
                f"[red]Permission error validating {self.name.capitalize()} installation at "
                f"{self.base_path}[/red]"
            )
            console.print(f"[red]Details: {e}[/red]")
            console.print(
                f"[yellow]Suggestion: Check directory permissions for {self.base_path}[/yellow]"
            )
            raise

        except OSError as e:
            console.print(
                f"[red]Error validating {self.name.capitalize()} installation at "
                f"{self.base_path}[/red]"
            )
            console.print(f"[red]Details: {e}[/red]")
            console.print(
                f"[yellow]Suggestion: Ensure {self.base_path} is a valid path "
                f"and accessible[/yellow]"
            )
            raise

    def rollback(self) -> None:
        """
        Rolls back the deployment by restoring backup files.

        This method:
        1. Recursively finds all .bak files in subdirectories using BAK_GLOB_PATTERN pattern
        2. Restores each backup file to its original location
        3. Removes empty directories after restoration
        4. Logs warnings and continues if backup files are missing
        """
        # Restore backups in prompts directory recursively
        for backup_file in self.prompts_dir.glob(BAK_GLOB_PATTERN):
            original_path = backup_file.with_suffix("")
            try:
                # On Windows, rename() fails if destination exists, so remove it first
                if original_path.exists():
                    original_path.unlink()
                backup_file.rename(original_path)
                console.print(f"[yellow]Restored {original_path.name} from backup[/yellow]")
            except OSError as e:
                console.print(
                    f"[yellow]Warning: Could not restore {backup_file.name}: {e}[/yellow]"
                )
                continue

        # Restore backups in rules directory recursively
        for backup_file in self.rules_dir.glob(BAK_GLOB_PATTERN):
            original_path = backup_file.with_suffix("")
            try:
                # On Windows, rename() fails if destination exists, so remove it first
                if original_path.exists():
                    original_path.unlink()
                backup_file.rename(original_path)
                console.print(f"[yellow]Restored {original_path.name} from backup[/yellow]")
            except OSError as e:
                console.print(
                    f"[yellow]Warning: Could not restore {backup_file.name}: {e}[/yellow]"
                )
                continue

        # Clean up empty directories after restoration
        self._remove_empty_directories(self.prompts_dir)
        self._remove_empty_directories(self.rules_dir)

    def clean_orphaned_files(self, deployed_filenames: set[str]) -> int:
        """
        Remove files in prompts/rules directories that are not in the deployed set.
        Also removes any .bak backup files recursively (including in subdirectories).

        Note: Orphaned .md files are only removed from the root directory to preserve
        files from previous deployments with different tag filters.

        Args:
            deployed_filenames: Set of filenames that were just deployed.

        Returns:
            Number of files removed.
        """
        removed_count = 0

        # Remove .bak files recursively in prompts directory (including subdirectories)
        for file_path in self.prompts_dir.glob(BAK_GLOB_PATTERN):
            file_path.unlink()
            console.print(f"  [dim]Removed backup file: {file_path.name}[/dim]")
            removed_count += 1

        # Remove orphaned .md files ONLY in root prompts directory (not subdirectories)
        for file_path in self.prompts_dir.glob("*.md"):
            if file_path.name not in deployed_filenames:
                file_path.unlink()
                console.print(f"  [yellow]Removed orphaned prompt: {file_path.name}[/yellow]")
                removed_count += 1

        # Remove .bak files recursively in rules directory (including subdirectories)
        for file_path in self.rules_dir.glob(BAK_GLOB_PATTERN):
            file_path.unlink()
            console.print(f"  [dim]Removed backup file: {file_path.name}[/dim]")
            removed_count += 1

        # Remove orphaned .md files ONLY in root rules directory (not subdirectories)
        for file_path in self.rules_dir.glob("*.md"):
            if file_path.name not in deployed_filenames:
                file_path.unlink()
                console.print(f"  [yellow]Removed orphaned rule: {file_path.name}[/yellow]")
                removed_count += 1

        return removed_count

    def aggregate_verification_results(self, results: list[VerificationResult]) -> dict[str, int]:
        """
        Aggregates verification results into summary counts.

        Args:
            results: List of VerificationResult objects.

        Returns:
            Dictionary with counts for passed, failed, warnings, and total.
        """
        summary = {
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "total": len(results),
        }

        for result in results:
            if result.status == "passed":
                summary["passed"] += 1
            elif result.status == "failed":
                summary["failed"] += 1
            elif result.status == "warning":
                summary["warnings"] += 1

        return summary

    def display_verification_report(
        self,
        results: list[VerificationResult],
        console: Console | None = None,
    ) -> None:
        """
        Displays a Rich-formatted verification report.

        Args:
            results: List of VerificationResult objects to display.
            console: Optional Console instance for output. Uses module console if None.
        """
        output_console = globals()["console"] if console is None else console

        # Display header
        output_console.print()
        output_console.print(f"[bold]Deployment: {self.name}[/bold]")

        # Build Rich table with all columns like validate/status
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="blue")
        table.add_column("Status")
        table.add_column("Issues", style="dim")
        table.add_column("Path", style="dim", overflow="fold")

        # Collect detailed errors/warnings for separate display
        detailed_issues: list[tuple[str, str, str]] = []

        for result in results:
            # Determine status color and text
            if result.status == "passed":
                status_color = SUCCESS_COLOR
                base_status = "PASSED"
                issues_text = "None"
            elif result.status == "failed":
                status_color = ERROR_COLOR
                base_status = "FAILED"
                issues_text = f"[{ERROR_COLOR}]1 error[/{ERROR_COLOR}]"
                detailed_issues.append((result.file_name, "ERROR", result.details))
            else:  # warning
                status_color = WARNING_COLOR
                base_status = "WARNING"
                issues_text = f"[{WARNING_COLOR}]1 warning[/{WARNING_COLOR}]"
                detailed_issues.append((result.file_name, "WARNING", result.details))

            # Add deployment status indicator
            if result.deployment_status == "new":
                status_indicator = "[cyan](NEW)[/cyan]"
            elif result.deployment_status == "updated":
                status_indicator = "[yellow](UPDATED)[/yellow]"
            elif result.deployment_status == "unchanged":
                status_indicator = "[dim](UNCHANGED)[/dim]"
            elif result.deployment_status == "deleted":
                status_indicator = "[red](DELETED)[/red]"
            else:
                status_indicator = ""

            status_text = (
                f"[{status_color}]{base_status}[/{status_color}] {status_indicator}"
                if status_indicator
                else f"[{status_color}]{base_status}[/{status_color}]"
            )

            # Get file path - try to get from handler's directories
            file_path = self._get_deployed_file_path(result)

            table.add_row(
                result.file_name,
                result.content_type,
                status_text,
                issues_text,
                str(file_path),
            )

        output_console.print(table)

        # Display summary
        summary = self.aggregate_verification_results(results)
        output_console.print()
        output_console.print(
            f"[bold]Summary:[/bold] {summary['passed']} passed, "
            f"{summary['failed']} failed, {summary['warnings']} warnings"
        )

        # Display detailed issues only if there are any
        if detailed_issues:
            output_console.print()
            output_console.print("[bold]Issues:[/bold]")
            for name, issue_type, details in detailed_issues:
                if issue_type == "ERROR":
                    output_console.print(f"  [{ERROR_COLOR}]✗ {name}:[/{ERROR_COLOR}] {details}")
                else:
                    output_console.print(
                        f"  [{WARNING_COLOR}]⚠ {name}:[/{WARNING_COLOR}] {details}"
                    )

        output_console.print()

    def _get_deployed_file_path(self, result: VerificationResult) -> Path:
        """Get the full path of a deployed file based on verification result.

        Args:
            result: The verification result containing file name and type.

        Returns:
            Path to the deployed file.
        """
        # This is a base implementation - subclasses can override if needed
        base_dir = self.prompts_dir if result.content_type == "prompt" else self.rules_dir

        # Try to find the file
        file_name = (
            result.file_name if result.file_name.endswith(".md") else f"{result.file_name}.md"
        )

        # Search in base directory and subdirectories
        for path in base_dir.rglob(file_name):
            return path

        # Fallback to simple concatenation
        return base_dir / file_name

    def _compare_content_hashes(self, source_content: str, target_file: Path) -> str:
        """Compare content hashes between source and deployed file.

        Args:
            source_content: The expected content string.
            target_file: Path to the deployed file.

        Returns:
            Status string: "synced", "outdated", or "error".
        """
        try:
            deployed_content = target_file.read_text(encoding="utf-8")
            source_hash = sha256(source_content.encode("utf-8")).hexdigest()
            deployed_hash = sha256(deployed_content.encode("utf-8")).hexdigest()
            return "synced" if source_hash == deployed_hash else "outdated"
        except (OSError, UnicodeDecodeError):
            return "error"
