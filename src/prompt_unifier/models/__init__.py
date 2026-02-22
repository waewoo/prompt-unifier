"""Pydantic data models for validation and type safety."""

from .functional_test import (
    FunctionalTestAssertion,
    FunctionalTestFile,
    FunctionalTestResult,
    FunctionalTestScenario,
)
from .prompt import PromptFrontmatter
from .rule import RuleFile, RuleFrontmatter
from .skill import SkillFile, SkillFrontmatter

# Union type for content files (prompts, rules, or skills)
ContentFile = PromptFrontmatter | RuleFile | SkillFrontmatter

__all__ = [
    "ContentFile",
    "FunctionalTestAssertion",
    "FunctionalTestFile",
    "FunctionalTestResult",
    "FunctionalTestScenario",
    "PromptFrontmatter",
    "RuleFile",
    "RuleFrontmatter",
    "SkillFile",
    "SkillFrontmatter",
]
