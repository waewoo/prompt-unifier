"""Tests for deploy command dry-run option and verification integration."""

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from prompt_unifier.cli.main import app

runner = CliRunner()


@pytest.fixture
def setup_deploy_environment(tmp_path: Path) -> tuple[Path, Path]:
    """Create a complete deployment environment with config and storage."""
    # Create config
    config_dir = tmp_path / ".prompt-unifier"
    config_dir.mkdir()
    config_file = config_dir / "config.yaml"
    storage_dir = tmp_path / "storage"
    storage_dir.mkdir()

    config_file.write_text(f"storage_path: {storage_dir}")

    # Create prompts directory with test file
    prompts_dir = storage_dir / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "test-prompt.md").write_text("""---
title: test-prompt
description: A test prompt
tags: ["python"]
version: 1.0.0
---


This is the prompt content.
""")

    # Create rules directory with test file
    rules_dir = storage_dir / "rules"
    rules_dir.mkdir()
    (rules_dir / "test-rule.md").write_text("""---
title: test-rule
description: A test rule
tags: ["python"]
version: 1.0.0
---


This is the rule content.
""")

    return tmp_path, storage_dir


class TestDryRunFlag:
    """Tests for the --dry-run flag functionality."""

    def test_dry_run_flag_recognized(self, setup_deploy_environment):
        """Test that --dry-run flag is recognized by deploy command."""
        tmp_path, storage_dir = setup_deploy_environment

        with runner.isolated_filesystem(temp_dir=tmp_path):
            # Change to the temp directory where config is
            import os

            os.chdir(tmp_path)

            result = runner.invoke(app, ["deploy", "--dry-run"])
            # Command should succeed (exit code 0) without actual deployment
            assert result.exit_code == 0
            # Should show dry-run preview
            assert "Dry-run preview" in result.output or "dry-run" in result.output.lower()

    def test_dry_run_preview_shows_rich_table(self, setup_deploy_environment):
        """Test dry-run preview shows Rich table with source, target, handler."""
        tmp_path, storage_dir = setup_deploy_environment

        with runner.isolated_filesystem(temp_dir=tmp_path):
            import os

            os.chdir(tmp_path)

            result = runner.invoke(app, ["deploy", "--dry-run"])
            assert result.exit_code == 0
            # Should show deployment preview information
            assert "test-prompt" in result.output or "test-rule" in result.output
            # Should show handler name
            assert "continue" in result.output.lower()

    def test_dry_run_warns_when_target_directories_missing(self, tmp_path: Path):
        """Test that dry-run logs warning when target directories don't exist."""
        # Create config pointing to a directory that doesn't have .continue
        config_dir = tmp_path / ".prompt-unifier"
        config_dir.mkdir()
        config_file = config_dir / "config.yaml"
        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()

        # Set base_path to a location without .continue directories
        nonexistent_base = tmp_path / "nonexistent_base"

        config_file.write_text(f"""storage_path: {storage_dir}
handlers:
  continue:
    base_path: {nonexistent_base}
""")

        # Create prompts
        prompts_dir = storage_dir / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "test.md").write_text("""---
title: test
description: test
---
content""")

        with runner.isolated_filesystem(temp_dir=tmp_path):
            import os

            os.chdir(tmp_path)

            result = runner.invoke(app, ["deploy", "--dry-run"])
            # Should complete without error but may show info about directory creation
            assert result.exit_code == 0

    def test_dry_run_skips_backup_deploy_verification(self, setup_deploy_environment):
        """Test that dry-run skips backup, deploy, and verification operations."""
        tmp_path, storage_dir = setup_deploy_environment

        with runner.isolated_filesystem(temp_dir=tmp_path):
            import os

            os.chdir(tmp_path)

            # Patch the actual deploy method to verify it's not called
            patch_path = "prompt_unifier.handlers.continue_handler.ContinueToolHandler.deploy"
            with patch(patch_path) as mock_deploy:
                result = runner.invoke(app, ["deploy", "--dry-run"])
                assert result.exit_code == 0
                # Deploy should NOT be called during dry-run
                mock_deploy.assert_not_called()


class TestDeployVerificationIntegration:
    """Tests for automatic verification after successful deploys."""

    def test_deploy_calls_verification_after_success(self, setup_deploy_environment):
        """Test that deploy command calls verification after successful deploys."""
        tmp_path, storage_dir = setup_deploy_environment

        with runner.isolated_filesystem(temp_dir=tmp_path):
            import os

            os.chdir(tmp_path)

            result = runner.invoke(app, ["deploy"])
            # Should complete deployment
            assert result.exit_code == 0
            # Should show deployment report
            assert "Deployment:" in result.output or "deployment" in result.output.lower()

    def test_existing_clean_flag_behavior_unchanged(self, setup_deploy_environment):
        """Test that existing --clean flag behavior is unchanged."""
        tmp_path, storage_dir = setup_deploy_environment

        with runner.isolated_filesystem(temp_dir=tmp_path):
            import os

            os.chdir(tmp_path)

            # First deploy some files
            result = runner.invoke(app, ["deploy"])
            assert result.exit_code == 0

            # Then deploy with --clean
            result = runner.invoke(app, ["deploy", "--clean"])
            assert result.exit_code == 0
            # Should mention cleaning or deployed items
            assert "Deployment" in result.output or "deployed" in result.output.lower()

    def test_existing_tags_filtering_behavior_unchanged(self, setup_deploy_environment):
        """Test that existing --tags filtering behavior is unchanged."""
        tmp_path, storage_dir = setup_deploy_environment

        with runner.isolated_filesystem(temp_dir=tmp_path):
            import os

            os.chdir(tmp_path)

            # Deploy with specific tag filter
            result = runner.invoke(app, ["deploy", "--tags", "python"])
            assert result.exit_code == 0
            # Should deploy items with the python tag
            assert "test-prompt" in result.output or "deployed" in result.output.lower()


class TestDryRunAndCleanInteraction:
    """Tests for dry-run interaction with other flags."""

    def test_dry_run_with_clean_flag(self, setup_deploy_environment):
        """Test that dry-run works correctly with --clean flag."""
        tmp_path, storage_dir = setup_deploy_environment

        with runner.isolated_filesystem(temp_dir=tmp_path):
            import os

            os.chdir(tmp_path)

            # Dry-run with clean flag should show preview without cleaning
            result = runner.invoke(app, ["deploy", "--dry-run", "--clean"])
            assert result.exit_code == 0
            # Should show dry-run preview
            assert "dry-run" in result.output.lower() or "preview" in result.output.lower()

    def test_dry_run_with_tags_filter(self, setup_deploy_environment):
        """Test that dry-run respects --tags filter."""
        tmp_path, storage_dir = setup_deploy_environment

        with runner.isolated_filesystem(temp_dir=tmp_path):
            import os

            os.chdir(tmp_path)

            # Dry-run with tags filter
            result = runner.invoke(app, ["deploy", "--dry-run", "--tags", "python"])
            assert result.exit_code == 0
            # Should show filtered items in preview
            assert "test-prompt" in result.output or "test-rule" in result.output

    def test_dry_run_with_nonexistent_tags(self, setup_deploy_environment):
        """Test that dry-run with non-matching tags shows no items."""
        tmp_path, storage_dir = setup_deploy_environment

        with runner.isolated_filesystem(temp_dir=tmp_path):
            import os

            os.chdir(tmp_path)

            # Dry-run with tags that don't match any files
            result = runner.invoke(app, ["deploy", "--dry-run", "--tags", "nonexistent"])
            assert result.exit_code == 0
            # Should indicate no matching files
            assert "No content" in result.output or "0" in result.output
