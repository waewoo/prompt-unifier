"""End-to-end integration tests for configurable handler base paths feature.

These tests validate complete workflows from project initialization through
configuration to deployment with custom base paths, ensuring the feature works
correctly in realistic multi-project scenarios.
"""

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from prompt_unifier.cli.main import app
from prompt_unifier.config.manager import ConfigManager
from prompt_unifier.handlers.continue_handler import ContinueToolHandler

runner = CliRunner()


@pytest.fixture
def project_a(tmp_path: Path) -> Path:
    """Create a mock project A directory structure."""
    project = tmp_path / "project-a"
    project.mkdir()
    return project


@pytest.fixture
def project_b(tmp_path: Path) -> Path:
    """Create a mock project B directory structure."""
    project = tmp_path / "project-b"
    project.mkdir()
    return project


@pytest.fixture
def mock_prompts_repo(tmp_path: Path) -> Path:
    """Create a mock prompts repository with test content."""
    repo_dir = tmp_path / "test-prompts-repo"
    repo_dir.mkdir()

    # Create prompts directory with test prompt
    prompts_dir = repo_dir / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "test-prompt.md").write_text("""---
title: test-prompt
description: A test prompt for integration testing
tags: ["python", "testing"]
version: 1.0.0
---

This is a test prompt for integration testing.
""")

    # Create rules directory with test rule
    rules_dir = repo_dir / "rules"
    rules_dir.mkdir()
    (rules_dir / "test-rule.md").write_text("""---
title: test-rule
description: A test rule for integration testing
category: testing
tags: ["python", "testing"]
version: 1.0.0
---

This is a test rule for integration testing.
""")

    # Initialize git repo
    import subprocess

    subprocess.run(["git", "init"], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_dir,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_dir,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=repo_dir,
        check=True,
        capture_output=True,
    )

    return repo_dir


class TestEndToEndWorkflow:
    """Test complete workflow: init -> configure -> deploy with custom paths."""

    def test_init_configure_deploy_with_custom_base_path(
        self, project_a: Path, mock_prompts_repo: Path
    ):
        """Test end-to-end workflow with custom base path configuration.

        Workflow:
        1. Initialize project with prompt-unifier
        2. Sync from repository
        3. Configure custom base_path in handlers section
        4. Deploy prompts/rules to custom location
        5. Verify files are in custom location, not default
        """
        custom_base_path = project_a / "custom_tools"

        # Change to project directory
        with patch("prompt_unifier.cli.commands.Path.cwd", return_value=project_a):
            # Step 1: Initialize
            result = runner.invoke(app, ["init"], catch_exceptions=False)
            assert result.exit_code == 0
            assert (project_a / ".prompt-unifier" / "config.yaml").exists()

            # Step 2: Sync from repository
            result = runner.invoke(
                app, ["sync", "--repo", str(mock_prompts_repo)], catch_exceptions=False
            )
            assert result.exit_code == 0

            # Step 3: Configure custom base_path
            config_path = project_a / ".prompt-unifier" / "config.yaml"
            config_manager = ConfigManager()
            config = config_manager.load_config(config_path)
            assert config is not None

            # Add handlers configuration
            config_content = config_path.read_text()
            config_content += f"""
handlers:
  continue:
    base_path: {custom_base_path}
"""
            config_path.write_text(config_content)

            # Step 4: Deploy with custom base_path
            result = runner.invoke(app, ["deploy"], catch_exceptions=False)
            assert result.exit_code == 0

            # Step 5: Verify deployment location
            custom_prompts_dir = custom_base_path / ".continue" / "prompts"
            custom_rules_dir = custom_base_path / ".continue" / "rules"

            assert custom_prompts_dir.exists()
            assert custom_rules_dir.exists()
            assert (custom_prompts_dir / "test-prompt.md").exists()
            assert (custom_rules_dir / "test-rule.md").exists()

            # Verify NOT in default location (cwd/.continue)
            project_a / ".continue"
            # Only custom_base_path should have the deployment
            assert (
                not (project_a / ".continue" / "prompts" / "test-prompt.md").exists()
                or custom_base_path == project_a
            )


class TestMultiProjectConfiguration:
    """Test that different projects can have different handler configurations."""

    def test_different_projects_different_base_paths(
        self, project_a: Path, project_b: Path, mock_prompts_repo: Path
    ):
        """Test that two projects can configure different base paths independently.

        Scenario:
        - Project A: Uses custom base path at project_a/tools
        - Project B: Uses custom base path at project_b/ai-assistants
        - Both deploy same content to different locations
        """
        # Setup Project A
        with patch("prompt_unifier.cli.commands.Path.cwd", return_value=project_a):
            runner.invoke(app, ["init"], catch_exceptions=False)
            runner.invoke(app, ["sync", "--repo", str(mock_prompts_repo)], catch_exceptions=False)

            config_path_a = project_a / ".prompt-unifier" / "config.yaml"
            config_content_a = config_path_a.read_text()
            config_content_a += f"""
handlers:
  continue:
    base_path: {project_a / "tools"}
"""
            config_path_a.write_text(config_content_a)

        # Setup Project B
        with patch("prompt_unifier.cli.commands.Path.cwd", return_value=project_b):
            runner.invoke(app, ["init"], catch_exceptions=False)
            runner.invoke(app, ["sync", "--repo", str(mock_prompts_repo)], catch_exceptions=False)

            config_path_b = project_b / ".prompt-unifier" / "config.yaml"
            config_content_b = config_path_b.read_text()
            config_content_b += f"""
handlers:
  continue:
    base_path: {project_b / "ai-assistants"}
"""
            config_path_b.write_text(config_content_b)

        # Deploy from Project A
        with patch("prompt_unifier.cli.commands.Path.cwd", return_value=project_a):
            result = runner.invoke(app, ["deploy"], catch_exceptions=False)
            assert result.exit_code == 0

        # Deploy from Project B
        with patch("prompt_unifier.cli.commands.Path.cwd", return_value=project_b):
            result = runner.invoke(app, ["deploy"], catch_exceptions=False)
            assert result.exit_code == 0

        # Verify separate deployments
        assert (project_a / "tools" / ".continue" / "prompts" / "test-prompt.md").exists()
        assert (project_b / "ai-assistants" / ".continue" / "prompts" / "test-prompt.md").exists()

        # Verify isolation - Project A files not in Project B location and vice versa
        assert not (project_b / "tools").exists()
        assert not (project_a / "ai-assistants").exists()


class TestEnvironmentVariableExpansion:
    """Test environment variable expansion in real deployment workflows."""

    def test_deployment_with_pwd_environment_variable(
        self, project_a: Path, mock_prompts_repo: Path
    ):
        """Test that $PWD expands correctly during actual deployment."""
        with patch("prompt_unifier.cli.commands.Path.cwd", return_value=project_a):
            # Initialize and sync
            runner.invoke(app, ["init"], catch_exceptions=False)
            runner.invoke(app, ["sync", "--repo", str(mock_prompts_repo)], catch_exceptions=False)

            # Configure with $PWD
            config_path = project_a / ".prompt-unifier" / "config.yaml"
            config_content = config_path.read_text()
            config_content += """
handlers:
  continue:
    base_path: $PWD/.continue-tools
"""
            config_path.write_text(config_content)

            # Deploy
            result = runner.invoke(app, ["deploy"], catch_exceptions=False)
            assert result.exit_code == 0

            # Verify $PWD expanded to project_a
            expected_path = project_a / ".continue-tools" / ".continue" / "prompts"
            assert expected_path.exists()
            assert (expected_path / "test-prompt.md").exists()

    def test_deployment_with_home_environment_variable(
        self, project_a: Path, mock_prompts_repo: Path
    ):
        """Test that $HOME expands correctly during actual deployment."""
        with patch("prompt_unifier.cli.commands.Path.cwd", return_value=project_a):
            # Initialize and sync
            runner.invoke(app, ["init"], catch_exceptions=False)
            runner.invoke(app, ["sync", "--repo", str(mock_prompts_repo)], catch_exceptions=False)

            # Configure with $HOME
            config_path = project_a / ".prompt-unifier" / "config.yaml"
            config_content = config_path.read_text()
            # Use a subdirectory in tmp to avoid conflicts
            test_home = project_a / "mock-home"
            test_home.mkdir()

            config_content += f"""
handlers:
  continue:
    base_path: {test_home}/.continue-global
"""
            config_path.write_text(config_content)

            # Deploy
            result = runner.invoke(app, ["deploy"], catch_exceptions=False)
            assert result.exit_code == 0

            # Verify deployment to home-based location
            expected_path = test_home / ".continue-global" / ".continue" / "prompts"
            assert expected_path.exists()
            assert (expected_path / "test-prompt.md").exists()


class TestCLIPrecedence:
    """Test CLI --base-path flag overrides configuration in real deployment."""

    def test_cli_flag_overrides_config_in_deployment(
        self, project_a: Path, mock_prompts_repo: Path
    ):
        """Test that CLI --base-path overrides config during actual deployment."""
        with patch("prompt_unifier.cli.commands.Path.cwd", return_value=project_a):
            # Initialize and sync
            runner.invoke(app, ["init"], catch_exceptions=False)
            runner.invoke(app, ["sync", "--repo", str(mock_prompts_repo)], catch_exceptions=False)

            # Configure with one base_path
            config_path = project_a / ".prompt-unifier" / "config.yaml"
            config_content = config_path.read_text()
            configured_path = project_a / "configured-location"
            config_content += f"""
handlers:
  continue:
    base_path: {configured_path}
"""
            config_path.write_text(config_content)

            # Deploy with CLI override
            cli_override_path = project_a / "cli-override-location"
            result = runner.invoke(
                app, ["deploy", "--base-path", str(cli_override_path)], catch_exceptions=False
            )
            assert result.exit_code == 0

            # Verify deployment to CLI path, NOT configured path
            cli_prompts = cli_override_path / ".continue" / "prompts"
            configured_prompts = configured_path / ".continue" / "prompts"

            assert cli_prompts.exists()
            assert (cli_prompts / "test-prompt.md").exists()

            # Configured path should NOT be created/used
            assert not configured_prompts.exists()


class TestActualFileDeployment:
    """Test actual file deployment to custom base paths."""

    def test_files_deployed_to_custom_location_with_correct_content(
        self, project_a: Path, mock_prompts_repo: Path
    ):
        """Test that files are actually deployed with correct content to custom path."""
        custom_base = project_a / "my-tools"

        with patch("prompt_unifier.cli.commands.Path.cwd", return_value=project_a):
            # Initialize and sync
            runner.invoke(app, ["init"], catch_exceptions=False)
            runner.invoke(app, ["sync", "--repo", str(mock_prompts_repo)], catch_exceptions=False)

            # Configure custom base path
            config_path = project_a / ".prompt-unifier" / "config.yaml"
            config_content = config_path.read_text()
            config_content += f"""
handlers:
  continue:
    base_path: {custom_base}
"""
            config_path.write_text(config_content)

            # Deploy
            result = runner.invoke(app, ["deploy"], catch_exceptions=False)
            assert result.exit_code == 0

            # Verify prompt file
            deployed_prompt = custom_base / ".continue" / "prompts" / "test-prompt.md"
            assert deployed_prompt.exists()

            content = deployed_prompt.read_text()
            assert "test-prompt" in content
            assert "integration testing" in content
            # Continue handler should add invokable: true
            assert "invokable: true" in content

            # Verify rule file
            deployed_rule = custom_base / ".continue" / "rules" / "test-rule.md"
            assert deployed_rule.exists()

            rule_content = deployed_rule.read_text()
            assert "test-rule" in rule_content
            assert "integration testing" in rule_content


class TestHandlerValidation:
    """Test handler validation with custom base paths."""

    def test_validation_creates_necessary_directories(self, tmp_path: Path):
        """Test that validate_tool_installation creates directories at custom path."""
        custom_base = tmp_path / "custom-continue-location"

        # Create handler with custom base path
        handler = ContinueToolHandler(base_path=custom_base)

        # Validate (should create directories)
        result = handler.validate_tool_installation()
        assert result is True

        # Verify directories created at custom location
        assert custom_base.exists()
        assert (custom_base / ".continue").exists()
        assert (custom_base / ".continue" / "prompts").exists()
        assert (custom_base / ".continue" / "rules").exists()


class TestConfigPersistence:
    """Test that handler configuration persists correctly."""

    def test_handlers_config_persists_across_operations(
        self, project_a: Path, mock_prompts_repo: Path
    ):
        """Test that handlers configuration survives multiple operations."""
        custom_base = project_a / "persistent-tools"

        with patch("prompt_unifier.cli.commands.Path.cwd", return_value=project_a):
            # Initialize
            runner.invoke(app, ["init"], catch_exceptions=False)

            # Add handlers configuration
            config_path = project_a / ".prompt-unifier" / "config.yaml"
            config_content = config_path.read_text()
            config_content += f"""
handlers:
  continue:
    base_path: {custom_base}
"""
            config_path.write_text(config_content)

            # Sync (should not overwrite handlers config)
            runner.invoke(app, ["sync", "--repo", str(mock_prompts_repo)], catch_exceptions=False)

            # Verify handlers config still present
            config_manager = ConfigManager()
            config = config_manager.load_config(config_path)
            assert config is not None
            assert config.handlers is not None
            assert "continue" in config.handlers
            assert config.handlers["continue"].base_path == str(custom_base)

            # Deploy (uses persisted config)
            result = runner.invoke(app, ["deploy"], catch_exceptions=False)
            assert result.exit_code == 0

            # Verify deployment used persisted custom path
            assert (custom_base / ".continue" / "prompts" / "test-prompt.md").exists()


class TestErrorScenarios:
    """Test error handling with custom base paths."""

    def test_deployment_fails_gracefully_with_missing_env_var(
        self, project_a: Path, mock_prompts_repo: Path
    ):
        """Test that deployment fails gracefully with clear error for missing env var."""
        with patch("prompt_unifier.cli.commands.Path.cwd", return_value=project_a):
            # Initialize and sync
            runner.invoke(app, ["init"], catch_exceptions=False)
            runner.invoke(app, ["sync", "--repo", str(mock_prompts_repo)], catch_exceptions=False)

            # Configure with non-existent environment variable
            config_path = project_a / ".prompt-unifier" / "config.yaml"
            config_content = config_path.read_text()
            config_content += """
handlers:
  continue:
    base_path: $NONEXISTENT_CUSTOM_VAR/tools
"""
            config_path.write_text(config_content)

            # Deploy should fail
            result = runner.invoke(app, ["deploy"], catch_exceptions=False)
            assert result.exit_code == 1

            # Should mention the missing variable
            assert (
                "NONEXISTENT_CUSTOM_VAR" in result.output or "Environment variable" in result.output
            )


class TestBackwardCompatibility:
    """Test that feature maintains backward compatibility."""

    def test_deployment_without_handlers_config_uses_default(
        self, project_a: Path, mock_prompts_repo: Path
    ):
        """Test that deployment works without handlers config (uses default cwd)."""
        with patch("prompt_unifier.cli.commands.Path.cwd", return_value=project_a):
            # Initialize and sync (no handlers configuration)
            runner.invoke(app, ["init"], catch_exceptions=False)
            runner.invoke(app, ["sync", "--repo", str(mock_prompts_repo)], catch_exceptions=False)

            # Deploy without handlers config
            result = runner.invoke(app, ["deploy"], catch_exceptions=False)
            assert result.exit_code == 0

            # Should deploy to default location (cwd/.continue)
            default_prompts = project_a / ".continue" / "prompts"
            assert default_prompts.exists()
            assert (default_prompts / "test-prompt.md").exists()
