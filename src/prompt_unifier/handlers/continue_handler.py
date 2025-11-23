from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

import yaml
from rich.console import Console
from rich.table import Table

from prompt_unifier.handlers.protocol import ToolHandler
from prompt_unifier.models.prompt import PromptFrontmatter
from prompt_unifier.models.rule import RuleFrontmatter

console = Console()

# Color constants matching RichFormatter patterns
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


class ContinueToolHandler(ToolHandler):
    """
    Tool handler for Continue AI assistant.
    Deploys prompts and rules to the appropriate Continue directories.
    """

    def __init__(self, base_path: Path | None = None):
        self.name = "continue"
        # CRITICAL CHANGE: Default base_path is now Path.cwd() instead of Path.home()
        self.base_path = base_path if base_path else Path.cwd()
        self.prompts_dir = self.base_path / ".continue" / "prompts"
        self.rules_dir = self.base_path / ".continue" / "rules"

        # Auto-create directories with informative output
        if not self.prompts_dir.exists():
            self.prompts_dir.mkdir(parents=True, exist_ok=True)
            console.print(f"[cyan]Created Continue prompts directory: {self.prompts_dir}[/cyan]")
        if not self.rules_dir.exists():
            self.rules_dir.mkdir(parents=True, exist_ok=True)
            console.print(f"[cyan]Created Continue rules directory: {self.rules_dir}[/cyan]")

    def validate_tool_installation(self) -> bool:
        """
        Validates that the Continue tool installation is accessible.

        Checks that:
        1. base_path exists or can be created
        2. .continue/ directory exists or can be created
        3. Required subdirectories (prompts/, rules/) are accessible

        Returns:
            bool: True if validation succeeds

        Raises:
            PermissionError: If directories cannot be created due to permissions
            OSError: If directories cannot be created for other reasons

        Examples:
            >>> handler = ContinueToolHandler()
            >>> handler.validate_tool_installation()
            True
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

            # Check if .continue directory exists
            continue_dir = self.base_path / ".continue"
            if not continue_dir.exists():
                console.print(
                    f"[yellow]Continue directory does not exist, "
                    f"attempting to create: {continue_dir}[/yellow]"
                )
                continue_dir.mkdir(parents=True, exist_ok=True)
                console.print(f"[green]Created Continue directory: {continue_dir}[/green]")

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
            except (PermissionError, OSError) as e:
                console.print(
                    f"[red]Error: Continue installation at {self.base_path} is not writable[/red]"
                )
                console.print(f"[red]Details: {e}[/red]")
                raise PermissionError(
                    f"Continue installation at {self.base_path} is not writable: {e}"
                ) from e

            console.print(f"[green]Continue installation validated at: {self.base_path}[/green]")
            return True

        except PermissionError as e:
            console.print(
                f"[red]Permission error validating Continue installation at {self.base_path}[/red]"
            )
            console.print(f"[red]Details: {e}[/red]")
            console.print(
                f"[yellow]Suggestion: Check directory permissions for {self.base_path}[/yellow]"
            )
            raise

        except OSError as e:
            console.print(f"[red]Error validating Continue installation at {self.base_path}[/red]")
            console.print(f"[red]Details: {e}[/red]")
            console.print(
                f"[yellow]Suggestion: Ensure {self.base_path} is a valid path "
                f"and accessible[/yellow]"
            )
            raise

    def _backup_file(self, file_path: Path) -> None:
        """Creates a backup of the given file."""
        if file_path.exists():
            backup_path = file_path.with_suffix(file_path.suffix + ".bak")
            file_path.rename(backup_path)
            console.print(f"[yellow]Backed up {file_path.name} to {backup_path.name}[/yellow]")

    def _process_prompt_content(self, prompt: PromptFrontmatter, body: str) -> str:
        """
        Processes the prompt content for Continue, ensuring invokable: true is set.
        """
        # Map our model fields to Continue's expected format
        continue_frontmatter = {
            "name": prompt.title,
            "description": prompt.description,
            "invokable": True,  # Always true for Continue prompts
        }
        # Add optional fields if present
        if prompt.category:
            continue_frontmatter["category"] = prompt.category
        if prompt.version:
            continue_frontmatter["version"] = prompt.version
        if prompt.tags:
            continue_frontmatter["tags"] = prompt.tags
        if prompt.author:
            continue_frontmatter["author"] = prompt.author
        if prompt.language:
            continue_frontmatter["language"] = prompt.language

        frontmatter_str = yaml.safe_dump(continue_frontmatter, sort_keys=False)
        # Remove trailing newline from YAML dump to avoid blank line before closing ---
        return f"---\n{frontmatter_str.rstrip()}\n---\n{body}"

    def _process_rule_content(self, rule: RuleFrontmatter, body: str) -> str:
        """
        Processes the rule content for Continue.
        """
        # Map our model fields to Continue's expected format
        continue_frontmatter: dict[str, Any] = {
            "name": rule.title,
        }
        # Add optional fields as per Continue spec
        if rule.description:
            continue_frontmatter["description"] = rule.description
        if rule.applies_to:
            continue_frontmatter["globs"] = rule.applies_to
        continue_frontmatter["alwaysApply"] = False
        if rule.category:
            continue_frontmatter["category"] = rule.category
        if rule.version:
            continue_frontmatter["version"] = rule.version
        if rule.tags:
            continue_frontmatter["tags"] = rule.tags
        if rule.author:
            continue_frontmatter["author"] = rule.author
        if rule.language:
            continue_frontmatter["language"] = rule.language

        frontmatter_str = yaml.safe_dump(continue_frontmatter, sort_keys=False)
        # Remove trailing newline from YAML dump to avoid blank line before closing ---
        return f"---\n{frontmatter_str.rstrip()}\n---\n{body}"

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
        # glob("**/*.bak") only matches files, not directories
        for file_path in self.prompts_dir.glob("**/*.bak"):
            file_path.unlink()
            console.print(f"  [dim]Removed backup file: {file_path.name}[/dim]")
            removed_count += 1

        # Remove orphaned .md files ONLY in root prompts directory (not subdirectories)
        # glob("*.md") only matches files, not directories
        for file_path in self.prompts_dir.glob("*.md"):
            if file_path.name not in deployed_filenames:
                file_path.unlink()
                console.print(f"  [yellow]Removed orphaned prompt: {file_path.name}[/yellow]")
                removed_count += 1

        # Remove .bak files recursively in rules directory (including subdirectories)
        # glob("**/*.bak") only matches files, not directories
        for file_path in self.rules_dir.glob("**/*.bak"):
            file_path.unlink()
            console.print(f"  [dim]Removed backup file: {file_path.name}[/dim]")
            removed_count += 1

        # Remove orphaned .md files ONLY in root rules directory (not subdirectories)
        # glob("*.md") only matches files, not directories
        for file_path in self.rules_dir.glob("*.md"):
            if file_path.name not in deployed_filenames:
                file_path.unlink()
                console.print(f"  [yellow]Removed orphaned rule: {file_path.name}[/yellow]")
                removed_count += 1

        return removed_count

    def deploy(
        self,
        content: Any,
        content_type: str,
        body: str = "",
        source_filename: str | None = None,
        relative_path: Path | None = None,
    ) -> None:
        """
        Deploys a prompt or rule to the Continue directories.

        Args:
            content: The content object (PromptFrontmatter or RuleFrontmatter).
            content_type: Type of content ("prompt" or "rule").
            body: The body content as a string.
            source_filename: Original filename to preserve. If None, uses content.title.
            relative_path: Relative path from prompts/ or rules/ directory to preserve
                          subdirectory structure. If None, deploys to root directory.
        """
        # Determine target filename: use source_filename if provided, else content.title
        if source_filename:
            # Ensure it has .md extension
            filename = (
                source_filename if source_filename.endswith(".md") else f"{source_filename}.md"
            )
        else:
            # Fallback to title-based naming for backward compatibility
            filename = f"{content.title}.md"

        if content_type == "prompt":
            if not isinstance(content, PromptFrontmatter):
                raise ValueError("Content must be a PromptFrontmatter instance for type 'prompt'")
            processed_content = self._process_prompt_content(content, body)
            base_dir = self.prompts_dir
        elif content_type == "rule":
            if not isinstance(content, RuleFrontmatter):
                raise ValueError("Content must be a RuleFrontmatter instance for type 'rule'")
            processed_content = self._process_rule_content(content, body)
            base_dir = self.rules_dir
        else:
            raise ValueError(f"Unsupported content type: {content_type}")

        # Construct target path with subdirectory structure if relative_path is provided
        if relative_path and str(relative_path) != ".":
            # Create subdirectory structure
            target_dir = base_dir / relative_path
            target_dir.mkdir(parents=True, exist_ok=True)
            target_file_path = target_dir / filename
        else:
            # Deploy to root directory
            target_file_path = base_dir / filename

        self._backup_file(target_file_path)
        target_file_path.write_text(processed_content, encoding="utf-8")
        console.print(
            f"[green]Deployed {content.title} ({content_type}) to {target_file_path}[/green]"
        )

    def get_status(self) -> str:
        """
        Returns the status of the Continue handler.
        """
        if self.prompts_dir.exists() and self.rules_dir.exists():
            return "active"
        return "inactive"

    def get_name(self) -> str:
        """
        Returns the name of the handler.
        """
        return self.name

    def verify_deployment(self, content_name: str, content_type: str) -> bool:
        """
        Verifies if a specific content item has been deployed correctly.
        """
        if content_type == "prompt":
            target_file_path = self.prompts_dir / f"{content_name}.md"
        elif content_type == "rule":
            target_file_path = self.rules_dir / f"{content_name}.md"
        else:
            return False

        if not target_file_path.exists():
            return False

        # Basic content verification (can be expanded if needed)
        deployed_content = target_file_path.read_text(encoding="utf-8")

        # For prompts, check if invokable: true is present in frontmatter
        if content_type == "prompt":
            # Extract frontmatter
            parts = deployed_content.split("---", 2)
            if len(parts) < 3:
                return False  # Invalid format

            frontmatter_str = parts[1].strip()
            try:
                frontmatter = yaml.safe_load(frontmatter_str)
                if not isinstance(frontmatter, dict) or not frontmatter.get("invokable"):
                    return False
            except yaml.YAMLError:
                return False  # Invalid YAML
        return True

    def verify_deployment_with_details(
        self,
        content_name: str,
        content_type: str,
        file_name: str,
        relative_path: Path | None = None,
    ) -> VerificationResult:
        """
        Verifies if a specific content item has been deployed correctly and returns
        detailed result information.

        Args:
            content_name: The name/title of the content item (used for display).
            content_type: Type of content ("prompt" or "rule").
            file_name: The actual filename of the deployed file (used for lookup).
            relative_path: Relative subdirectory path where the file was deployed.

        Returns:
            VerificationResult with status and details.
        """
        # Ensure file_name has .md extension
        actual_file_name = file_name if file_name.endswith(".md") else f"{file_name}.md"

        if content_type == "prompt":
            base_dir = self.prompts_dir
        elif content_type == "rule":
            base_dir = self.rules_dir
        else:
            return VerificationResult(
                file_name=file_name,
                content_type=content_type,
                status="failed",
                details=f"Unsupported content type: {content_type}",
            )

        # Construct target path with subdirectory structure if relative_path is provided
        if relative_path and str(relative_path) != ".":
            target_file_path = base_dir / relative_path / actual_file_name
        else:
            # Deploy to root directory
            target_file_path = base_dir / actual_file_name

        if not target_file_path.exists():
            return VerificationResult(
                file_name=file_name,
                content_type=content_type,
                status="failed",
                details=f"File does not exist: {target_file_path}",
            )

        # Basic content verification
        try:
            deployed_content = target_file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            return VerificationResult(
                file_name=file_name,
                content_type=content_type,
                status="failed",
                details=f"Cannot read file: {e}",
            )

        # For prompts, check if invokable: true is present in frontmatter
        if content_type == "prompt":
            # Extract frontmatter
            parts = deployed_content.split("---", 2)
            if len(parts) < 3:
                return VerificationResult(
                    file_name=file_name,
                    content_type=content_type,
                    status="failed",
                    details="Invalid format: missing frontmatter delimiters",
                )

            frontmatter_str = parts[1].strip()
            try:
                frontmatter = yaml.safe_load(frontmatter_str)
                if not isinstance(frontmatter, dict):
                    return VerificationResult(
                        file_name=file_name,
                        content_type=content_type,
                        status="failed",
                        details="Invalid frontmatter: not a dictionary",
                    )
                if not frontmatter.get("invokable"):
                    return VerificationResult(
                        file_name=file_name,
                        content_type=content_type,
                        status="failed",
                        details="Missing or false 'invokable' field in frontmatter",
                    )
            except yaml.YAMLError as e:
                return VerificationResult(
                    file_name=file_name,
                    content_type=content_type,
                    status="failed",
                    details=f"Invalid YAML frontmatter: {e}",
                )

        return VerificationResult(
            file_name=file_name,
            content_type=content_type,
            status="passed",
            details="File verified successfully",
        )

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

        # Display header with handler name
        output_console.print()
        output_console.print(f"[bold]Verification Report: {self.name}[/bold]")
        output_console.print("-" * 60)

        # Build Rich table
        table = Table(show_header=True, header_style="bold")
        table.add_column("File", style="dim")
        table.add_column("Type")
        table.add_column("Status")
        table.add_column("Details", style="dim")

        for result in results:
            # Determine status color
            if result.status == "passed":
                status_color = SUCCESS_COLOR
                status_text = f"[{status_color}]PASSED[/{status_color}]"
            elif result.status == "failed":
                status_color = ERROR_COLOR
                status_text = f"[{status_color}]FAILED[/{status_color}]"
            else:  # warning
                status_color = WARNING_COLOR
                status_text = f"[{status_color}]WARNING[/{status_color}]"

            table.add_row(
                result.file_name,
                result.content_type,
                status_text,
                result.details,
            )

        output_console.print(table)

        # Display summary
        summary = self.aggregate_verification_results(results)
        output_console.print()
        output_console.print("[bold]Summary:[/bold]")
        output_console.print(f"  Total: {summary['total']}")
        output_console.print(f"  Passed: [{SUCCESS_COLOR}]{summary['passed']}[/{SUCCESS_COLOR}]")
        output_console.print(f"  Failed: [{ERROR_COLOR}]{summary['failed']}[/{ERROR_COLOR}]")
        output_console.print(
            f"  Warnings: [{WARNING_COLOR}]{summary['warnings']}[/{WARNING_COLOR}]"
        )

        # Show warning message if there are failures
        if summary["failed"] > 0:
            output_console.print()
            output_console.print(
                f"[{WARNING_COLOR}]Warning: {summary['failed']} verification(s) failed. "
                f"Review the details above.[/{WARNING_COLOR}]"
            )

        output_console.print()

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

    def rollback(self) -> None:
        """
        Rolls back the deployment by restoring backup files.

        This method:
        1. Recursively finds all .bak files in subdirectories using **/*.bak pattern
        2. Restores each backup file to its original location
        3. Removes empty directories after restoration
        4. Logs warnings and continues if backup files are missing
        """
        # Restore backups in prompts directory recursively
        for backup_file in self.prompts_dir.glob("**/*.bak"):
            original_path = backup_file.with_suffix("")
            try:
                backup_file.rename(original_path)
                console.print(f"[yellow]Restored {original_path.name} from backup[/yellow]")
            except (OSError, FileNotFoundError) as e:
                console.print(
                    f"[yellow]Warning: Could not restore {backup_file.name}: {e}[/yellow]"
                )
                continue

        # Restore backups in rules directory recursively
        for backup_file in self.rules_dir.glob("**/*.bak"):
            original_path = backup_file.with_suffix("")
            try:
                backup_file.rename(original_path)
                console.print(f"[yellow]Restored {original_path.name} from backup[/yellow]")
            except (OSError, FileNotFoundError) as e:
                console.print(
                    f"[yellow]Warning: Could not restore {backup_file.name}: {e}[/yellow]"
                )
                continue

        # Clean up empty directories after restoration
        self._remove_empty_directories(self.prompts_dir)
        self._remove_empty_directories(self.rules_dir)

    def get_deployment_status(
        self,
        content_name: str,
        content_type: str,
        source_content: str,
        source_filename: str | None = None,
        relative_path: Path | None = None,  # Added relative_path parameter
    ) -> str:
        """
        Check the deployment status of a content item.

        Args:
            content_name: The name/title of the content item.
            content_type: Type of content ("prompt" or "rule").
            source_content: The expected content string (processed).
            source_filename: Optional specific filename if different from title.
            relative_path: Relative subdirectory path where the file was deployed.

        Returns:
            Status string: "synced", "outdated", "missing", or "error".
        """
        # Determine target filename
        if source_filename:
            filename = (
                source_filename if source_filename.endswith(".md") else f"{source_filename}.md"
            )
        else:
            filename = f"{content_name}.md"

        # Determine target directory and file path, accounting for relative_path
        if content_type == "prompt":
            base_dir = self.prompts_dir
        elif content_type == "rule":
            base_dir = self.rules_dir
        else:
            return "error"

        if relative_path and str(relative_path) != ".":
            target_file = base_dir / relative_path / filename
        else:
            target_file = base_dir / filename

        # Check existence
        if not target_file.exists():
            return "missing"

        try:
            # Read deployed content
            deployed_content = target_file.read_text(encoding="utf-8")

            # Compare content hashes for robustness against whitespace issues
            # (though currently we expect exact matches, hashing is good practice)
            source_hash = sha256(source_content.encode("utf-8")).hexdigest()
            deployed_hash = sha256(deployed_content.encode("utf-8")).hexdigest()

            if source_hash == deployed_hash:
                return "synced"
            else:
                return "outdated"

        except (OSError, UnicodeDecodeError):
            return "error"
