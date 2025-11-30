"""End-to-end integration tests for recursive file discovery deployment feature.

These tests validate the complete workflow of recursive file discovery, relative path
preservation, and deployment to handlers with subdirectory structure preservation.
Tests cover critical user workflows and integration points that are not covered by
unit tests in Task Groups 1 and 2.
"""

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from prompt_unifier.cli.main import app
from prompt_unifier.config.manager import ConfigManager

runner = CliRunner()


@pytest.fixture
def complex_storage_structure(tmp_path: Path) -> Path:
    """Create a complex storage structure with multiple nesting levels."""
    storage_dir = tmp_path / "storage"
    storage_dir.mkdir()

    # Prompts with complex subdirectory structure
    prompts_dir = storage_dir / "prompts"
    prompts_dir.mkdir()

    # Root level prompt
    (prompts_dir / "root-prompt.md").write_text(
        """---
title: root-prompt
description: Root level prompt
tags: ["general"]
version: 1.0.0
---

Root prompt content
"""
    )

    # Backend subdirectory
    backend_dir = prompts_dir / "backend"
    backend_dir.mkdir()
    (backend_dir / "backend-prompt.md").write_text(
        """---
title: backend-prompt
description: Backend prompt
tags: ["backend"]
version: 1.0.0
---

Backend prompt content
"""
    )

    # Nested API subdirectory (backend/api)
    api_dir = backend_dir / "api"
    api_dir.mkdir()
    (api_dir / "api-prompt.md").write_text(
        """---
title: api-prompt
description: API prompt
tags: ["api", "backend"]
version: 1.0.0
---

API prompt content
"""
    )

    # Deeply nested subdirectory (backend/api/v2/endpoints)
    v2_dir = api_dir / "v2"
    v2_dir.mkdir()
    endpoints_dir = v2_dir / "endpoints"
    endpoints_dir.mkdir()
    (endpoints_dir / "endpoint-prompt.md").write_text(
        """---
title: endpoint-prompt
description: Endpoint prompt
tags: ["api", "v2"]
version: 1.0.0
---

Endpoint prompt content
"""
    )

    # Frontend subdirectory (parallel to backend)
    frontend_dir = prompts_dir / "frontend"
    frontend_dir.mkdir()
    (frontend_dir / "frontend-prompt.md").write_text(
        """---
title: frontend-prompt
description: Frontend prompt
tags: ["frontend"]
version: 1.0.0
---

Frontend prompt content
"""
    )

    # Rules with subdirectory structure
    rules_dir = storage_dir / "rules"
    rules_dir.mkdir()

    # Root level rule
    (rules_dir / "root-rule.md").write_text(
        """---
title: root-rule
description: Root level rule
category: standards
tags: ["general"]
version: 1.0.0
---

Root rule content
"""
    )

    # Security subdirectory
    security_dir = rules_dir / "security"
    security_dir.mkdir()
    (security_dir / "security-rule.md").write_text(
        """---
title: security-rule
description: Security rule
category: security
tags: ["security"]
version: 1.0.0
---

Security rule content
"""
    )

    # Nested auth subdirectory (security/auth)
    auth_dir = security_dir / "auth"
    auth_dir.mkdir()
    (auth_dir / "auth-rule.md").write_text(
        """---
title: auth-rule
description: Authentication rule
category: security
tags: ["security", "auth"]
version: 1.0.0
---

Auth rule content
"""
    )

    return storage_dir


@pytest.fixture
def mock_prompts_repo_with_subdirs(tmp_path: Path) -> Path:
    """Create a mock Git repository with subdirectory structure."""
    repo_dir = tmp_path / "test-repo"
    repo_dir.mkdir()

    # Create prompts with subdirectories
    prompts_dir = repo_dir / "prompts"
    prompts_dir.mkdir()

    (prompts_dir / "main-prompt.md").write_text(
        """---
title: main-prompt
description: Main prompt
tags: ["test"]
version: 1.0.0
---

Main content
"""
    )

    backend_dir = prompts_dir / "backend"
    backend_dir.mkdir()
    (backend_dir / "backend-test.md").write_text(
        """---
title: backend-test
description: Backend test
tags: ["backend"]
version: 1.0.0
---

Backend content
"""
    )

    # Create rules with subdirectories
    rules_dir = repo_dir / "rules"
    rules_dir.mkdir()

    (rules_dir / "main-rule.md").write_text(
        """---
title: main-rule
description: Main rule
category: testing
tags: ["test"]
version: 1.0.0
---

Rule content
"""
    )

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


class TestEndToEndRecursiveDeployment:
    """Test complete end-to-end workflow with recursive discovery and subdirectory preservation."""

    def test_deploy_preserves_complex_subdirectory_structure(
        self, tmp_path: Path, complex_storage_structure: Path
    ):
        """Test that deployment preserves complex nested subdirectory structure.

        This is a critical integration test that validates:
        1. Recursive file discovery finds all files
        2. Relative paths are calculated correctly
        3. Handlers receive and use relative paths
        4. Subdirectory structure is reproduced in deployment
        """
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        with patch("prompt_unifier.cli.commands.Path.cwd", return_value=project_dir):
            # Initialize
            result = runner.invoke(app, ["init"], catch_exceptions=False)
            assert result.exit_code == 0

            # Update config to point to complex storage
            config_path = project_dir / ".prompt-unifier" / "config.yaml"
            config_manager = ConfigManager()
            config = config_manager.load_config(config_path)
            assert config is not None

            config.storage_path = str(complex_storage_structure)
            config_manager.save_config(config_path, config)

            # Deploy
            result = runner.invoke(app, ["deploy"], catch_exceptions=False)
            assert result.exit_code == 0

            # Verify deployment structure is preserved
            continue_dir = project_dir / ".continue"

            # Check root level files
            assert (continue_dir / "prompts" / "root-prompt.md").exists()
            assert (continue_dir / "rules" / "root-rule.md").exists()

            # Check first-level subdirectories
            assert (continue_dir / "prompts" / "backend" / "backend-prompt.md").exists()
            assert (continue_dir / "prompts" / "frontend" / "frontend-prompt.md").exists()
            assert (continue_dir / "rules" / "security" / "security-rule.md").exists()

            # Check nested subdirectories (2 levels deep)
            assert (continue_dir / "prompts" / "backend" / "api" / "api-prompt.md").exists()
            assert (continue_dir / "rules" / "security" / "auth" / "auth-rule.md").exists()

            # Check deeply nested subdirectories (4 levels deep)
            deep_path = (
                continue_dir
                / "prompts"
                / "backend"
                / "api"
                / "v2"
                / "endpoints"
                / "endpoint-prompt.md"
            )
            assert deep_path.exists()

    def test_init_sync_deploy_workflow_with_subdirectories(
        self, tmp_path: Path, mock_prompts_repo_with_subdirs: Path
    ):
        """Test complete workflow: init -> sync -> deploy with subdirectory preservation.

        This validates the entire user workflow from scratch, ensuring
        subdirectory structure is maintained through sync and deployment.
        """
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        with patch("prompt_unifier.cli.commands.Path.cwd", return_value=project_dir):
            # Step 1: Initialize
            result = runner.invoke(app, ["init"], catch_exceptions=False)
            assert result.exit_code == 0

            # Step 2: Sync from repository with subdirectories
            result = runner.invoke(
                app, ["sync", "--repo", str(mock_prompts_repo_with_subdirs)], catch_exceptions=False
            )
            assert result.exit_code == 0

            # Step 3: Deploy
            result = runner.invoke(app, ["deploy"], catch_exceptions=False)
            assert result.exit_code == 0

            # Verify subdirectory structure is preserved
            continue_dir = project_dir / ".continue"
            assert (continue_dir / "prompts" / "main-prompt.md").exists()
            assert (continue_dir / "prompts" / "backend" / "backend-test.md").exists()
            assert (continue_dir / "rules" / "main-rule.md").exists()

            # Verify content is correct
            backend_file = continue_dir / "prompts" / "backend" / "backend-test.md"
            content = backend_file.read_text()
            assert "backend-test" in content
            assert "Backend content" in content

    def test_tag_filtering_with_subdirectory_deployment(
        self, tmp_path: Path, complex_storage_structure: Path
    ):
        """Test that tag filtering works correctly with subdirectory deployment.

        Critical test for ensuring tag filtering interacts correctly with
        recursive discovery and relative path preservation.
        """
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        with patch("prompt_unifier.cli.commands.Path.cwd", return_value=project_dir):
            # Initialize and configure
            runner.invoke(app, ["init"], catch_exceptions=False)
            config_path = project_dir / ".prompt-unifier" / "config.yaml"
            config_manager = ConfigManager()
            config = config_manager.load_config(config_path)
            config.storage_path = str(complex_storage_structure)
            config_manager.save_config(config_path, config)

            # Deploy only files tagged with "api"
            result = runner.invoke(app, ["deploy", "--tags", "api"], catch_exceptions=False)
            assert result.exit_code == 0

            continue_dir = project_dir / ".continue"

            # Should deploy api-tagged files in their subdirectories
            assert (continue_dir / "prompts" / "backend" / "api" / "api-prompt.md").exists()
            endpoint_path = (
                continue_dir
                / "prompts"
                / "backend"
                / "api"
                / "v2"
                / "endpoints"
                / "endpoint-prompt.md"
            )
            assert endpoint_path.exists()

            # Should NOT deploy non-api tagged files
            assert not (continue_dir / "prompts" / "root-prompt.md").exists()
            assert not (continue_dir / "prompts" / "backend" / "backend-prompt.md").exists()
            assert not (continue_dir / "prompts" / "frontend" / "frontend-prompt.md").exists()

    def test_custom_base_path_with_subdirectory_structure(
        self, tmp_path: Path, complex_storage_structure: Path
    ):
        """Test that custom base paths work with subdirectory structure preservation.

        Integration test for custom base paths + recursive deployment.
        """
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        custom_base = project_dir / "custom-tools"

        with patch("prompt_unifier.cli.commands.Path.cwd", return_value=project_dir):
            # Initialize and configure
            runner.invoke(app, ["init"], catch_exceptions=False)
            config_path = project_dir / ".prompt-unifier" / "config.yaml"
            config_manager = ConfigManager()
            config = config_manager.load_config(config_path)
            config.storage_path = str(complex_storage_structure)
            config_manager.save_config(config_path, config)

            # Add custom base_path configuration
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

            # Verify deployment to custom base path with subdirectory structure
            continue_dir = custom_base / ".continue"
            assert (continue_dir / "prompts" / "backend" / "api" / "api-prompt.md").exists()
            assert (continue_dir / "rules" / "security" / "auth" / "auth-rule.md").exists()

            # Verify NOT in default location
            assert not (project_dir / ".continue" / "prompts").exists()


class TestCleanOperationWithSubdirectories:
    """Test --clean flag interaction with subdirectory structure."""

    def test_clean_removes_orphaned_files_at_root_level(
        self, tmp_path: Path, complex_storage_structure: Path
    ):
        """Test that --clean flag correctly handles orphaned files at root level.

        Note: Currently clean only works at root level, not in subdirectories.
        This test validates the current behavior. Subdirectory clean support
        could be added in future enhancements.
        """
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        with patch("prompt_unifier.cli.commands.Path.cwd", return_value=project_dir):
            # Initialize and configure
            runner.invoke(app, ["init"], catch_exceptions=False)
            config_path = project_dir / ".prompt-unifier" / "config.yaml"
            config_manager = ConfigManager()
            config = config_manager.load_config(config_path)
            config.storage_path = str(complex_storage_structure)
            config_manager.save_config(config_path, config)

            # First deployment - deploys all files
            result = runner.invoke(app, ["deploy"], catch_exceptions=False)
            assert result.exit_code == 0

            continue_dir = project_dir / ".continue"

            # Manually create an orphaned file at root level
            orphaned_file = continue_dir / "prompts" / "orphaned.md"
            orphaned_file.write_text("This file should be removed")

            # Second deployment with --clean
            result = runner.invoke(app, ["deploy", "--clean"], catch_exceptions=False)
            assert result.exit_code == 0

            # Orphaned file at root should be removed
            assert not orphaned_file.exists()

            # Valid files should still exist
            assert (continue_dir / "prompts" / "root-prompt.md").exists()
            assert (continue_dir / "prompts" / "backend" / "backend-prompt.md").exists()

    def test_clean_with_tag_filter_preserves_non_filtered_files(
        self, tmp_path: Path, complex_storage_structure: Path
    ):
        """Test that --clean with tag filtering doesn't remove files outside filter scope.

        Edge case test for clean operation with filtering.
        """
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        with patch("prompt_unifier.cli.commands.Path.cwd", return_value=project_dir):
            # Initialize and configure
            runner.invoke(app, ["init"], catch_exceptions=False)
            config_path = project_dir / ".prompt-unifier" / "config.yaml"
            config_manager = ConfigManager()
            config = config_manager.load_config(config_path)
            config.storage_path = str(complex_storage_structure)
            config_manager.save_config(config_path, config)

            # First deployment - all files
            runner.invoke(app, ["deploy"], catch_exceptions=False)

            continue_dir = project_dir / ".continue"
            backend_file = continue_dir / "prompts" / "backend" / "backend-prompt.md"
            frontend_file = continue_dir / "prompts" / "frontend" / "frontend-prompt.md"

            assert backend_file.exists()
            assert frontend_file.exists()

            # Deploy with tag filter and clean
            # This should only clean within the filtered scope
            result = runner.invoke(
                app, ["deploy", "--tags", "backend", "--clean"], catch_exceptions=False
            )
            assert result.exit_code == 0

            # Backend files should still exist (they were redeployed)
            assert backend_file.exists()

            # Frontend files should still exist (outside filter scope, not cleaned)
            assert frontend_file.exists()


class TestEdgeCases:
    """Test edge cases and complex scenarios."""

    def test_empty_subdirectories_are_handled_correctly(self, tmp_path: Path):
        """Test that empty subdirectories don't cause issues."""
        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()

        prompts_dir = storage_dir / "prompts"
        prompts_dir.mkdir()

        # Create an empty subdirectory
        empty_dir = prompts_dir / "empty"
        empty_dir.mkdir()

        # Create a file in another subdirectory
        backend_dir = prompts_dir / "backend"
        backend_dir.mkdir()
        (backend_dir / "test.md").write_text(
            """---
title: test
description: Test
tags: ["test"]
version: 1.0.0
---

Content
"""
        )

        rules_dir = storage_dir / "rules"
        rules_dir.mkdir()

        project_dir = tmp_path / "project"
        project_dir.mkdir()

        with patch("prompt_unifier.cli.commands.Path.cwd", return_value=project_dir):
            runner.invoke(app, ["init"], catch_exceptions=False)
            config_path = project_dir / ".prompt-unifier" / "config.yaml"
            config_manager = ConfigManager()
            config = config_manager.load_config(config_path)
            config.storage_path = str(storage_dir)
            config_manager.save_config(config_path, config)

            # Deploy should succeed despite empty subdirectory
            result = runner.invoke(app, ["deploy"], catch_exceptions=False)
            assert result.exit_code == 0

            # Only the backend file should be deployed
            continue_dir = project_dir / ".continue"
            assert (continue_dir / "prompts" / "backend" / "test.md").exists()

    def test_multiple_deployments_update_subdirectory_files(
        self, tmp_path: Path, complex_storage_structure: Path
    ):
        """Test that multiple deployments correctly update files in subdirectories.

        Validates that backup and update logic works with nested structures.
        """
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        with patch("prompt_unifier.cli.commands.Path.cwd", return_value=project_dir):
            # Initialize and configure
            runner.invoke(app, ["init"], catch_exceptions=False)
            config_path = project_dir / ".prompt-unifier" / "config.yaml"
            config_manager = ConfigManager()
            config = config_manager.load_config(config_path)
            config.storage_path = str(complex_storage_structure)
            config_manager.save_config(config_path, config)

            # First deployment
            result = runner.invoke(app, ["deploy"], catch_exceptions=False)
            assert result.exit_code == 0

            continue_dir = project_dir / ".continue"
            api_file = continue_dir / "prompts" / "backend" / "api" / "api-prompt.md"
            assert api_file.exists()

            original_content = api_file.read_text()

            # Modify source file
            source_file = (
                complex_storage_structure / "prompts" / "backend" / "api" / "api-prompt.md"
            )
            source_file.write_text(
                """---
title: api-prompt
description: Updated API prompt
tags: ["api", "backend"]
version: 2.0.0
---

Updated API prompt content
"""
            )

            # Second deployment
            result = runner.invoke(app, ["deploy"], catch_exceptions=False)
            assert result.exit_code == 0

            # File should be updated
            updated_content = api_file.read_text()
            assert updated_content != original_content
            assert "Updated API prompt content" in updated_content

            # Backup should exist
            backup_file = api_file.with_suffix(".md.bak")
            assert backup_file.exists()
            assert original_content in backup_file.read_text()

    def test_deeply_nested_paths_with_special_characters(self, tmp_path: Path):
        """Test that subdirectory names with hyphens, underscores work correctly."""
        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()

        prompts_dir = storage_dir / "prompts"
        prompts_dir.mkdir()

        # Create path with special characters (hyphens, underscores, numbers)
        special_dir = prompts_dir / "my-backend_v2" / "api-endpoints_2024"
        special_dir.mkdir(parents=True)
        (special_dir / "special-test.md").write_text(
            """---
title: special-test
description: Test with special chars
tags: ["test"]
version: 1.0.0
---

Content
"""
        )

        rules_dir = storage_dir / "rules"
        rules_dir.mkdir()

        project_dir = tmp_path / "project"
        project_dir.mkdir()

        with patch("prompt_unifier.cli.commands.Path.cwd", return_value=project_dir):
            runner.invoke(app, ["init"], catch_exceptions=False)
            config_path = project_dir / ".prompt-unifier" / "config.yaml"
            config_manager = ConfigManager()
            config = config_manager.load_config(config_path)
            config.storage_path = str(storage_dir)
            config_manager.save_config(config_path, config)

            # Deploy
            result = runner.invoke(app, ["deploy"], catch_exceptions=False)
            assert result.exit_code == 0

            # Verify path structure is preserved
            continue_dir = project_dir / ".continue"
            expected_file = (
                continue_dir
                / "prompts"
                / "my-backend_v2"
                / "api-endpoints_2024"
                / "special-test.md"
            )
            assert expected_file.exists()


class TestDuplicateTitleDetectionWithSubdirectories:
    """Test duplicate title detection across subdirectories."""

    def test_duplicate_titles_in_different_subdirectories_fails(self, tmp_path: Path):
        """Test that duplicate titles in different subdirectories are detected.

        Critical validation that duplicate detection works with recursive discovery.
        """
        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()

        prompts_dir = storage_dir / "prompts"
        prompts_dir.mkdir()

        # Same title in root
        (prompts_dir / "duplicate.md").write_text(
            """---
title: shared-title
description: Root duplicate
tags: ["test"]
version: 1.0.0
---

Root content
"""
        )

        # Same title in subdirectory
        backend_dir = prompts_dir / "backend"
        backend_dir.mkdir()
        (backend_dir / "duplicate.md").write_text(
            """---
title: shared-title
description: Backend duplicate
tags: ["backend"]
version: 1.0.0
---

Backend content
"""
        )

        rules_dir = storage_dir / "rules"
        rules_dir.mkdir()

        project_dir = tmp_path / "project"
        project_dir.mkdir()

        with patch("prompt_unifier.cli.commands.Path.cwd", return_value=project_dir):
            runner.invoke(app, ["init"], catch_exceptions=False)
            config_path = project_dir / ".prompt-unifier" / "config.yaml"
            config_manager = ConfigManager()
            config = config_manager.load_config(config_path)
            config.storage_path = str(storage_dir)
            config_manager.save_config(config_path, config)

            # Deploy should fail with duplicate error
            result = runner.invoke(app, ["deploy"], catch_exceptions=False)
            assert result.exit_code == 1
            assert "duplicate" in result.output.lower() or "conflict" in result.output.lower()
            assert "shared-title" in result.output
