"""Tests for KiloCodeToolHandler skill deployment."""

from pathlib import Path

import pytest

from prompt_unifier.handlers.kilo_code_handler import KiloCodeToolHandler
from prompt_unifier.models.skill import SkillFrontmatter


@pytest.fixture
def handler(tmp_path: Path) -> KiloCodeToolHandler:
    return KiloCodeToolHandler(base_path=tmp_path)


@pytest.fixture
def skill() -> SkillFrontmatter:
    return SkillFrontmatter(name="my-skill", description="A useful skill")


@pytest.fixture
def skill_with_mode() -> SkillFrontmatter:
    return SkillFrontmatter(name="code-skill", description="A code skill", mode="code")


class TestSkillTargetDir:
    def test_no_mode_returns_skills_dir(self, handler: KiloCodeToolHandler):
        target = handler._get_skill_target_dir(None)
        assert target == handler.base_path / ".kilocode" / "skills"

    def test_with_mode_returns_skills_mode_dir(self, handler: KiloCodeToolHandler):
        target = handler._get_skill_target_dir("code")
        assert target == handler.base_path / ".kilocode" / "skills-code"

    def test_architect_mode(self, handler: KiloCodeToolHandler):
        target = handler._get_skill_target_dir("architect")
        assert target == handler.base_path / ".kilocode" / "skills-architect"


class TestBuildSkillYamlContent:
    def test_minimal_skill_yaml(self, handler: KiloCodeToolHandler, skill: SkillFrontmatter):
        content = handler._build_skill_yaml_content(skill, "Body text")
        assert content.startswith("---\n")
        assert "name: my-skill" in content
        assert "description: A useful skill" in content
        assert "Body text" in content
        # mode not present when None
        assert "mode:" not in content

    def test_skill_with_mode_yaml(
        self, handler: KiloCodeToolHandler, skill_with_mode: SkillFrontmatter
    ):
        content = handler._build_skill_yaml_content(skill_with_mode, "Body")
        assert "mode: code" in content

    def test_skill_with_all_optional_fields(self, handler: KiloCodeToolHandler):
        skill = SkillFrontmatter(
            name="full-skill",
            description="Full skill",
            mode="code",
            license="MIT",
            compatibility=">=1.0",
            metadata={"author": "me"},
        )
        content = handler._build_skill_yaml_content(skill, "Body")
        assert "license: MIT" in content
        assert "compatibility: '>=1.0'" in content
        assert "author: me" in content


class TestDeploySkill:
    def test_deploy_creates_skill_file_no_mode(
        self, handler: KiloCodeToolHandler, skill: SkillFrontmatter
    ):
        handler.deploy(skill, "skill", "Skill body content")

        skill_file = handler.base_path / ".kilocode" / "skills" / "my-skill" / "SKILL.md"
        assert skill_file.exists()

    def test_deployed_content_preserves_frontmatter(
        self, handler: KiloCodeToolHandler, skill: SkillFrontmatter
    ):
        handler.deploy(skill, "skill", "The body")

        skill_file = handler.base_path / ".kilocode" / "skills" / "my-skill" / "SKILL.md"
        content = skill_file.read_text()
        assert content.startswith("---")
        assert "name: my-skill" in content

    def test_deploy_skill_with_mode_uses_mode_dir(
        self, handler: KiloCodeToolHandler, skill_with_mode: SkillFrontmatter
    ):
        handler.deploy(skill_with_mode, "skill", "Body")

        skill_file = handler.base_path / ".kilocode" / "skills-code" / "code-skill" / "SKILL.md"
        assert skill_file.exists()

    def test_deploy_skill_not_deployed_to_workflows(
        self, handler: KiloCodeToolHandler, skill: SkillFrontmatter
    ):
        handler.deploy(skill, "skill", "Body")
        # workflows dir should not contain skill files
        assert not any(handler.prompts_dir.rglob("*.md"))

    def test_deploy_invalid_content_type_raises(self, handler: KiloCodeToolHandler):
        with pytest.raises(ValueError, match="SkillFrontmatter"):
            # Pass a non-SkillFrontmatter object with content_type="skill"
            from prompt_unifier.models.prompt import PromptFrontmatter

            prompt = PromptFrontmatter(title="Not a skill", description="desc")
            handler.deploy(prompt, "skill", "Body")  # type: ignore[arg-type]


class TestVerifySkillDeployment:
    def test_verify_deployed_skill_passes(
        self, handler: KiloCodeToolHandler, skill: SkillFrontmatter
    ):
        handler.deploy(skill, "skill", "Body")
        # file_name for skills is "skills/my-skill/SKILL.md"
        result = handler.verify_deployment_with_details(
            "my-skill", "skill", "skills/my-skill/SKILL.md"
        )
        assert result.status == "passed"

    def test_verify_missing_skill_fails(self, handler: KiloCodeToolHandler):
        result = handler.verify_deployment_with_details(
            "ghost-skill", "skill", "skills/ghost-skill/SKILL.md"
        )
        assert result.status == "failed"
        assert "does not exist" in result.details

    def test_verify_skill_without_frontmatter_fails(self, handler: KiloCodeToolHandler):
        # Create a SKILL.md without frontmatter
        skill_dir = handler.base_path / ".kilocode" / "skills" / "bad-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Bad skill\nNo frontmatter")

        result = handler.verify_deployment_with_details(
            "bad-skill", "skill", "skills/bad-skill/SKILL.md"
        )
        assert result.status == "failed"
        assert "frontmatter" in result.details.lower()


class TestGetDeploymentStatusSkill:
    def test_skill_missing_returns_missing(self, handler: KiloCodeToolHandler):
        status = handler.get_deployment_status(
            "ghost", "skill", "body", content=SkillFrontmatter(name="ghost", description="d")
        )
        assert status == "missing"

    def test_skill_synced_after_deploy(self, handler: KiloCodeToolHandler, skill: SkillFrontmatter):
        body = "Skill body"
        handler.deploy(skill, "skill", body)
        expected_content = handler._build_skill_yaml_content(skill, body)
        status = handler.get_deployment_status("my-skill", "skill", expected_content, content=skill)
        assert status == "synced"

    def test_skill_outdated_after_content_change(
        self, handler: KiloCodeToolHandler, skill: SkillFrontmatter
    ):
        handler.deploy(skill, "skill", "old body")
        status = handler.get_deployment_status(
            "my-skill", "skill", "completely different content", content=skill
        )
        assert status == "outdated"

    def test_clean_orphaned_no_kilocode_dir(self, tmp_path: Path):
        """Test clean_orphaned_files when .kilocode dir doesn't exist."""
        import shutil

        handler = KiloCodeToolHandler(base_path=tmp_path)
        shutil.rmtree(tmp_path / ".kilocode")
        # Should not crash and return empty results for skills
        result = handler.clean_orphaned_files(set())
        # prompts/rules cleanup already ran, skills portion exits early
        assert isinstance(result, list)


class TestCleanOrphanedSkills:
    def test_clean_removes_orphaned_skill_dir(
        self, handler: KiloCodeToolHandler, skill: SkillFrontmatter
    ):
        # Deploy a skill then clean with empty set
        handler.deploy(skill, "skill", "Body")
        skill_dir = handler.base_path / ".kilocode" / "skills" / "my-skill"
        assert skill_dir.exists()

        removed = handler.clean_orphaned_files(set())
        assert not skill_dir.exists()
        names = [r.file_name for r in removed]
        assert "my-skill" in names

    def test_clean_keeps_deployed_skill(
        self, handler: KiloCodeToolHandler, skill: SkillFrontmatter
    ):
        handler.deploy(skill, "skill", "Body")
        skill_dir = handler.base_path / ".kilocode" / "skills" / "my-skill"

        # "skills/my-skill" is the identifier for this skill
        removed = handler.clean_orphaned_files({"skills/my-skill"})
        assert skill_dir.exists()
        assert not any(r.file_name == "my-skill" for r in removed)

    def test_clean_removes_skill_with_mode(
        self, handler: KiloCodeToolHandler, skill_with_mode: SkillFrontmatter
    ):
        handler.deploy(skill_with_mode, "skill", "Body")
        skill_dir = handler.base_path / ".kilocode" / "skills-code" / "code-skill"
        assert skill_dir.exists()

        removed = handler.clean_orphaned_files(set())
        assert not skill_dir.exists()
        names = [r.file_name for r in removed]
        assert "code-skill" in names
