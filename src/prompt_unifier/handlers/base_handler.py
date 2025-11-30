"""Base handler class with shared functionality for tool handlers."""

import logging
from abc import ABC
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

import yaml
from rich.console import Console
from rich.table import Table

from prompt_unifier.constants import BAK_GLOB_PATTERN, KILO_CODE_MEMORY_BANK_DIR
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
    actual_file_path: str | None = None  # New field for actual file system path


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
        self.logger = logging.getLogger(__name__)
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
            if backup_path.exists():
                backup_path.unlink()
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
                # KiloCode specific exclusion: Do not remove .kilocode/rules/memory-bank directory
                if (
                    self.name == "kilocode"
                    and base_dir == self.rules_dir
                    and dir_path == self.rules_dir / KILO_CODE_MEMORY_BANK_DIR
                ):
                    continue

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

    def _extract_title_from_md_file(self, file_path: Path) -> str | None:
        """
        Extracts the 'name' from the YAML frontmatter of a markdown file.
        Returns None if frontmatter is missing or parsing fails.
        """
        try:
            content = file_path.read_text(encoding="utf-8")
            parts = content.split("---", 2)
            if len(parts) < 3:
                return None  # Missing frontmatter delimiters

            frontmatter_str = parts[1].strip()
            frontmatter = yaml.safe_load(frontmatter_str)

            if isinstance(frontmatter, dict) and "name" in frontmatter:
                return str(frontmatter["name"])
        except (OSError, UnicodeDecodeError, yaml.YAMLError) as e:
            logger.warning(f"Failed to extract title from {file_path}: {e}")
        return None

    def _remove_backup_files(
        self, directory: Path, content_type: str, results: list[VerificationResult]
    ) -> None:
        """Remove .bak files and track them in results."""
        for file_path in directory.glob(BAK_GLOB_PATTERN):
            results.append(
                VerificationResult(
                    file_name=file_path.name,
                    content_type=content_type,
                    status="passed",
                    details="Backup file removed successfully",
                    deployment_status="deleted",
                    actual_file_path=str(file_path),
                )
            )
            file_path.unlink()

    def _remove_orphaned_md_files(
        self,
        directory: Path,
        content_type: str,
        deployed_filenames: set[str],
        use_recursive: bool,
        results: list[VerificationResult],
    ) -> None:
        """Remove orphaned .md files and track them in results."""
        glob_func = directory.rglob if use_recursive else directory.glob
        for file_path in glob_func("*.md"):
            if self._should_skip_file(file_path, content_type):
                continue

            rel_path = str(file_path.relative_to(directory))
            if rel_path not in deployed_filenames:
                self._remove_and_track_file(file_path, content_type, results)

    def _should_skip_file(self, file_path: Path, content_type: str) -> bool:
        """Check if file should be skipped during cleanup."""
        if content_type == "rule" and self.name == "kilocode":
            return (
                KILO_CODE_MEMORY_BANK_DIR in file_path.parts
                and file_path.parent == self.rules_dir / KILO_CODE_MEMORY_BANK_DIR
            )
        return False

    def _remove_and_track_file(
        self, file_path: Path, content_type: str, results: list[VerificationResult]
    ) -> None:
        """Remove a file and add it to results tracking."""
        extracted_title = self._extract_title_from_md_file(file_path)
        content_name = extracted_title if extracted_title else file_path.stem

        file_path.unlink()
        results.append(
            VerificationResult(
                file_name=content_name,
                content_type=content_type,
                status="passed",
                details="File removed successfully",
                deployment_status="deleted",
                actual_file_path=str(file_path),
            )
        )

    def clean_orphaned_files(self, deployed_filenames: set[str]) -> list[VerificationResult]:
        """
        Remove files in prompts/rules directories that are not in the deployed set.
        Also removes any .bak backup files recursively (including in subdirectories).

        Args:
            deployed_filenames: Set of filenames (including relative paths) that were just deployed.

        Returns:
            List of VerificationResult objects for removed files.
        """
        removed_results: list[VerificationResult] = []
        use_recursive = self.name == "kilocode"

        # Clean prompts directory
        self._remove_backup_files(self.prompts_dir, "prompt", removed_results)
        self._remove_orphaned_md_files(
            self.prompts_dir, "prompt", deployed_filenames, use_recursive, removed_results
        )

        # Clean rules directory
        self._remove_backup_files(self.rules_dir, "rule", removed_results)
        self._remove_orphaned_md_files(
            self.rules_dir, "rule", deployed_filenames, use_recursive, removed_results
        )

        # Clean up empty directories
        self._remove_empty_directories(self.prompts_dir)
        self._remove_empty_directories(self.rules_dir)

        return removed_results

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

    def _format_status_info(
        self, result: VerificationResult, detailed_issues: list[tuple[str, str, str]]
    ) -> tuple[str, str, str]:
        """Format status color, text and issues for a result."""
        if result.status == "passed":
            return SUCCESS_COLOR, "PASSED", "None"
        elif result.status == "failed":
            detailed_issues.append((result.file_name, "ERROR", result.details))
            return ERROR_COLOR, "FAILED", f"[{ERROR_COLOR}]1 error[/{ERROR_COLOR}]"
        else:  # warning
            detailed_issues.append((result.file_name, "WARNING", result.details))
            return WARNING_COLOR, "WARNING", f"[{WARNING_COLOR}]1 warning[/{WARNING_COLOR}]"

    def _get_deployment_status_indicator(self, deployment_status: str | None) -> str:
        """Get formatted deployment status indicator."""
        status_map = {
            "new": "[cyan](NEW)[/cyan]",
            "updated": "[yellow](UPDATED)[/yellow]",
            "unchanged": "[dim](UNCHANGED)[/dim]",
            "deleted": "[red](DELETED)[/red]",
        }
        return status_map.get(deployment_status or "", "")

    def _build_verification_table(
        self, results: list[VerificationResult], detailed_issues: list[tuple[str, str, str]]
    ) -> Table:
        """Build Rich table with verification results."""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="blue")
        table.add_column("Status")
        table.add_column("Issues", style="dim")
        table.add_column("Path", style="dim", overflow="fold")

        for result in results:
            status_color, base_status, issues_text = self._format_status_info(
                result, detailed_issues
            )
            status_indicator = self._get_deployment_status_indicator(result.deployment_status)

            status_text = (
                f"[{status_color}]{base_status}[/{status_color}] {status_indicator}"
                if status_indicator
                else f"[{status_color}]{base_status}[/{status_color}]"
            )

            file_path = self._get_deployed_file_path(result)
            table.add_row(
                result.file_name, result.content_type, status_text, issues_text, str(file_path)
            )

        return table

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

        # Build and display table
        detailed_issues: list[tuple[str, str, str]] = []
        table = self._build_verification_table(results, detailed_issues)
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
        if result.actual_file_path:
            return Path(result.actual_file_path)

        # This is a fallback in case actual_file_path is not set
        # (should not happen if all previous steps are correct)
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
