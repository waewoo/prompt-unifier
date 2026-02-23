"""Content quality validator for skill files.

This module provides SkillContentValidator, which checks skill body content
for quality issues: missing execution conditions, insufficient length,
lack of actionable instructions, and poor markdown structure.
"""

import re

from prompt_unifier.core.scaff_validator import ACTION_VERBS
from prompt_unifier.models.skill import SkillFrontmatter
from prompt_unifier.models.validation import ValidationIssue, ValidationSeverity, WarningCode

# Minimum word count for meaningful skill content
MIN_WORDS: int = 50


class SkillContentValidator:
    """Content quality validator for skill files.

    Generates ValidationIssue warnings (no numerical score) for:
    - Missing compatibility / execution conditions
    - Content too short (< MIN_WORDS words)
    - Not actionable (lacks action verbs or step-by-step structure)
    - Poorly structured (no markdown headers or lists)
    """

    def generate_issues(self, frontmatter: SkillFrontmatter, content: str) -> list[ValidationIssue]:
        """Return list of warnings for skill quality issues.

        Args:
            frontmatter: Parsed skill frontmatter fields.
            content: Skill body text (after the --- separator).

        Returns:
            List of ValidationIssue warnings; empty list if no issues found.
        """
        issues: list[ValidationIssue] = []
        issues.extend(self._check_compatibility(frontmatter))
        issues.extend(self._check_content_length(content))
        issues.extend(self._check_actionable(content))
        issues.extend(self._check_structure(content))
        return issues

    def _check_compatibility(self, frontmatter: SkillFrontmatter) -> list[ValidationIssue]:
        """Warn if execution conditions (compatibility field) are not specified.

        Args:
            frontmatter: Parsed skill frontmatter fields.

        Returns:
            List with one warning if compatibility is None, else empty list.
        """
        if frontmatter.compatibility is None:
            return [
                ValidationIssue(
                    line=None,
                    severity=ValidationSeverity.WARNING,
                    code=WarningCode.SKILL_NO_COMPATIBILITY.value,
                    message="Skill does not specify execution conditions",
                    suggestion=(
                        "Add a 'compatibility' field describing environment requirements "
                        "(e.g., 'Requires git and docker')"
                    ),
                )
            ]
        return []

    def _check_content_length(self, content: str) -> list[ValidationIssue]:
        """Warn if skill body content is below the minimum word count.

        Args:
            content: Skill body text.

        Returns:
            List with one warning if word count < MIN_WORDS, else empty list.
        """
        word_count = len(content.split())
        if word_count < MIN_WORDS:
            return [
                ValidationIssue(
                    line=None,
                    severity=ValidationSeverity.WARNING,
                    code=WarningCode.SKILL_CONTENT_TOO_SHORT.value,
                    message=(
                        f"Skill content is too brief ({word_count} words, minimum {MIN_WORDS})"
                    ),
                    suggestion=("Add more detailed instructions, examples, or usage guidelines"),
                )
            ]
        return []

    def _check_actionable(self, content: str) -> list[ValidationIssue]:
        """Warn if skill content lacks actionable instructions.

        Considers content actionable when it contains at least one of:
        - A numbered/ordered list (step-by-step instructions)
        - Bullet list items that start with an action verb
        - Lines/sentences that start with an action verb (imperative sentences)

        This avoids false positives from action verbs buried inside nouns
        (e.g., "document" inside "documentation").

        Args:
            content: Skill body text.

        Returns:
            List with one warning if the content is not actionable, else empty list.
        """
        action_verb_set = set(ACTION_VERBS)

        # 1. Numbered list indicates step-by-step instructions
        if re.search(r"^\s*\d+\.", content, re.MULTILINE):
            return []

        # 2. Bullet list items starting with action verbs
        bullet_starters = re.findall(r"^\s*[-*+]\s*(?:[*_]{1,3})?(\w+)", content, re.MULTILINE)
        if any(w.lower() in action_verb_set for w in bullet_starters):
            return []

        # 3. Lines / sentences starting with an action verb (imperative sentences)
        line_starters = re.findall(r"^([A-Za-z]+)", content, re.MULTILINE)
        if any(w.lower() in action_verb_set for w in line_starters):
            return []

        return [
            ValidationIssue(
                line=None,
                severity=ValidationSeverity.WARNING,
                code=WarningCode.SKILL_NOT_ACTIONABLE.value,
                message="Skill lacks actionable instructions",
                suggestion=(
                    "Use imperative verbs (run, create, check, verify) and "
                    "step-by-step numbered lists"
                ),
            )
        ]

    def _check_structure(self, content: str) -> list[ValidationIssue]:
        """Warn if skill content has no markdown structure (headers or lists).

        Args:
            content: Skill body text.

        Returns:
            List with one warning if content has no headers or lists, else empty list.
        """
        has_header = bool(re.search(r"^#{1,6}\s+\S", content, re.MULTILINE))
        has_list = bool(re.search(r"^\s*(?:[-*+]|\d+\.)\s+\S", content, re.MULTILINE))

        if not has_header and not has_list:
            return [
                ValidationIssue(
                    line=None,
                    severity=ValidationSeverity.WARNING,
                    code=WarningCode.SKILL_POORLY_STRUCTURED.value,
                    message="Skill content lacks markdown structure",
                    suggestion=(
                        "Add headers (##) to separate sections and bullet/numbered lists for steps"
                    ),
                )
            ]
        return []
