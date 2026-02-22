"""Tests for SkillFrontmatter and SkillFile models."""

import pytest
from pydantic import ValidationError

from prompt_unifier.models.skill import SkillFile, SkillFrontmatter


class TestSkillFrontmatterValid:
    """Tests for valid SkillFrontmatter instances."""

    def test_minimal_valid_skill(self):
        skill = SkillFrontmatter(name="my-skill", description="A useful skill")
        assert skill.name == "my-skill"
        assert skill.description == "A useful skill"
        assert skill.mode is None
        assert skill.license is None
        assert skill.compatibility is None
        assert skill.metadata is None

    def test_full_skill_with_all_fields(self):
        skill = SkillFrontmatter(
            name="code-review",
            description="Performs automated code review",
            mode="code",
            license="MIT",
            compatibility="1.0",
            metadata={"version": "1.0.0", "author": "team"},
        )
        assert skill.name == "code-review"
        assert skill.mode == "code"
        assert skill.license == "MIT"
        assert skill.compatibility == "1.0"
        assert skill.metadata == {"version": "1.0.0", "author": "team"}

    def test_single_char_name(self):
        skill = SkillFrontmatter(name="a", description="Short name skill")
        assert skill.name == "a"

    def test_name_with_numbers(self):
        skill = SkillFrontmatter(name="skill-1-2", description="Skill with numbers")
        assert skill.name == "skill-1-2"

    def test_whitespace_stripped_from_strings(self):
        skill = SkillFrontmatter(name="my-skill", description="  A description  ")
        assert skill.description == "A description"

    def test_mode_valid_slug(self):
        skill = SkillFrontmatter(name="my-skill", description="desc", mode="architect")
        assert skill.mode == "architect"


class TestSkillFrontmatterNameValidation:
    """Tests for name field validation."""

    def test_name_too_long(self):
        long_name = "a" * 65
        with pytest.raises(ValidationError, match="name"):
            SkillFrontmatter(name=long_name, description="desc")

    def test_name_exactly_64_chars(self):
        name = "a" * 64
        skill = SkillFrontmatter(name=name, description="desc")
        assert len(skill.name) == 64

    def test_name_uppercase_rejected(self):
        with pytest.raises(ValidationError, match="name"):
            SkillFrontmatter(name="MySkill", description="desc")

    def test_name_with_spaces_rejected(self):
        with pytest.raises(ValidationError, match="name"):
            SkillFrontmatter(name="my skill", description="desc")

    def test_name_starting_with_hyphen_rejected(self):
        with pytest.raises(ValidationError, match="name"):
            SkillFrontmatter(name="-my-skill", description="desc")

    def test_name_ending_with_hyphen_rejected(self):
        with pytest.raises(ValidationError, match="name"):
            SkillFrontmatter(name="my-skill-", description="desc")

    def test_name_empty_rejected(self):
        with pytest.raises(ValidationError, match="name"):
            SkillFrontmatter(name="", description="desc")

    def test_name_with_underscores_rejected(self):
        with pytest.raises(ValidationError, match="name"):
            SkillFrontmatter(name="my_skill", description="desc")

    def test_name_with_dots_rejected(self):
        with pytest.raises(ValidationError, match="name"):
            SkillFrontmatter(name="my.skill", description="desc")


class TestSkillFrontmatterDescriptionValidation:
    """Tests for description field validation."""

    def test_description_too_long(self):
        long_desc = "a" * 1025
        with pytest.raises(ValidationError, match="description"):
            SkillFrontmatter(name="my-skill", description=long_desc)

    def test_description_exactly_1024_chars(self):
        desc = "a" * 1024
        skill = SkillFrontmatter(name="my-skill", description=desc)
        assert len(skill.description) == 1024

    def test_description_empty_rejected(self):
        with pytest.raises(ValidationError, match="description"):
            SkillFrontmatter(name="my-skill", description="")

    def test_description_whitespace_only_rejected(self):
        with pytest.raises(ValidationError, match="description"):
            SkillFrontmatter(name="my-skill", description="   ")


class TestSkillFrontmatterModeValidation:
    """Tests for mode field validation."""

    def test_mode_invalid_slug_with_uppercase(self):
        with pytest.raises(ValidationError, match="mode"):
            SkillFrontmatter(name="my-skill", description="desc", mode="Code")

    def test_mode_starting_with_hyphen_rejected(self):
        with pytest.raises(ValidationError, match="mode"):
            SkillFrontmatter(name="my-skill", description="desc", mode="-code")

    def test_mode_ending_with_hyphen_rejected(self):
        with pytest.raises(ValidationError, match="mode"):
            SkillFrontmatter(name="my-skill", description="desc", mode="code-")

    def test_mode_none_allowed(self):
        skill = SkillFrontmatter(name="my-skill", description="desc", mode=None)
        assert skill.mode is None


class TestSkillFrontmatterExtraFields:
    """Tests for extra field rejection."""

    def test_extra_fields_rejected(self):
        with pytest.raises(ValidationError):
            SkillFrontmatter(
                name="my-skill",
                description="desc",
                unknown_field="value",  # type: ignore[call-arg]
            )


class TestSkillFile:
    """Tests for SkillFile model."""

    def test_valid_skill_file(self):
        skill = SkillFile(
            name="my-skill",
            description="A useful skill",
            content="# My Skill\n\nDo this and that.",
        )
        assert skill.name == "my-skill"
        assert skill.content == "# My Skill\n\nDo this and that."

    def test_skill_file_with_all_fields(self):
        skill = SkillFile(
            name="code-review",
            description="Automated code review",
            mode="code",
            license="MIT",
            content="Review the code.",
        )
        assert skill.mode == "code"
        assert skill.content == "Review the code."

    def test_skill_file_empty_content_rejected(self):
        with pytest.raises(ValidationError, match="content"):
            SkillFile(name="my-skill", description="desc", content="")

    def test_skill_file_whitespace_content_rejected(self):
        with pytest.raises(ValidationError, match="content"):
            SkillFile(name="my-skill", description="desc", content="   ")
