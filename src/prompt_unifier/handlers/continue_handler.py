import logging
from pathlib import Path
from typing import Any

import yaml

from prompt_unifier.constants import CONTINUE_DIR
from prompt_unifier.handlers.base_handler import BaseToolHandler, VerificationResult
from prompt_unifier.handlers.handler_utils import console
from prompt_unifier.models.prompt import PromptFrontmatter
from prompt_unifier.models.rule import RuleFrontmatter

logger = logging.getLogger(__name__)


class ContinueToolHandler(BaseToolHandler):
    """
    Tool handler for Continue AI assistant.
    Deploys prompts and rules to the appropriate Continue directories.
    """

    def __init__(self, base_path: Path | None = None):
        super().__init__()
        self.name = "continue"
        # CRITICAL CHANGE: Default base_path is now Path.cwd() instead of Path.home()
        self.base_path = base_path if base_path else Path.cwd()
        self.tool_dir_constant = CONTINUE_DIR
        self.prompts_dir = self.base_path / CONTINUE_DIR / "prompts"
        self.rules_dir = self.base_path / CONTINUE_DIR / "rules"

        # Track deployment statuses for verification
        self._deployment_statuses: dict[str, str] = {}

        # Auto-create directories with informative output
        if not self.prompts_dir.exists():
            self.prompts_dir.mkdir(parents=True, exist_ok=True)
            console.print(f"[cyan]Created Continue prompts directory: {self.prompts_dir}[/cyan]")
        if not self.rules_dir.exists():
            self.rules_dir.mkdir(parents=True, exist_ok=True)
            console.print(f"[cyan]Created Continue rules directory: {self.rules_dir}[/cyan]")

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

        # Determine deployment status before deploying
        deployment_status = self._determine_deployment_status(target_file_path, processed_content)
        self._deployment_statuses[content.title] = deployment_status

        self._backup_file(target_file_path)
        target_file_path.write_text(processed_content, encoding="utf-8")
        logger.debug(f"Deployed {content.title} ({content_type}) to {target_file_path}")

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

    def _get_target_file_path(
        self,
        content_type: str,
        file_path_in_handler_dir: str,
    ) -> tuple[Path | None, str | None]:
        """Get target file path and validate content type."""
        if content_type == "prompt":
            base_dir = self.prompts_dir
        elif content_type == "rule":
            base_dir = self.rules_dir
        else:
            return None, f"Unsupported content type: {content_type}"

        target_file_path = base_dir / file_path_in_handler_dir

        return target_file_path, None

    def _verify_prompt_frontmatter(
        self,
        deployed_content: str,
        content_name: str,
    ) -> VerificationResult | None:
        """Verify prompt frontmatter has invokable field. Returns error result or None if OK."""
        parts = deployed_content.split("---", 2)
        if len(parts) < 3:
            return VerificationResult(
                file_name=content_name,
                content_type="prompt",
                status="failed",
                details="Invalid format: missing frontmatter delimiters",
            )

        frontmatter_str = parts[1].strip()
        try:
            frontmatter = yaml.safe_load(frontmatter_str)
            if not isinstance(frontmatter, dict):
                return VerificationResult(
                    file_name=content_name,
                    content_type="prompt",
                    status="failed",
                    details="Invalid frontmatter: not a dictionary",
                )
            if not frontmatter.get("invokable"):
                return VerificationResult(
                    file_name=content_name,
                    content_type="prompt",
                    status="failed",
                    details="Missing or false 'invokable' field in frontmatter",
                )
        except yaml.YAMLError as e:
            return VerificationResult(
                file_name=content_name,
                content_type="prompt",
                status="failed",
                details=f"Invalid YAML frontmatter: {e}",
            )

        return None  # No error, verification passed

    def verify_deployment_with_details(
        self,
        content_name: str,
        content_type: str,
        file_name: str,
    ) -> VerificationResult:
        """
        Verifies if a specific content item has been deployed correctly and returns
        detailed result information.

        Args:
            content_name: The name/title of the content item (used for display).
            content_type: Type of content ("prompt" or "rule").
            file_name: The actual filename of the deployed file (used for lookup).

        Returns:
            VerificationResult with status and details.
        """
        logger.debug(f"Verifying deployment: '{content_name}' ({content_type}) at '{file_name}'")

        target_file_path, error = self._get_target_file_path(content_type, file_name)
        if error or target_file_path is None:
            return VerificationResult(
                file_name=content_name,
                content_type=content_type,
                status="failed",
                details=error or "Invalid path",
            )

        if not target_file_path.exists():
            return VerificationResult(
                file_name=content_name,
                content_type=content_type,
                status="failed",
                details=f"File does not exist: {target_file_path}",
            )

        try:
            deployed_content = target_file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            return VerificationResult(
                file_name=content_name,
                content_type=content_type,
                status="failed",
                details=f"Cannot read file: {e}",
            )

        if content_type == "prompt":
            error_result = self._verify_prompt_frontmatter(deployed_content, content_name)
            if error_result:
                return error_result

        # Retrieve deployment status from tracking dictionary
        deployment_status = self._deployment_statuses.get(content_name, "unknown")

        result = VerificationResult(
            file_name=content_name,
            content_type=content_type,
            status="passed",
            details="File verified successfully",
            deployment_status=deployment_status,
            actual_file_path=str(target_file_path),
        )
        return result

    def _determine_target_filename(self, content_name: str, source_filename: str | None) -> str:
        """Determine the target filename for deployment status check.

        Args:
            content_name: The name/title of the content item.
            source_filename: Optional specific filename if different from title.

        Returns:
            The filename to use for the target file.
        """
        if source_filename:
            return source_filename if source_filename.endswith(".md") else f"{source_filename}.md"
        return f"{content_name}.md"

    def _determine_target_file_path(
        self,
        content_type: str,
        file_path_in_handler_dir: str,
    ) -> Path | None:
        """Determine the target file path for deployment status check."""
        if content_type == "prompt":
            base_dir = self.prompts_dir
        elif content_type == "rule":
            base_dir = self.rules_dir
        else:
            return None

        return base_dir / file_path_in_handler_dir

    def get_deployment_status(
        self,
        content_name: str,
        content_type: str,
        source_content: str,
        source_filename: str | None = None,
        relative_path: Path | None = None,
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
        actual_filename = self._determine_target_filename(content_name, source_filename)

        # Combine relative_path and actual_filename to form file_path_in_handler_dir
        if relative_path and str(relative_path) != ".":
            combined_path = relative_path / actual_filename
            file_path_in_handler_dir = str(combined_path)
        else:
            file_path_in_handler_dir = actual_filename

        target_file = self._determine_target_file_path(content_type, file_path_in_handler_dir)

        if target_file is None:
            return "error"

        if not target_file.exists():
            return "missing"

        return self._compare_content_hashes(source_content, target_file)
