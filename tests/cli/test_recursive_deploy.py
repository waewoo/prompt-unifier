"""Tests for recursive file discovery in deploy command (Task Group 1)."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from prompt_manager.cli.main import app

runner = CliRunner()


@pytest.fixture
def mock_storage_with_subdirs(tmp_path: Path) -> Path:
    """Create mock storage with prompts and rules in subdirectories."""
    storage_dir = tmp_path / "storage"
    storage_dir.mkdir()

    # Root level prompts
    prompts_dir = storage_dir / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "root-prompt.md").write_text("""---
title: root-prompt
description: A prompt at root level
tags: ["python"]
version: 1.0.0
---

Root level prompt content
""")

    # Subdirectory prompts
    subdir_prompts = prompts_dir / "backend"
    subdir_prompts.mkdir()
    (subdir_prompts / "backend-prompt.md").write_text("""---
title: backend-prompt
description: A prompt in subdirectory
tags: ["python", "backend"]
version: 1.0.0
---

Backend subdirectory prompt content
""")

    # Nested subdirectory prompts
    nested_prompts = subdir_prompts / "api"
    nested_prompts.mkdir()
    (nested_prompts / "api-prompt.md").write_text("""---
title: api-prompt
description: A prompt in nested subdirectory
tags: ["python", "api"]
version: 1.0.0
---

Nested API prompt content
""")

    # Root level rules
    rules_dir = storage_dir / "rules"
    rules_dir.mkdir()
    (rules_dir / "root-rule.md").write_text("""---
title: root-rule
description: A rule at root level
category: testing
tags: ["python"]
version: 1.0.0
---

Root level rule content
""")

    # Subdirectory rules
    subdir_rules = rules_dir / "security"
    subdir_rules.mkdir()
    (subdir_rules / "security-rule.md").write_text("""---
title: security-rule
description: A rule in subdirectory
category: security
tags: ["python", "security"]
version: 1.0.0
---

Security subdirectory rule content
""")

    return storage_dir


@pytest.fixture
def mock_storage_with_duplicates(tmp_path: Path) -> Path:
    """Create mock storage with duplicate titles."""
    storage_dir = tmp_path / "storage"
    storage_dir.mkdir()

    prompts_dir = storage_dir / "prompts"
    prompts_dir.mkdir()

    # First prompt with title "duplicate-prompt"
    (prompts_dir / "first-duplicate.md").write_text("""---
title: duplicate-prompt
description: First duplicate prompt
tags: ["python"]
version: 1.0.0
---

First duplicate content
""")

    # Subdirectory with same title
    subdir = prompts_dir / "backend"
    subdir.mkdir()
    (subdir / "second-duplicate.md").write_text("""---
title: duplicate-prompt
description: Second duplicate prompt
tags: ["backend"]
version: 1.0.0
---

Second duplicate content
""")

    # Rules directory (no duplicates)
    rules_dir = storage_dir / "rules"
    rules_dir.mkdir()
    (rules_dir / "normal-rule.md").write_text("""---
title: normal-rule
description: A normal rule
category: testing
tags: ["test"]
version: 1.0.0
---

Normal rule content
""")

    return storage_dir


class TestRecursiveFileDiscovery:
    """Tests for recursive file discovery in deploy command."""

    def test_deploy_finds_files_in_subdirectories(
        self, tmp_path: Path, mock_storage_with_subdirs: Path
    ):
        """Test that deploy command discovers files in subdirectories."""
        config_dir = tmp_path / ".prompt-manager"
        config_dir.mkdir()
        config_file = config_dir / "config.yaml"
        config_file.write_text(f"""
repo_url: https://example.com/repo.git
storage_path: {mock_storage_with_subdirs}
target_handlers: ["continue"]
""")

        with patch("prompt_manager.cli.commands.Path.cwd", return_value=tmp_path):
            with patch("prompt_manager.cli.commands.ContinueToolHandler") as mock_handler:
                mock_handler_instance = MagicMock()
                mock_handler.return_value = mock_handler_instance
                mock_handler_instance.get_name.return_value = "continue"

                result = runner.invoke(app, ["deploy"])

                # Should discover all files (3 prompts + 2 rules = 5 files)
                # Check that deploy was called for files in subdirectories
                assert result.exit_code == 0
                assert mock_handler_instance.deploy.call_count == 5

    def test_deploy_finds_files_in_nested_subdirectories(
        self, tmp_path: Path, mock_storage_with_subdirs: Path
    ):
        """Test that deploy discovers files in deeply nested subdirectories."""
        config_dir = tmp_path / ".prompt-manager"
        config_dir.mkdir()
        config_file = config_dir / "config.yaml"
        config_file.write_text(f"""
repo_url: https://example.com/repo.git
storage_path: {mock_storage_with_subdirs}
target_handlers: ["continue"]
""")

        with patch("prompt_manager.cli.commands.Path.cwd", return_value=tmp_path):
            with patch("prompt_manager.cli.commands.ContinueToolHandler") as mock_handler:
                mock_handler_instance = MagicMock()
                mock_handler.return_value = mock_handler_instance
                mock_handler_instance.get_name.return_value = "continue"

                runner.invoke(app, ["deploy"])

                # Verify nested file was deployed (api-prompt in backend/api/)
                deployed_titles = []
                for call in mock_handler_instance.deploy.call_args_list:
                    frontmatter = call[0][0]  # First positional argument
                    deployed_titles.append(frontmatter.title)

                assert "api-prompt" in deployed_titles
                assert "backend-prompt" in deployed_titles
                assert "security-rule" in deployed_titles

    def test_deploy_still_finds_files_at_root(
        self, tmp_path: Path, mock_storage_with_subdirs: Path
    ):
        """Test that deploy still discovers files at the root level."""
        config_dir = tmp_path / ".prompt-manager"
        config_dir.mkdir()
        config_file = config_dir / "config.yaml"
        config_file.write_text(f"""
repo_url: https://example.com/repo.git
storage_path: {mock_storage_with_subdirs}
target_handlers: ["continue"]
""")

        with patch("prompt_manager.cli.commands.Path.cwd", return_value=tmp_path):
            with patch("prompt_manager.cli.commands.ContinueToolHandler") as mock_handler:
                mock_handler_instance = MagicMock()
                mock_handler.return_value = mock_handler_instance
                mock_handler_instance.get_name.return_value = "continue"

                runner.invoke(app, ["deploy"])

                # Verify root level files were deployed
                deployed_titles = []
                for call in mock_handler_instance.deploy.call_args_list:
                    frontmatter = call[0][0]
                    deployed_titles.append(frontmatter.title)

                assert "root-prompt" in deployed_titles
                assert "root-rule" in deployed_titles

    def test_deploy_recursive_with_tag_filter(
        self, tmp_path: Path, mock_storage_with_subdirs: Path
    ):
        """Test recursive discovery works with tag filtering."""
        config_dir = tmp_path / ".prompt-manager"
        config_dir.mkdir()
        config_file = config_dir / "config.yaml"
        config_file.write_text(f"""
repo_url: https://example.com/repo.git
storage_path: {mock_storage_with_subdirs}
target_handlers: ["continue"]
""")

        with patch("prompt_manager.cli.commands.Path.cwd", return_value=tmp_path):
            with patch("prompt_manager.cli.commands.ContinueToolHandler") as mock_handler:
                mock_handler_instance = MagicMock()
                mock_handler.return_value = mock_handler_instance
                mock_handler_instance.get_name.return_value = "continue"

                # Deploy only files tagged with "api"
                result = runner.invoke(app, ["deploy", "--tags", "api"])

                # Should only deploy api-prompt
                assert result.exit_code == 0
                deployed_titles = []
                for call in mock_handler_instance.deploy.call_args_list:
                    frontmatter = call[0][0]
                    deployed_titles.append(frontmatter.title)

                assert "api-prompt" in deployed_titles
                assert len(deployed_titles) == 1


class TestDuplicateTitleDetection:
    """Tests for duplicate title conflict detection."""

    def test_deploy_fails_with_duplicate_titles(
        self, tmp_path: Path, mock_storage_with_duplicates: Path
    ):
        """Test that deploy fails when duplicate titles are detected."""
        config_dir = tmp_path / ".prompt-manager"
        config_dir.mkdir()
        config_file = config_dir / "config.yaml"
        config_file.write_text(f"""
repo_url: https://example.com/repo.git
storage_path: {mock_storage_with_duplicates}
target_handlers: ["continue"]
""")

        with patch("prompt_manager.cli.commands.Path.cwd", return_value=tmp_path):
            result = runner.invoke(app, ["deploy"])

            # Should fail with exit code 1
            assert result.exit_code == 1
            # Should mention duplicate titles
            assert "duplicate" in result.output.lower() or "conflict" in result.output.lower()
            assert "duplicate-prompt" in result.output

    def test_deploy_error_message_lists_conflicting_files(
        self, tmp_path: Path, mock_storage_with_duplicates: Path
    ):
        """Test that error message lists the conflicting files."""
        config_dir = tmp_path / ".prompt-manager"
        config_dir.mkdir()
        config_file = config_dir / "config.yaml"
        config_file.write_text(f"""
repo_url: https://example.com/repo.git
storage_path: {mock_storage_with_duplicates}
target_handlers: ["continue"]
""")

        with patch("prompt_manager.cli.commands.Path.cwd", return_value=tmp_path):
            result = runner.invoke(app, ["deploy"])

            # Error message should list both files with the duplicate title
            assert "first-duplicate.md" in result.output or "duplicate-prompt" in result.output
            # Should show at least the title that's duplicated
            assert "duplicate-prompt" in result.output

    def test_deploy_succeeds_without_duplicates(
        self, tmp_path: Path, mock_storage_with_subdirs: Path
    ):
        """Test that deploy succeeds when there are no duplicate titles."""
        config_dir = tmp_path / ".prompt-manager"
        config_dir.mkdir()
        config_file = config_dir / "config.yaml"
        config_file.write_text(f"""
repo_url: https://example.com/repo.git
storage_path: {mock_storage_with_subdirs}
target_handlers: ["continue"]
""")

        with patch("prompt_manager.cli.commands.Path.cwd", return_value=tmp_path):
            with patch("prompt_manager.cli.commands.ContinueToolHandler") as mock_handler:
                mock_handler_instance = MagicMock()
                mock_handler.return_value = mock_handler_instance
                mock_handler_instance.get_name.return_value = "continue"

                result = runner.invoke(app, ["deploy"])

                # Should succeed
                assert result.exit_code == 0
                # Should not mention duplicates
                assert "duplicate" not in result.output.lower()

    def test_duplicate_detection_across_prompts_and_rules(self, tmp_path: Path):
        """Test that duplicate titles are detected across prompts and rules."""
        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()

        prompts_dir = storage_dir / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "shared-name.md").write_text("""---
title: shared-title
description: A prompt
tags: ["test"]
version: 1.0.0
---

Prompt content
""")

        rules_dir = storage_dir / "rules"
        rules_dir.mkdir()
        (rules_dir / "shared-name-rule.md").write_text("""---
title: shared-title
description: A rule
category: testing
tags: ["test"]
version: 1.0.0
---

Rule content
""")

        config_dir = tmp_path / ".prompt-manager"
        config_dir.mkdir()
        config_file = config_dir / "config.yaml"
        config_file.write_text(f"""
repo_url: https://example.com/repo.git
storage_path: {storage_dir}
target_handlers: ["continue"]
""")

        with patch("prompt_manager.cli.commands.Path.cwd", return_value=tmp_path):
            result = runner.invoke(app, ["deploy"])

            # Should fail due to duplicate title across prompts and rules
            assert result.exit_code == 1
            assert "duplicate" in result.output.lower() or "conflict" in result.output.lower()
            assert "shared-title" in result.output
