from pathlib import Path
from typing import Any

import yaml
from rich.console import Console

from prompt_unifier.handlers.protocol import ToolHandler
from prompt_unifier.models.prompt import PromptFrontmatter
from prompt_unifier.models.rule import RuleFrontmatter

console = Console()


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

    def rollback(self) -> None:
        """
        Rolls back the deployment by restoring backup files.
        """
        # Restore backups if they exist
        for backup_file in self.prompts_dir.glob("*.bak"):
            original_path = backup_file.with_suffix("")
            backup_path = self.prompts_dir / backup_file.name
            backup_path.rename(original_path)
            console.print(f"[yellow]Restored {original_path.name} from backup[/yellow]")

        for backup_file in self.rules_dir.glob("*.bak"):
            original_path = backup_file.with_suffix("")
            backup_path = self.rules_dir / backup_file.name
            backup_path.rename(original_path)
            console.print(f"[yellow]Restored {original_path.name} from backup[/yellow]")
