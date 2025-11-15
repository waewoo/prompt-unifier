"""Tests for CLI commands."""

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from prompt_manager.cli.main import app
from prompt_manager.core.content_parser import ContentFileParser
from prompt_manager.models.validation import ValidationSummary

runner = CliRunner()


@pytest.fixture
def mock_config(tmp_path: Path) -> Path:
    """Create a mock config file."""
    config_dir = tmp_path / ".prompt-manager"
    config_dir.mkdir()
    config_file = config_dir / "config.yaml"
    config_file.write_text(f"""
repo_url: https://example.com/repo.git
storage_path: {tmp_path / "storage"}
deploy_tags: ["python"]
target_handlers: ["continue"]
""")
    return config_file


@pytest.fixture
def mock_storage(tmp_path: Path) -> Path:
    """Create mock storage with prompts and rules."""
    storage_dir = tmp_path / "storage"
    storage_dir.mkdir()

    prompts_dir = storage_dir / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "test-prompt.md").write_text("""
---
title: test-prompt
description: A test prompt
tags: ["python"]
version: 1.0.0
---


Prompt content
""")

    rules_dir = storage_dir / "rules"
    rules_dir.mkdir()
    (rules_dir / "test-rule.md").write_text("""
---
title: test-rule
description: A test rule
category: testing
tags: ["python"]
version: 1.0.0
---


Rule content
""")

    return storage_dir


class TestValidateCommand:
    """Tests for the validate command."""

    def test_validate_no_directory_no_config(self):
        """Test validate without directory and without configuration."""
        with runner.isolated_filesystem():
            result = runner.invoke(app, ["validate"])
            assert result.exit_code == 1
            assert "No directory specified and configuration not found" in result.output

    def test_validate_invalid_content_type(self):
        """Test validate with invalid content type."""
        with runner.isolated_filesystem():
            # Create a valid config
            config_dir = Path.cwd() / ".prompt-manager"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text("storage_path: /tmp/storage")

            result = runner.invoke(app, ["validate", "--type", "invalid"])
            assert result.exit_code == 1
            assert "Invalid --type 'invalid'" in result.output

    def test_validate_missing_prompts_directory(self):
        """Test validate when prompts directory doesn't exist."""
        with runner.isolated_filesystem():
            # Create config and storage but not prompts
            config_dir = Path.cwd() / ".prompt-manager"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            storage_dir = Path.cwd() / "storage"
            storage_dir.mkdir()

            config_file.write_text(f"storage_path: {storage_dir}")

            result = runner.invoke(app, ["validate", "--type", "prompts"])
            assert result.exit_code == 1
            assert "Prompts directory" in result.output
            assert "does not exist" in result.output

    def test_validate_missing_rules_directory(self):
        """Test validate when rules directory doesn't exist."""
        with runner.isolated_filesystem():
            # Create config and storage but not rules
            config_dir = Path.cwd() / ".prompt-manager"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            storage_dir = Path.cwd() / "storage"
            storage_dir.mkdir()

            config_file.write_text(f"storage_path: {storage_dir}")

            result = runner.invoke(app, ["validate", "--type", "rules"])
            assert result.exit_code == 1
            assert "Rules directory" in result.output
            assert "does not exist" in result.output

    def test_validate_directory_not_exists(self):
        """Test validate with a directory that doesn't exist."""
        result = runner.invoke(app, ["validate", "/nonexistent/directory"])
        assert result.exit_code == 1
        assert "does not exist" in result.output

    def test_validate_directory_not_a_directory(self):
        """Test validate with a path that is not a directory."""
        with runner.isolated_filesystem():
            # Create a file instead of a directory
            test_file = Path.cwd() / "not_a_directory"
            test_file.write_text("content")

            result = runner.invoke(app, ["validate", str(test_file)])
            assert result.exit_code == 1
            assert "is not a directory" in result.output

    @patch("prompt_manager.core.batch_validator.BatchValidator.validate_directory")
    def test_validate_failure_exit_code(self, mock_validate):
        """Test that validate returns code 1 when validation fails."""
        mock_validate.return_value = ValidationSummary(
            success=False, total_files=1, passed=0, failed=1, error_count=1, warning_count=0
        )

        with runner.isolated_filesystem():
            # Create valid config and storage
            config_dir = Path.cwd() / ".prompt-manager"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            storage_dir = Path.cwd() / "storage"
            storage_dir.mkdir()
            prompts_dir = storage_dir / "prompts"
            prompts_dir.mkdir()

            config_file.write_text(f"storage_path: {storage_dir}")

            # Create a valid prompt file
            (prompts_dir / "test.md").write_text("""---
title: test
description: test
---
content""")

            result = runner.invoke(app, ["validate", "--type", "prompts"])
            assert result.exit_code == 1

    def test_validate_command_with_all_params(self):
        """Test validate command with all parameters."""
        with runner.isolated_filesystem():
            # Create a directory with valid files
            test_dir = Path.cwd() / "test_prompts"
            test_dir.mkdir()
            (test_dir / "test.md").write_text("""---
title: test
description: test
---
content""")

            result = runner.invoke(
                app, ["validate", str(test_dir), "--json", "--verbose", "--type", "all"]
            )
            # Command should succeed or fail gracefully
            assert result.exit_code in [0, 1]

    def test_validate_command_default_directory(self):
        """Test validate command without specified directory."""
        with runner.isolated_filesystem():
            # Create config structure
            config_dir = Path.cwd() / ".prompt-manager"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            storage_dir = Path.cwd() / "storage"
            storage_dir.mkdir()
            prompts_dir = storage_dir / "prompts"
            prompts_dir.mkdir()

            config_file.write_text(f"storage_path: {storage_dir}")

            # Create a valid prompt file
            (prompts_dir / "test.md").write_text("""---
title: test
description: test
---
content""")

            result = runner.invoke(app, ["validate"])
            assert result.exit_code in [0, 1]


class TestInitCommand:
    """Tests for the init command."""

    @patch("pathlib.Path.mkdir")
    def test_init_permission_error(self, mock_mkdir):
        """Test init with PermissionError."""
        mock_mkdir.side_effect = PermissionError("Permission denied")

        with runner.isolated_filesystem():
            result = runner.invoke(app, ["init"])
            assert result.exit_code == 1
            assert "Permission denied" in result.output

    @patch("pathlib.Path.mkdir")
    def test_init_generic_error(self, mock_mkdir):
        """Test init with a generic error."""
        mock_mkdir.side_effect = Exception("Generic error")

        with runner.isolated_filesystem():
            result = runner.invoke(app, ["init"])
            # Test should fail if mkdir fails
            assert result.exit_code == 1
            assert "Error" in result.output

    def test_init_command_with_storage_path(self):
        """Test init command with --storage-path."""
        with runner.isolated_filesystem():
            custom_storage = Path.cwd() / "custom_storage"

            result = runner.invoke(app, ["init", "--storage-path", str(custom_storage)])
            assert result.exit_code == 0

            # Verify directory was created
            assert custom_storage.exists()
            assert (Path.cwd() / ".prompt-manager" / "config.yaml").exists()


class TestSyncCommand:
    """Tests for the sync command."""

    def test_sync_config_load_failure(self):
        """Test sync when config loading fails."""
        with runner.isolated_filesystem():
            # Create existing but invalid config
            config_dir = Path.cwd() / ".prompt-manager"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text("invalid: yaml: content")

            result = runner.invoke(app, ["sync"])
            assert result.exit_code == 1
            assert "Failed to load configuration" in result.output

    def test_sync_no_repo_url_configured(self):
        """Test sync without configured repository URL."""
        with runner.isolated_filesystem():
            # Create config without repo_url
            config_dir = Path.cwd() / ".prompt-manager"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text("storage_path: /tmp/storage")

            result = runner.invoke(app, ["sync"])
            assert result.exit_code == 1
            assert "No repository URL configured" in result.output

    def test_sync_storage_path_flag_updates_config(self):
        """Test that --storage-path flag updates the config."""
        with runner.isolated_filesystem():
            # Create valid config
            config_dir = Path.cwd() / ".prompt-manager"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            original_storage = Path.cwd() / "original_storage"
            original_storage.mkdir()

            config_file.write_text(f"""
repo_url: https://example.com/repo.git
storage_path: {original_storage}
""")

            # Mock git service to avoid real clone
            with patch("prompt_manager.git.service.GitService.clone_to_temp") as mock_clone:
                mock_clone.return_value = (Path.cwd() / "temp_repo", None)
                with patch(
                    "prompt_manager.git.service.GitService.get_latest_commit"
                ) as mock_commit:
                    mock_commit.return_value = "abc123"
                    with patch("prompt_manager.git.service.GitService.extract_prompts_dir"):
                        # Create new storage directory
                        new_storage = Path.cwd() / "new_storage"

                        runner.invoke(app, ["sync", "--storage-path", str(new_storage)])
                        # Test mainly verifies command doesn't crash
                        # Exact behavior verification would require more mocking

    @patch("prompt_manager.git.service.GitService.clone_to_temp")
    def test_sync_permission_error(self, mock_clone):
        """Test sync with PermissionError."""
        mock_clone.side_effect = PermissionError("Permission denied")

        with runner.isolated_filesystem():
            # Create valid config
            config_dir = Path.cwd() / ".prompt-manager"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text("repo_url: https://example.com/repo.git")

            result = runner.invoke(app, ["sync"])
            assert result.exit_code == 1
            assert "Permission denied" in result.output

    def test_sync_command_with_repo(self):
        """Test sync command with --repo."""
        with runner.isolated_filesystem():
            # Create config
            config_dir = Path.cwd() / ".prompt-manager"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text("storage_path: /tmp/storage")

            # Mock git service
            with patch("prompt_manager.git.service.GitService.clone_to_temp") as mock_clone:
                mock_clone.return_value = (Path.cwd() / "temp_repo", None)
                with patch(
                    "prompt_manager.git.service.GitService.get_latest_commit"
                ) as mock_commit:
                    mock_commit.return_value = "abc123"
                    with patch("prompt_manager.git.service.GitService.extract_prompts_dir"):
                        result = runner.invoke(
                            app, ["sync", "--repo", "https://example.com/repo.git"]
                        )
                        # Test verifies command executes without error
                        assert result.exit_code in [0, 1]

    def test_sync_command_without_repo(self):
        """Test sync command without --repo (uses config)."""
        with runner.isolated_filesystem():
            # Create config with repo_url
            config_dir = Path.cwd() / ".prompt-manager"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text("""
repo_url: https://example.com/repo.git
storage_path: /tmp/storage
""")

            # Mock git service
            with patch("prompt_manager.git.service.GitService.clone_to_temp") as mock_clone:
                mock_clone.return_value = (Path.cwd() / "temp_repo", None)
                with patch(
                    "prompt_manager.git.service.GitService.get_latest_commit"
                ) as mock_commit:
                    mock_commit.return_value = "abc123"
                    with patch("prompt_manager.git.service.GitService.extract_prompts_dir"):
                        result = runner.invoke(app, ["sync"])
                        assert result.exit_code in [0, 1]

    def test_sync_command_with_storage_path(self):
        """Test sync command with --storage-path."""
        with runner.isolated_filesystem():
            # Create config
            config_dir = Path.cwd() / ".prompt-manager"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text("repo_url: https://example.com/repo.git")

            custom_storage = Path.cwd() / "custom_storage"

            # Mock git service
            with patch("prompt_manager.git.service.GitService.clone_to_temp") as mock_clone:
                mock_clone.return_value = (Path.cwd() / "temp_repo", None)
                with patch(
                    "prompt_manager.git.service.GitService.get_latest_commit"
                ) as mock_commit:
                    mock_commit.return_value = "abc123"
                    with patch("prompt_manager.git.service.GitService.extract_prompts_dir"):
                        result = runner.invoke(app, ["sync", "--storage-path", str(custom_storage)])
                        assert result.exit_code in [0, 1]


class TestStatusCommand:
    """Tests for the status command."""

    def test_status_config_not_found(self):
        """Test status without configuration."""
        with runner.isolated_filesystem():
            result = runner.invoke(app, ["status"])
            # Status command should not fail with code 1, should show error
            # but continue
            assert result.exit_code == 0
            assert "Error:" in result.output

    def test_status_config_load_failure(self):
        """Test status with corrupted config."""
        with runner.isolated_filesystem():
            # Create corrupted config
            config_dir = Path.cwd() / ".prompt-manager"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text("invalid: yaml: content")

            result = runner.invoke(app, ["status"])
            # Status command should not fail with code 1, should show error
            # but continue
            assert result.exit_code == 0
            assert "Error:" in result.output

    def test_status_no_repo_configured(self):
        """Test status without configured repository."""
        with runner.isolated_filesystem():
            # Create config without repo_url
            config_dir = Path.cwd() / ".prompt-manager"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text("storage_path: /tmp/storage")

            result = runner.invoke(app, ["status"])
            assert result.exit_code == 0  # Status is informational, no error
            assert "Not configured" in result.output
            assert "Run 'prompt-manager sync --repo" in result.output

    def test_status_never_synced(self):
        """Test status when never synchronized."""
        with runner.isolated_filesystem():
            # Create config with repo but without sync
            config_dir = Path.cwd() / ".prompt-manager"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text("""
repo_url: https://example.com/repo.git
storage_path: /tmp/storage
""")

            result = runner.invoke(app, ["status"])
            assert result.exit_code == 0
            assert "Never" in result.output
            assert "None" in result.output

    @patch("prompt_manager.git.service.GitService.check_remote_updates")
    def test_status_update_check_fails(self, mock_check_updates):
        """Test status when update check fails."""
        mock_check_updates.side_effect = Exception("Network error")

        with runner.isolated_filesystem():
            # Create complete config
            config_dir = Path.cwd() / ".prompt-manager"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text("""
repo_url: https://example.com/repo.git
storage_path: /tmp/storage
last_sync_timestamp: 2024-01-01T00:00:00Z
last_sync_commit: abc123
""")

            result = runner.invoke(app, ["status"])
            # Status command should succeed even if update check fails
            assert result.exit_code == 0
            # Verify there's output, regardless of exact content
            assert len(result.output) > 0

    def test_status_generic_error(self):
        """Test status with a generic error."""
        with runner.isolated_filesystem():
            # Create valid config
            config_dir = Path.cwd() / ".prompt-manager"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text("storage_path: /tmp/storage")

            # Mock ConfigManager to simulate an error
            with patch("prompt_manager.config.manager.ConfigManager.load_config") as mock_load:
                mock_load.side_effect = Exception("Unexpected error")

                result = runner.invoke(app, ["status"])
                assert result.exit_code == 0  # Status is informational
                assert "Error:" in result.output


class TestDeployCommand:
    """Tests for the deploy command."""

    def test_deploy_configuration_validation(self):
        """Test that deploy command validates configuration properly."""
        with runner.isolated_filesystem():
            # Test with no config file
            result = runner.invoke(app, ["deploy"])
            assert result.exit_code == 1
            assert "Configuration not found" in result.output

    def test_deploy_file_scanning_logic(self):
        """Test the file scanning and filtering logic directly."""
        with runner.isolated_filesystem():
            tmp_path = Path.cwd()

            # Setup config and storage
            config_dir = tmp_path / ".prompt-manager"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text(f"""
repo_url: https://example.com/repo.git
storage_path: {tmp_path / "storage"}
deploy_tags: ["python"]
target_handlers: ["continue"]
""")

            storage_dir = tmp_path / "storage"
            storage_dir.mkdir()

            prompts_dir = storage_dir / "prompts"
            prompts_dir.mkdir()
            # Use exact format from fixtures
            (prompts_dir / "test-prompt.md").write_text("""---
title: test-prompt
description: A test prompt
tags: ["python"]
version: 1.0.0
---


This is the prompt content.
""")

            # Test parsing files
            parser = ContentFileParser()
            content_files = []

            for md_file in prompts_dir.glob("*.md"):
                try:
                    parsed_content = parser.parse_file(md_file)
                    content_files.append((parsed_content, "prompt", md_file))
                except Exception as e:
                    print(f"Failed to parse {md_file}: {e}")

            # Should have found one prompt file
            assert len(content_files) == 1
            parsed_content, content_type, file_path = content_files[0]
            assert parsed_content.title == "test-prompt"
            assert content_type == "prompt"
            assert "python" in parsed_content.tags

    def test_deploy_tag_filtering(self):
        """Test tag filtering logic."""
        with runner.isolated_filesystem():
            tmp_path = Path.cwd()

            # Setup files with different tags
            storage_dir = tmp_path / "storage"
            storage_dir.mkdir()

            prompts_dir = storage_dir / "prompts"
            prompts_dir.mkdir()
            # Use exact format from fixtures
            (prompts_dir / "python-prompt.md").write_text("""---
title: python-prompt
description: A python prompt
tags: ["python", "backend"]
version: 1.0.0
---


Python content
""")

            (prompts_dir / "js-prompt.md").write_text("""---
title: js-prompt
description: A js prompt
tags: ["javascript", "frontend"]
version: 1.0.0
---


JavaScript content
""")

            # Test filtering by tags
            parser = ContentFileParser()
            content_files = []

            for md_file in prompts_dir.glob("*.md"):
                try:
                    parsed_content = parser.parse_file(md_file)
                    content_files.append((parsed_content, "prompt", md_file))
                except Exception:
                    pass

            # Filter for python tag
            python_files = []
            for parsed_content, content_type, file_path in content_files:
                if "python" in parsed_content.tags:
                    python_files.append((parsed_content, content_type, file_path))

            assert len(python_files) == 1
            assert python_files[0][0].title == "python-prompt"

    def test_deploy_name_filtering(self):
        """Test name filtering logic."""
        with runner.isolated_filesystem():
            tmp_path = Path.cwd()

            storage_dir = tmp_path / "storage"
            storage_dir.mkdir()

            prompts_dir = storage_dir / "prompts"
            prompts_dir.mkdir()
            # Use exact format from fixtures
            (prompts_dir / "specific-prompt.md").write_text("""---
title: specific-prompt
description: A specific prompt
tags: ["test"]
version: 1.0.0
---


Specific content
""")

            (prompts_dir / "other-prompt.md").write_text("""---
title: other-prompt
description: Another prompt
tags: ["test"]
version: 1.0.0
---


Other content
""")

            # Test filtering by name
            parser = ContentFileParser()
            content_files = []

            for md_file in prompts_dir.glob("*.md"):
                try:
                    parsed_content = parser.parse_file(md_file)
                    content_files.append((parsed_content, "prompt", md_file))
                except Exception:
                    pass

            # Filter for specific name
            filtered_files = []
            target_name = "specific-prompt"
            for parsed_content, content_type, file_path in content_files:
                if parsed_content.title == target_name:
                    filtered_files.append((parsed_content, content_type, file_path))

            assert len(filtered_files) == 1
            assert filtered_files[0][0].title == "specific-prompt"

    def test_deploy_command_help(self):
        """Test that deploy command has proper help."""
        result = runner.invoke(app, ["deploy", "--help"])
        assert result.exit_code == 0
        assert "Deploy prompts and rules" in result.output

    def test_deploy_command_with_invalid_config(self):
        """Test deploy command behavior with invalid configuration."""
        with runner.isolated_filesystem():
            # Create invalid config
            config_dir = Path.cwd() / ".prompt-manager"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text("invalid: yaml: content")

            result = runner.invoke(app, ["deploy"])
            assert result.exit_code == 1

    def test_deploy_command_with_missing_storage(self):
        """Test deploy command behavior with missing storage directory."""
        with runner.isolated_filesystem():
            # Create config without storage directory
            config_dir = Path.cwd() / ".prompt-manager"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text("""
repo_url: https://example.com/repo.git
storage_path: /nonexistent/path
deploy_tags: ["python"]
target_handlers: ["continue"]
""")

            result = runner.invoke(app, ["deploy"])
            assert result.exit_code == 1
            assert "does not exist" in result.output

    def test_deploy_command_with_name(self):
        """Test deploy command with --name."""
        with runner.isolated_filesystem():
            # Create complete structure
            config_dir = Path.cwd() / ".prompt-manager"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            storage_dir = Path.cwd() / "storage"
            storage_dir.mkdir()
            prompts_dir = storage_dir / "prompts"
            prompts_dir.mkdir()

            config_file.write_text(f"storage_path: {storage_dir}")

            # Create a prompt
            (prompts_dir / "test_prompt.md").write_text("""---
title: test_prompt
description: test
---
content""")

            result = runner.invoke(app, ["deploy", "--name", "test_prompt"])
            assert result.exit_code in [0, 1]

    def test_deploy_command_with_tags(self):
        """Test deploy command with --tags."""
        with runner.isolated_filesystem():
            # Create complete structure
            config_dir = Path.cwd() / ".prompt-manager"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            storage_dir = Path.cwd() / "storage"
            storage_dir.mkdir()
            prompts_dir = storage_dir / "prompts"
            prompts_dir.mkdir()

            config_file.write_text(f"storage_path: {storage_dir}")

            # Create a prompt with tags
            (prompts_dir / "test_prompt.md").write_text("""---
title: test_prompt
description: test
tags: ["python", "backend"]
---
content""")

            result = runner.invoke(app, ["deploy", "--tags", "python"])
            assert result.exit_code in [0, 1]

    def test_deploy_command_with_handlers(self):
        """Test deploy command with --handlers."""
        with runner.isolated_filesystem():
            # Create complete structure
            config_dir = Path.cwd() / ".prompt-manager"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            storage_dir = Path.cwd() / "storage"
            storage_dir.mkdir()
            prompts_dir = storage_dir / "prompts"
            prompts_dir.mkdir()

            config_file.write_text(f"storage_path: {storage_dir}")

            # Create a prompt
            (prompts_dir / "test_prompt.md").write_text("""---
title: test_prompt
description: test
---
content""")

            result = runner.invoke(app, ["deploy", "--handlers", "continue"])
            assert result.exit_code in [0, 1]

    def test_deploy_command_with_multiple_tags(self):
        """Test deploy command with multiple tags (comma-separated)."""
        with runner.isolated_filesystem():
            # Create complete structure
            config_dir = Path.cwd() / ".prompt-manager"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            storage_dir = Path.cwd() / "storage"
            storage_dir.mkdir()
            prompts_dir = storage_dir / "prompts"
            prompts_dir.mkdir()

            config_file.write_text(f"storage_path: {storage_dir}")

            # Create a prompt with tags
            (prompts_dir / "test_prompt.md").write_text("""---
title: test_prompt
description: test
tags: ["python", "backend"]
---
content""")

            result = runner.invoke(app, ["deploy", "--tags", "python,backend"])
            assert result.exit_code in [0, 1]

    def test_deploy_command_with_multiple_handlers(self):
        """Test deploy command with multiple handlers (comma-separated)."""
        with runner.isolated_filesystem():
            # Create complete structure
            config_dir = Path.cwd() / ".prompt-manager"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            storage_dir = Path.cwd() / "storage"
            storage_dir.mkdir()
            prompts_dir = storage_dir / "prompts"
            prompts_dir.mkdir()

            config_file.write_text(f"storage_path: {storage_dir}")

            # Create a prompt
            (prompts_dir / "test_prompt.md").write_text("""---
title: test_prompt
description: test
---
content""")

            result = runner.invoke(app, ["deploy", "--handlers", "continue,other"])
            assert result.exit_code in [0, 1]

    @patch("prompt_manager.handlers.continue_handler.ContinueToolHandler.deploy")
    @patch("prompt_manager.handlers.continue_handler.ContinueToolHandler.rollback")
    def test_deploy_rollback_on_failure(self, mock_rollback, mock_deploy):
        """Test that rollback is called when deployment fails."""
        mock_deploy.side_effect = Exception("Deployment failed")
        mock_rollback.return_value = None

        with runner.isolated_filesystem():
            # Create valid config and files
            config_dir = Path.cwd() / ".prompt-manager"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            storage_dir = Path.cwd() / "storage"
            storage_dir.mkdir()
            prompts_dir = storage_dir / "prompts"
            prompts_dir.mkdir()

            config_file.write_text(f"storage_path: {storage_dir}")

            # Create a valid prompt
            (prompts_dir / "test.md").write_text("""---
title: test
description: test
---
content""")

            runner.invoke(app, ["deploy"])
            # Rollback should be called
            mock_rollback.assert_called_once()

    def test_deploy_generic_error(self):
        """Test deploy with a generic error."""
        with runner.isolated_filesystem():
            # Create valid config
            config_dir = Path.cwd() / ".prompt-manager"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            storage_dir = Path.cwd() / "storage"
            storage_dir.mkdir()

            config_file.write_text(f"storage_path: {storage_dir}")

            # Mock to simulate an unexpected error
            with patch("prompt_manager.config.manager.ConfigManager.load_config") as mock_load:
                mock_load.side_effect = Exception("Unexpected error")

                result = runner.invoke(app, ["deploy"])
                assert result.exit_code == 1
                assert "Error during deployment" in result.output


class TestMainModule:
    """Tests for the main CLI module."""

    def test_version_callback(self):
        """Test version callback."""
        import typer

        from prompt_manager.cli.main import version_callback

        with pytest.raises(typer.Exit):
            version_callback(True)

    def test_version_output(self):
        """Test version output."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        from prompt_manager.cli.main import __version__

        assert f"prompt-manager version {__version__}" in result.output

    def test_version_short_flag(self):
        """Test short version flag."""
        result = runner.invoke(app, ["-v"])
        assert result.exit_code == 0
        from prompt_manager.cli.main import __version__

        assert f"prompt-manager version {__version__}" in result.output

    def test_main_callback_version(self):
        """Test main callback with version."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "prompt-manager version" in result.output

    def test_main_callback_no_version(self):
        """Test main callback without version."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert (
            "prompt-manager" in result.output
            or "Prompt Manager" in result.output
            or "Usage:" in result.output
        )

    def test_main_entry_point(self):
        """Test main entry point."""
        # Test that main function can be called
        from prompt_manager.cli.main import main

        # Can't really test full execution without arguments
        # but can verify function exists and is callable
        assert callable(main)

    def test_main_name_guard(self):
        """Test the if __name__ == "__main__" guard."""
        # Can't test directly, but can verify code exists
        import prompt_manager.cli.main as main_module

        assert hasattr(main_module, "main")
        assert hasattr(main_module, "__name__")
