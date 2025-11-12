"""Unit tests for RuleFile and RuleFrontmatter Pydantic models."""

import warnings

import pytest
from pydantic import ValidationError

from prompt_manager.models.rule import VALID_CATEGORIES, RuleFile, RuleFrontmatter


class TestRuleFrontmatterValid:
    """Test valid RuleFrontmatter instances."""

    def test_valid_rule_with_all_fields(self):
        """Test valid rule with all required and optional fields."""
        rule = RuleFrontmatter(
            name="python-style-guide",
            description="Python coding standards and best practices",
            type="rule",
            category="coding-standards",
            tags=["python", "pep8", "style"],
            version="1.2.0",
            applies_to=["python", "django", "fastapi"],
            author="team-platform",
        )

        assert rule.name == "python-style-guide"
        assert rule.description == "Python coding standards and best practices"
        assert rule.type == "rule"
        assert rule.category == "coding-standards"
        assert rule.tags == ["python", "pep8", "style"]
        assert rule.version == "1.2.0"
        assert rule.applies_to == ["python", "django", "fastapi"]
        assert rule.author == "team-platform"

    def test_valid_rule_with_minimal_fields(self):
        """Test valid rule with only required fields."""
        rule = RuleFrontmatter(
            name="api-guide",
            description="REST API design guidelines",
            type="rule",
            category="architecture",
        )

        assert rule.name == "api-guide"
        assert rule.description == "REST API design guidelines"
        assert rule.type == "rule"
        assert rule.category == "architecture"
        assert rule.tags == []  # Default empty list
        assert rule.version == "1.0.0"  # Default version
        assert rule.applies_to == []  # Default empty list
        assert rule.author is None  # Default None

    def test_valid_categories(self):
        """Test all valid predefined categories."""
        for category in VALID_CATEGORIES:
            rule = RuleFrontmatter(
                name="test-rule",
                description="Test rule",
                type="rule",
                category=category,
            )
            assert rule.category == category


class TestRuleFrontmatterInvalidName:
    """Test invalid name formats."""

    def test_name_with_uppercase(self):
        """Test that name with uppercase letters is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RuleFrontmatter(
                name="Python-Style",
                description="Test",
                type="rule",
                category="coding-standards",
            )
        assert "must be in kebab-case" in str(exc_info.value)

    def test_name_with_spaces(self):
        """Test that name with spaces is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RuleFrontmatter(
                name="python style",
                description="Test",
                type="rule",
                category="coding-standards",
            )
        assert "must be in kebab-case" in str(exc_info.value)

    def test_name_with_underscores(self):
        """Test that name with underscores is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RuleFrontmatter(
                name="python_style",
                description="Test",
                type="rule",
                category="coding-standards",
            )
        assert "must be in kebab-case" in str(exc_info.value)

    def test_name_starting_with_number(self):
        """Test that name starting with number is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RuleFrontmatter(
                name="1-python-style",
                description="Test",
                type="rule",
                category="coding-standards",
            )
        assert "must be in kebab-case" in str(exc_info.value)

    def test_name_empty(self):
        """Test that empty name is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RuleFrontmatter(
                name="",
                description="Test",
                type="rule",
                category="coding-standards",
            )
        assert "must be a non-empty string" in str(exc_info.value)

    def test_name_whitespace_only(self):
        """Test that whitespace-only name is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RuleFrontmatter(
                name="   ",
                description="Test",
                type="rule",
                category="coding-standards",
            )
        assert "must be a non-empty string" in str(exc_info.value)


class TestRuleFrontmatterMissingFields:
    """Test missing required fields."""

    def test_missing_name(self):
        """Test that missing name is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RuleFrontmatter(
                description="Test",
                type="rule",
                category="coding-standards",
            )
        assert "name" in str(exc_info.value).lower()

    def test_missing_description(self):
        """Test that missing description is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RuleFrontmatter(
                name="test-rule",
                type="rule",
                category="coding-standards",
            )
        assert "description" in str(exc_info.value).lower()

    def test_missing_category(self):
        """Test that missing category is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RuleFrontmatter(
                name="test-rule",
                description="Test",
                type="rule",
            )
        assert "category" in str(exc_info.value).lower()


class TestRuleFrontmatterInvalidCategory:
    """Test category validation."""

    def test_custom_category_triggers_warning(self):
        """Test that custom category triggers warning but doesn't fail."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            rule = RuleFrontmatter(
                name="test-rule",
                description="Test",
                type="rule",
                category="custom-category",
            )

            assert rule.category == "custom-category"
            assert len(w) == 1
            assert "Non-standard category" in str(w[0].message)
            assert "custom-category" in str(w[0].message)

    def test_warning_message_includes_valid_categories(self):
        """Test that warning includes list of valid categories."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            RuleFrontmatter(
                name="test-rule",
                description="Test",
                type="rule",
                category="my-custom-cat",
            )

            assert len(w) == 1
            warning_msg = str(w[0].message)
            # Check that at least some standard categories are mentioned
            assert "coding-standards" in warning_msg
            assert "architecture" in warning_msg


class TestRuleFrontmatterInvalidTags:
    """Test tag validation."""

    def test_tags_with_uppercase(self):
        """Test that uppercase tags are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RuleFrontmatter(
                name="test-rule",
                description="Test",
                type="rule",
                category="coding-standards",
                tags=["Python", "PEP8"],
            )
        assert "must be lowercase" in str(exc_info.value)

    def test_tags_with_spaces(self):
        """Test that tags with spaces are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RuleFrontmatter(
                name="test-rule",
                description="Test",
                type="rule",
                category="coding-standards",
                tags=["python style", "pep 8"],
            )
        assert "must be lowercase without spaces" in str(exc_info.value)

    def test_too_many_tags(self):
        """Test that more than 10 tags are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RuleFrontmatter(
                name="test-rule",
                description="Test",
                type="rule",
                category="coding-standards",
                tags=[f"tag{i}" for i in range(11)],  # 11 tags
            )
        assert "max_length" in str(exc_info.value).lower() or "11" in str(exc_info.value)

    def test_valid_tags(self):
        """Test that valid lowercase tags are accepted."""
        rule = RuleFrontmatter(
            name="test-rule",
            description="Test",
            type="rule",
            category="coding-standards",
            tags=["python", "pep8", "style-guide"],
        )
        assert rule.tags == ["python", "pep8", "style-guide"]


class TestRuleFrontmatterInvalidVersion:
    """Test version validation."""

    def test_invalid_version_format(self):
        """Test that non-semver version is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RuleFrontmatter(
                name="test-rule",
                description="Test",
                type="rule",
                category="coding-standards",
                version="1.0",
            )
        assert "semantic versioning" in str(exc_info.value).lower()

    def test_version_with_text(self):
        """Test that version with text is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RuleFrontmatter(
                name="test-rule",
                description="Test",
                type="rule",
                category="coding-standards",
                version="v1.0.0",
            )
        assert "semantic versioning" in str(exc_info.value).lower()

    def test_valid_version_formats(self):
        """Test various valid semver formats."""
        valid_versions = ["0.0.1", "1.0.0", "2.5.3", "10.20.30"]

        for version in valid_versions:
            rule = RuleFrontmatter(
                name="test-rule",
                description="Test",
                type="rule",
                category="coding-standards",
                version=version,
            )
            assert rule.version == version


class TestRuleFrontmatterDescription:
    """Test description validation."""

    def test_description_too_long(self):
        """Test that description over 200 chars is rejected."""
        long_desc = "a" * 201

        with pytest.raises(ValidationError) as exc_info:
            RuleFrontmatter(
                name="test-rule",
                description=long_desc,
                type="rule",
                category="coding-standards",
            )
        assert "200" in str(exc_info.value)

    def test_description_max_length(self):
        """Test that description of exactly 200 chars is accepted."""
        desc = "a" * 200

        rule = RuleFrontmatter(
            name="test-rule",
            description=desc,
            type="rule",
            category="coding-standards",
        )
        assert len(rule.description) == 200


class TestRuleFileComplete:
    """Test complete RuleFile model with content."""

    def test_valid_rule_file_with_content(self):
        """Test valid RuleFile with all fields including content."""
        rule = RuleFile(
            name="python-style",
            description="Python coding standards",
            type="rule",
            category="coding-standards",
            tags=["python", "pep8"],
            version="1.0.0",
            content="# Python Style Guide\n\nUse PEP 8...",
        )

        assert rule.name == "python-style"
        assert rule.content == "# Python Style Guide\n\nUse PEP 8..."
        assert len(rule.content) > 0

    def test_rule_file_minimal(self):
        """Test RuleFile with minimal fields."""
        rule = RuleFile(
            name="test-rule",
            description="Test",
            type="rule",
            category="testing",
            content="Test content",
        )

        assert rule.content == "Test content"

    def test_rule_file_empty_content(self):
        """Test that empty content is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RuleFile(
                name="test-rule",
                description="Test",
                type="rule",
                category="testing",
                content="",
            )
        assert "content" in str(exc_info.value).lower()

    def test_rule_file_whitespace_only_content(self):
        """Test that whitespace-only content is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RuleFile(
                name="test-rule",
                description="Test",
                type="rule",
                category="testing",
                content="   \n  \n  ",
            )
        assert "content" in str(exc_info.value).lower()

    def test_rule_file_inherits_frontmatter_validation(self):
        """Test that RuleFile inherits all frontmatter validation."""
        # Invalid name should still be rejected
        with pytest.raises(ValidationError) as exc_info:
            RuleFile(
                name="Invalid_Name",
                description="Test",
                type="rule",
                category="testing",
                content="Test content",
            )
        assert "kebab-case" in str(exc_info.value)


class TestRuleFrontmatterExtraFields:
    """Test that extra fields are rejected."""

    def test_extra_field_rejected(self):
        """Test that extra field not in model is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RuleFrontmatter(
                name="test-rule",
                description="Test",
                type="rule",
                category="testing",
                unknown_field="should fail",  # type: ignore
            )
        assert "extra" in str(exc_info.value).lower() or "unexpected" in str(exc_info.value).lower()
