"""Tests for SkillContentValidator.

Tests follow TDD: written before the implementation.
"""

import pytest

from prompt_unifier.core.skill_validator import SkillContentValidator
from prompt_unifier.models.skill import SkillFrontmatter
from prompt_unifier.models.validation import ValidationSeverity, WarningCode


@pytest.fixture
def validator() -> SkillContentValidator:
    """Return a fresh SkillContentValidator instance."""
    return SkillContentValidator()


@pytest.fixture
def minimal_frontmatter() -> SkillFrontmatter:
    """SkillFrontmatter with no compatibility (execution conditions missing)."""
    return SkillFrontmatter(name="test-skill", description="A test skill for unit tests")


@pytest.fixture
def full_frontmatter() -> SkillFrontmatter:
    """SkillFrontmatter with all optional fields, including compatibility."""
    return SkillFrontmatter(
        name="test-skill",
        description="A test skill for unit tests",
        compatibility="Requires git and docker installed",
    )


GOOD_CONTENT = """\
## Overview

This skill helps you review Kubernetes manifests for best practices.

## Steps

1. Run `kubectl get pods` to list running pods
2. Check resource limits: verify each pod has CPU and memory limits set
3. Validate liveness and readiness probes are configured
4. Review RBAC permissions and ensure least-privilege is applied
5. Check for deprecated API versions using `kubectl convert`
6. Verify network policies restrict traffic appropriately
7. Document any findings and create remediation tickets

## Examples

Use this skill after deploying a new service to ensure compliance.
Always run in dry-run mode first to avoid accidental changes.
"""

SHORT_CONTENT = "This is a very short skill."

UNSTRUCTURED_CONTENT = (
    "This skill is about reviewing code. "
    "You should check for common issues. "
    "Make sure to run the linter. "
    "Verify that all tests pass. "
    "Check code style and formatting. "
    "Review naming conventions and ensure they match the project standards. "
    "Look for potential security vulnerabilities and report them. "
    "Check for proper error handling throughout the codebase. "
    "Ensure documentation is up to date and accurate for all public APIs. "
    "Validate configuration files for correctness and completeness."
)

NO_VERBS_CONTENT = """\
## Overview

A skill for code analysis.

## Information

The codebase has many files. The project is large.
There are multiple modules and packages.
Each module serves a distinct purpose in the architecture.
The system has several layers of abstraction.
Documentation is available for all public interfaces.
Configuration is stored in YAML files for portability.
The database schema uses normalized form for data integrity.
Logging is centralized to a single aggregation endpoint.
"""


class TestCheckCompatibility:
    """Tests for _check_compatibility check."""

    def test_warns_when_compatibility_missing(
        self, validator: SkillContentValidator, minimal_frontmatter: SkillFrontmatter
    ) -> None:
        """SKILL_NO_COMPATIBILITY warning when compatibility is None."""
        issues = validator.generate_issues(minimal_frontmatter, GOOD_CONTENT)
        codes = [i.code for i in issues]
        assert WarningCode.SKILL_NO_COMPATIBILITY.value in codes

    def test_no_warning_when_compatibility_set(
        self, validator: SkillContentValidator, full_frontmatter: SkillFrontmatter
    ) -> None:
        """No SKILL_NO_COMPATIBILITY warning when compatibility is provided."""
        issues = validator.generate_issues(full_frontmatter, GOOD_CONTENT)
        codes = [i.code for i in issues]
        assert WarningCode.SKILL_NO_COMPATIBILITY.value not in codes

    def test_compatibility_warning_is_warning_severity(
        self, validator: SkillContentValidator, minimal_frontmatter: SkillFrontmatter
    ) -> None:
        """SKILL_NO_COMPATIBILITY issue has WARNING severity."""
        issues = validator.generate_issues(minimal_frontmatter, GOOD_CONTENT)
        compat_issues = [i for i in issues if i.code == WarningCode.SKILL_NO_COMPATIBILITY.value]
        assert len(compat_issues) == 1
        assert compat_issues[0].severity == ValidationSeverity.WARNING


class TestCheckContentLength:
    """Tests for _check_content_length check."""

    def test_warns_when_content_too_short(
        self, validator: SkillContentValidator, full_frontmatter: SkillFrontmatter
    ) -> None:
        """SKILL_CONTENT_TOO_SHORT warning for content below MIN_WORDS."""
        issues = validator.generate_issues(full_frontmatter, SHORT_CONTENT)
        codes = [i.code for i in issues]
        assert WarningCode.SKILL_CONTENT_TOO_SHORT.value in codes

    def test_no_warning_for_sufficient_content(
        self, validator: SkillContentValidator, full_frontmatter: SkillFrontmatter
    ) -> None:
        """No SKILL_CONTENT_TOO_SHORT warning for content above MIN_WORDS."""
        issues = validator.generate_issues(full_frontmatter, GOOD_CONTENT)
        codes = [i.code for i in issues]
        assert WarningCode.SKILL_CONTENT_TOO_SHORT.value not in codes

    def test_content_too_short_message_includes_word_count(
        self, validator: SkillContentValidator, full_frontmatter: SkillFrontmatter
    ) -> None:
        """SKILL_CONTENT_TOO_SHORT message mentions the actual word count."""
        issues = validator.generate_issues(full_frontmatter, SHORT_CONTENT)
        short_issues = [i for i in issues if i.code == WarningCode.SKILL_CONTENT_TOO_SHORT.value]
        assert len(short_issues) == 1
        assert "words" in short_issues[0].message.lower()


class TestCheckActionable:
    """Tests for _check_actionable check."""

    def test_warns_when_no_action_verbs_and_no_steps(
        self, validator: SkillContentValidator, full_frontmatter: SkillFrontmatter
    ) -> None:
        """SKILL_NOT_ACTIONABLE warning when content has no action verbs and no numbered list."""
        issues = validator.generate_issues(full_frontmatter, NO_VERBS_CONTENT)
        codes = [i.code for i in issues]
        assert WarningCode.SKILL_NOT_ACTIONABLE.value in codes

    def test_no_warning_for_actionable_with_numbered_list(
        self, validator: SkillContentValidator, full_frontmatter: SkillFrontmatter
    ) -> None:
        """No SKILL_NOT_ACTIONABLE warning when numbered steps are present."""
        issues = validator.generate_issues(full_frontmatter, GOOD_CONTENT)
        codes = [i.code for i in issues]
        assert WarningCode.SKILL_NOT_ACTIONABLE.value not in codes

    def test_no_warning_for_actionable_with_imperative_verbs(
        self, validator: SkillContentValidator, full_frontmatter: SkillFrontmatter
    ) -> None:
        """No SKILL_NOT_ACTIONABLE warning when action verbs are sufficiently present."""
        content = (
            "## Steps\n\n"
            "Run the linter, then check the output. "
            "Create a report and verify the results. "
            "Build the project and deploy it to staging. "
            "Validate the configuration and update the docs.\n\n"
            "Ensure all tests pass before merging the code changes."
        )
        issues = validator.generate_issues(full_frontmatter, content)
        codes = [i.code for i in issues]
        assert WarningCode.SKILL_NOT_ACTIONABLE.value not in codes


class TestCheckStructure:
    """Tests for _check_structure check."""

    def test_warns_when_no_markdown_structure(
        self, validator: SkillContentValidator, full_frontmatter: SkillFrontmatter
    ) -> None:
        """SKILL_POORLY_STRUCTURED warning when content has no headers or lists."""
        issues = validator.generate_issues(full_frontmatter, UNSTRUCTURED_CONTENT)
        codes = [i.code for i in issues]
        assert WarningCode.SKILL_POORLY_STRUCTURED.value in codes

    def test_no_warning_with_headers(
        self, validator: SkillContentValidator, full_frontmatter: SkillFrontmatter
    ) -> None:
        """No SKILL_POORLY_STRUCTURED warning when markdown headers are present."""
        issues = validator.generate_issues(full_frontmatter, GOOD_CONTENT)
        codes = [i.code for i in issues]
        assert WarningCode.SKILL_POORLY_STRUCTURED.value not in codes

    def test_no_warning_with_bullet_list(
        self, validator: SkillContentValidator, full_frontmatter: SkillFrontmatter
    ) -> None:
        """No SKILL_POORLY_STRUCTURED warning when bullet list is present."""
        content = (
            "This skill helps you review code.\n\n"
            "- Run the linter and fix all errors\n"
            "- Check for security vulnerabilities\n"
            "- Verify test coverage is above 80 percent\n"
            "- Review dependencies for known CVEs\n"
        ) * 4
        issues = validator.generate_issues(full_frontmatter, content)
        codes = [i.code for i in issues]
        assert WarningCode.SKILL_POORLY_STRUCTURED.value not in codes


class TestGenerateIssuesIntegration:
    """Integration tests for generate_issues combining multiple checks."""

    def test_ideal_skill_produces_no_issues(
        self, validator: SkillContentValidator, full_frontmatter: SkillFrontmatter
    ) -> None:
        """A well-formed skill with all best practices produces no warnings."""
        issues = validator.generate_issues(full_frontmatter, GOOD_CONTENT)
        assert issues == []

    def test_multiple_warnings_for_poor_skill(
        self, validator: SkillContentValidator, minimal_frontmatter: SkillFrontmatter
    ) -> None:
        """A poor skill triggers multiple warnings at once."""
        issues = validator.generate_issues(minimal_frontmatter, SHORT_CONTENT)
        codes = [i.code for i in issues]
        assert WarningCode.SKILL_NO_COMPATIBILITY.value in codes
        assert WarningCode.SKILL_CONTENT_TOO_SHORT.value in codes
        assert len(issues) >= 2

    def test_all_issues_have_suggestion(
        self, validator: SkillContentValidator, minimal_frontmatter: SkillFrontmatter
    ) -> None:
        """Every generated issue has a non-empty suggestion."""
        issues = validator.generate_issues(minimal_frontmatter, SHORT_CONTENT)
        for issue in issues:
            assert issue.suggestion, f"Issue {issue.code} has empty suggestion"

    def test_all_issues_have_warning_severity(
        self, validator: SkillContentValidator, minimal_frontmatter: SkillFrontmatter
    ) -> None:
        """All skill validation issues are warnings (not errors)."""
        issues = validator.generate_issues(minimal_frontmatter, SHORT_CONTENT)
        for issue in issues:
            assert issue.severity == ValidationSeverity.WARNING
