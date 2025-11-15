from pathlib import Path
from typing import Any

import yaml
from rich.console import Console

from prompt_manager.handlers.protocol import ToolHandler
from prompt_manager.models.prompt import PromptFrontmatter
from prompt_manager.models.rule import RuleFrontmatter

console = Console()


class ContinueToolHandler(ToolHandler):
    """
    Tool handler for Continue AI assistant.
    Deploys prompts and rules to the appropriate Continue directories.
    """

    def __init__(self, base_path: Path | None = None):
        self.name = "continue"
        self.base_path = base_path if base_path else Path.home()
        self.prompts_dir = self.base_path / ".continue" / "prompts"
        self.rules_dir = self.base_path / ".continue" / "rules"
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        self.rules_dir.mkdir(parents=True, exist_ok=True)

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
        return f"---\n{frontmatter_str}\n---\n{body}"

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
        return f"---\n{frontmatter_str}\n---\n{body}"

    def deploy(self, content: Any, content_type: str, body: str = "") -> None:
        """
        Deploys a prompt or rule to the Continue directories.
        """
        if content_type == "prompt":
            if not isinstance(content, PromptFrontmatter):
                raise ValueError("Content must be a PromptFrontmatter instance for type 'prompt'")
            processed_content = self._process_prompt_content(content, body)
            target_file_path = self.prompts_dir / f"{content.title}.md"
        elif content_type == "rule":
            if not isinstance(content, RuleFrontmatter):
                raise ValueError("Content must be a RuleFrontmatter instance for type 'rule'")
            processed_content = self._process_rule_content(content, body)
            target_file_path = self.rules_dir / f"{content.title}.md"
        else:
            raise ValueError(f"Unsupported content type: {content_type}")

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
