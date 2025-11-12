"""Pydantic data models for validation and type safety."""

from .prompt import PromptFrontmatter
from .rule import RuleFile, RuleFrontmatter

# Union type for content files (prompts or rules)
ContentFile = PromptFrontmatter | RuleFile

__all__ = [
    "PromptFrontmatter",
    "RuleFrontmatter",
    "RuleFile",
    "ContentFile",
]
