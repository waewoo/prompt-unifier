"""Kilo Code tool handler for deploying prompts and rules."""

import logging
import re
from pathlib import Path
from typing import Any

import yaml

from prompt_unifier.constants import KILO_CODE_DIR
from prompt_unifier.handlers.base_handler import BaseToolHandler, VerificationResult
from prompt_unifier.handlers.handler_utils import console
from prompt_unifier.models.prompt import PromptFrontmatter
from prompt_unifier.models.rule import RuleFrontmatter

logger = logging.getLogger(__name__)


class KiloCodeToolHandler(BaseToolHandler):
    """
    Tool handler for Kilo Code AI assistant.
    Deploys prompts and rules as pure Markdown files (no YAML frontmatter)
    to flat directory structure with directory-prefixed file naming.
    """

    def __init__(self, base_path: Path | None = None):
        """Initialize the Kilo Code handler.

        Args:
            base_path: Base path for deployment. Defaults to Path.cwd().
        """
        super().__init__()
        self.name = "kilocode"
        # Use Path.cwd() as default base_path for project-local installations
        self.base_path = base_path if base_path else Path.cwd()
        self.tool_dir_constant = KILO_CODE_DIR
        self.prompts_dir = self.base_path / KILO_CODE_DIR / "workflows"
        self.rules_dir = self.base_path / KILO_CODE_DIR / "rules"

        # Track deployment statuses for verification
        self._deployment_statuses: dict[str, str] = {}

        # Auto-create directories with informative output
        if not self.prompts_dir.exists():
            self.prompts_dir.mkdir(parents=True, exist_ok=True)
            console.print(f"[cyan]Created Kilo Code workflows directory: {self.prompts_dir}[/cyan]")
        if not self.rules_dir.exists():
            self.rules_dir.mkdir(parents=True, exist_ok=True)
            console.print(f"[cyan]Created Kilo Code rules directory: {self.rules_dir}[/cyan]")

    def _convert_to_pure_markdown(self, yaml_content: str) -> str:
        """
        Converts YAML frontmatter content to pure Markdown format.

        Extracts YAML frontmatter fields and converts them to Markdown:
        - name → H1 title (# Title)
        - description → intro paragraphs
        - optional metadata → formatted Markdown text line

        Args:
            yaml_content: Content with YAML frontmatter

        Returns:
            Pure Markdown content without YAML blocks
        """
        # Extract YAML and body sections
        yaml_block, body = self._extract_yaml_and_body(yaml_content)
        if yaml_block is None:
            return yaml_content

        # Parse frontmatter
        frontmatter = self._parse_yaml_frontmatter(yaml_block)
        if frontmatter is None:
            return yaml_content

        # Build markdown output
        return self._build_markdown_from_frontmatter(frontmatter, body)

    def _extract_yaml_and_body(self, yaml_content: str) -> tuple[str | None, str]:
        """Extract YAML frontmatter and body from content.

        Args:
            yaml_content: Content with YAML frontmatter delimiters.

        Returns:
            Tuple of (yaml_block, body). Returns (None, "") if no valid frontmatter.
        """
        parts = yaml_content.split("---", 2)
        if len(parts) < 3:
            return None, ""

        yaml_block = parts[1].strip()
        body_section = parts[2].strip()

        # Split body on >>> if present
        if ">>>" in body_section:
            body_parts = body_section.split(">>>", 1)
            body = body_parts[1].strip() if len(body_parts) > 1 else ""
        else:
            body = body_section

        return yaml_block, body

    def _parse_yaml_frontmatter(self, yaml_block: str) -> dict[str, Any] | None:
        """Parse YAML frontmatter block.

        Args:
            yaml_block: YAML content as string.

        Returns:
            Dictionary of frontmatter or None if parsing fails.
        """
        try:
            frontmatter = yaml.safe_load(yaml_block)
            return frontmatter if isinstance(frontmatter, dict) else None
        except yaml.YAMLError:
            return None

    def _build_markdown_from_frontmatter(self, frontmatter: dict[str, Any], body: str) -> str:
        """Build pure Markdown from frontmatter and body.

        Args:
            frontmatter: Dictionary of frontmatter fields.
            body: Body content.

        Returns:
            Pure Markdown string.
        """
        markdown_lines = []

        # Add title
        name = frontmatter.get("name", "")
        if name:
            markdown_lines.extend([f"# {name}", ""])

        # Add description
        description = frontmatter.get("description", "")
        if description:
            markdown_lines.extend([description, ""])

        # Add metadata line
        metadata_line = self._build_metadata_line(frontmatter)
        if metadata_line:
            markdown_lines.extend([metadata_line, ""])

        # Add body
        if body:
            markdown_lines.append(body)

        return "\n".join(markdown_lines)

    def _build_metadata_line(self, frontmatter: dict[str, Any]) -> str:
        """Build metadata line from frontmatter fields.

        Args:
            frontmatter: Dictionary of frontmatter fields.

        Returns:
            Formatted metadata line or empty string if no metadata.
        """
        metadata_parts = []
        metadata_fields = ["category", "tags", "version", "author", "language", "applies_to"]

        for field in metadata_fields:
            value = frontmatter.get(field)
            if not value:
                continue

            # Format field name
            if field == "applies_to":
                field_display = "AppliesTo"
            else:
                field_display = field.replace("_", " ").title().replace(" ", "")

            # Format value
            value_str = ", ".join(str(v) for v in value) if isinstance(value, list) else str(value)

            metadata_parts.append(f"**{field_display}:** {value_str}")

        return " | ".join(metadata_parts)

    def _generate_directory_prefix(self, relative_path: Path | None) -> str:
        """
        Generates directory prefix for file naming.

        Extracts the closest parent directory name from relative path
        and normalizes it to kebab-case for use as a prefix.

        Args:
            relative_path: Relative path from prompts/ or rules/ base directory

        Returns:
            Directory prefix with trailing hyphen (e.g., "commands-" or "misc-")
        """
        if not relative_path or str(relative_path) == ".":
            # Root file - use default prefix
            return "misc-"

        # Get the last part of the path (closest directory to file)
        parts = relative_path.parts
        if parts:
            directory_name = parts[-1]
            # Normalize to kebab-case
            normalized = re.sub(r"[^a-z0-9]+", "-", directory_name.lower())
            normalized = normalized.strip("-")
            return f"{normalized}-"

        return "misc-"

    def _apply_file_naming_pattern(self, prefix: str, filename: str) -> str:
        """
        Applies the [directory]-[filename].md naming pattern.

        Args:
            prefix: Directory prefix (e.g., "commands-")
            filename: Original filename

        Returns:
            Filename with pattern applied and .md extension
        """
        # Ensure filename has .md extension
        if not filename.endswith(".md"):
            filename = f"{filename}.md"

        # Apply prefix
        return f"{prefix}{filename}"

    def deploy(
        self,
        content: Any,
        content_type: str,
        body: str = "",
        source_filename: str | None = None,
        relative_path: Path | None = None,
    ) -> None:
        """
        Deploys a prompt or rule to the Kilo Code directories.

        Args:
            content: The content object (PromptFrontmatter or RuleFrontmatter).
            content_type: Type of content ("prompt" or "rule").
            body: The body content as a string.
            source_filename: Original filename to preserve. If None, uses content.title.
            relative_path: Relative path from prompts/ or rules/ directory to preserve
                          subdirectory structure. If None, deploys to root directory.
        """
        # Validate and get base directory
        base_dir = self._validate_content_and_get_base_dir(content, content_type)

        # Create YAML content and transform to Markdown
        frontmatter_dict = self._build_frontmatter_dict_from_content(content)
        yaml_content = self._create_yaml_content(frontmatter_dict, body)
        markdown_content = self._convert_to_pure_markdown(yaml_content)

        # Determine target file path
        final_filename = self._determine_target_filename(
            content.title, source_filename, relative_path
        )
        target_file_path = base_dir / final_filename

        # Determine deployment status before deploying
        deployment_status = self._determine_deployment_status(target_file_path, markdown_content)
        self._deployment_statuses[content.title] = deployment_status

        # Write file
        target_file_path.write_text(markdown_content, encoding="utf-8")
        logger.debug(f"Deployed {content.title} ({content_type}) to {target_file_path}")

    def _validate_content_and_get_base_dir(self, content: Any, content_type: str) -> Path:
        """Validate content type and return base directory.

        Args:
            content: The content object.
            content_type: Type of content ("prompt" or "rule").

        Returns:
            Base directory path.

        Raises:
            ValueError: If content type is invalid or content doesn't match type.
        """
        if content_type == "prompt":
            if not isinstance(content, PromptFrontmatter):
                raise ValueError("Content must be a PromptFrontmatter instance for type 'prompt'")
            return self.prompts_dir

        if content_type == "rule":
            if not isinstance(content, RuleFrontmatter):
                raise ValueError("Content must be a RuleFrontmatter instance for type 'rule'")
            return self.rules_dir

        raise ValueError(f"Unsupported content type: {content_type}")

    def _build_frontmatter_dict_from_content(self, content: Any) -> dict[str, Any]:
        """Build frontmatter dictionary from content object.

        Args:
            content: The content object with frontmatter fields.

        Returns:
            Dictionary of frontmatter fields.
        """
        frontmatter_dict = {
            "name": content.title,
            "description": content.description,
        }

        # Add optional fields
        optional_fields = ["category", "version", "tags", "author", "language", "applies_to"]
        for field in optional_fields:
            if hasattr(content, field):
                value = getattr(content, field)
                if value:
                    frontmatter_dict[field] = value

        return frontmatter_dict

    def _create_yaml_content(self, frontmatter_dict: dict[str, Any], body: str) -> str:
        """Create YAML content from frontmatter and body.

        Args:
            frontmatter_dict: Dictionary of frontmatter fields.
            body: Body content.

        Returns:
            YAML content string with frontmatter delimiters.
        """
        yaml_str = yaml.safe_dump(frontmatter_dict, sort_keys=False)
        return f"---\n{yaml_str.rstrip()}\n---\n>>>\n{body}"

    def _determine_target_filename(
        self, content_name: str, source_filename: str | None, relative_path: Path | None
    ) -> str:
        """Determine the target filename with directory prefix.

        Args:
            content_name: The name/title of the content item.
            source_filename: Optional specific filename if different from title.
            relative_path: Relative subdirectory path.

        Returns:
            The filename to use for the target file with prefix applied.
        """
        if source_filename:
            filename = (
                source_filename if source_filename.endswith(".md") else f"{source_filename}.md"
            )
        else:
            filename = f"{content_name}.md"

        # Generate directory prefix and apply naming pattern
        prefix = self._generate_directory_prefix(relative_path)
        return self._apply_file_naming_pattern(prefix, filename)

    def calculate_deployed_filename(
        self, source_filename: str | None, content_name: str, relative_path: Path | None
    ) -> str:
        """Calculate the final deployed filename with directory prefix.

        This method is useful for external callers who need to know what the final
        filename will be after deployment (with directory prefix applied).

        Args:
            source_filename: Optional specific filename if different from title.
            content_name: The name/title of the content item.
            relative_path: Relative subdirectory path.

        Returns:
            The final filename that will be used for deployment (with prefix).
        """
        return self._determine_target_filename(content_name, source_filename, relative_path)

    def _determine_target_file_path(self, content_type: str, final_filename: str) -> Path | None:
        """Determine the target file path for deployment status check.

        Args:
            content_type: Type of content ("prompt" or "rule").
            final_filename: The final filename with prefix applied.

        Returns:
            The target file path, or None if content_type is invalid.
        """
        if content_type == "prompt":
            return self.prompts_dir / final_filename
        elif content_type == "rule":
            return self.rules_dir / final_filename
        return None

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
        # Determine target filename with directory prefix
        final_filename = self._determine_target_filename(
            content_name, source_filename, relative_path
        )
        target_file = self._determine_target_file_path(content_type, final_filename)

        if target_file is None:
            return "error"

        if not target_file.exists():
            return "missing"

        return self._compare_content_hashes(source_content, target_file)

    def verify_deployment_with_details(
        self,
        content_name: str,
        content_type: str,
        file_name: str,
        _relative_path: Path | None = None,
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
        logger.debug(f"Verifying deployment: '{content_name}' ({content_type}) at '{file_name}'")

        # Determine target file path
        target_file_path = self._determine_target_file_path(content_type, file_name)

        if target_file_path is None:
            return VerificationResult(
                file_name=content_name,
                content_type=content_type,
                status="failed",
                details=f"Unsupported content type: {content_type}",
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

        # Validate pure Markdown format
        if deployed_content.startswith("---"):
            return VerificationResult(
                file_name=content_name,
                content_type=content_type,
                status="failed",
                details="File contains YAML frontmatter delimiters (should be pure Markdown)",
            )

        if not deployed_content.startswith("# "):
            return VerificationResult(
                file_name=content_name,
                content_type=content_type,
                status="failed",
                details="File does not start with H1 title (# Title)",
            )

        # Retrieve deployment status from tracking dictionary
        deployment_status = self._deployment_statuses.get(content_name, "unknown")

        return VerificationResult(
            file_name=content_name,
            content_type=content_type,
            status="passed",
            details="File verified successfully",
            deployment_status=deployment_status,
            actual_file_path=str(target_file_path),
        )
