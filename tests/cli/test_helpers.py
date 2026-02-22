"""Tests for CLI helper functions.

This module tests the helper functions extracted to prompt_unifier.cli.helpers.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import typer

from prompt_unifier.cli.helpers import (
    _display_handler_completion,
    _warn_missing_handler_dirs,
    check_duplicate_titles,
    determine_repo_configs,
    determine_storage_dir,
    determine_validation_targets,
    display_dry_run_preview,
    filter_content_files,
    load_config_or_exit,
    resolve_handler_base_path,
    resolve_validation_directory,
    scan_content_files,
)
from prompt_unifier.models.git_config import GitConfig, HandlerConfig, RepositoryConfig


class TestCLIHelpers:
    """Tests for CLI helper functions."""

    def test_load_config_or_exit_success(self, tmp_path: Path):
        """Test load_config_or_exit with valid config."""
        config_dir = tmp_path / ".prompt-unifier"
        config_dir.mkdir()
        config_file = config_dir / "config.yaml"
        storage_path = str(tmp_path / "storage")
        config_file.write_text(f"storage_path: {storage_path}\n")

        config = load_config_or_exit(config_file)
        assert config.storage_path == storage_path

    def test_load_config_or_exit_failure(self, tmp_path: Path):
        """Test load_config_or_exit with invalid/missing config."""
        config_file = tmp_path / "nonexistent.yaml"

        with pytest.raises(typer.Exit) as excinfo:
            load_config_or_exit(config_file)
        assert excinfo.value.exit_code == 1

    def test_scan_content_files(self, tmp_path: Path):
        """Test scan_content_files discovers prompts and rules."""
        storage_dir = tmp_path / "storage"
        prompts_dir = storage_dir / "prompts"
        rules_dir = storage_dir / "rules"
        prompts_dir.mkdir(parents=True)
        rules_dir.mkdir(parents=True)

        (prompts_dir / "test_prompt.md").write_text(
            "---\ntitle: Prompt\ndescription: desc\nversion: 1.0.0\nauthor: me\n---\nContent"
        )
        (rules_dir / "test_rule.md").write_text(
            "---\ntitle: Rule\ndescription: desc\ncategory: testing\n---\nContent"
        )
        # Non-md file should be ignored
        (prompts_dir / "ignore.txt").write_text("ignored")

        content_files = scan_content_files(storage_dir)
        assert len(content_files) == 2

        types = [cf[1] for cf in content_files]
        assert "prompt" in types
        assert "rule" in types

    def test_scan_content_files_includes_skills(self, tmp_path: Path):
        """Test scan_content_files discovers skills in addition to prompts and rules."""
        storage_dir = tmp_path / "storage"
        skills_dir = storage_dir / "skills"
        skills_dir.mkdir(parents=True)

        (skills_dir / "my-skill.md").write_text(
            "---\nname: my-skill\ndescription: A skill\n---\nSkill body"
        )

        content_files = scan_content_files(storage_dir)
        assert len(content_files) == 1

        parsed, content_type, _ = content_files[0]
        assert content_type == "skill"
        assert parsed.name == "my-skill"

    def test_scan_content_files_skills_parse_error_warns(self, tmp_path: Path):
        """Test scan_content_files warns on unparseable skill files."""
        storage_dir = tmp_path / "storage"
        skills_dir = storage_dir / "skills"
        skills_dir.mkdir(parents=True)

        # Invalid skill (missing required fields)
        (skills_dir / "bad.md").write_text("---\ntitle: wrong\n---\nBody")

        content_files = scan_content_files(storage_dir)
        # Bad file is skipped, no crash
        assert len(content_files) == 0

    def test_check_duplicate_titles(self):
        """Test check_duplicate_titles identifies duplicates."""
        mock_prompt1 = MagicMock()
        mock_prompt1.title = "Duplicate"
        mock_prompt2 = MagicMock()
        mock_prompt2.title = "Duplicate"
        mock_prompt3 = MagicMock()
        mock_prompt3.title = "Unique"

        content_files = [
            (mock_prompt1, "prompt", Path("file1.md")),
            (mock_prompt2, "prompt", Path("file2.md")),
            (mock_prompt3, "prompt", Path("file3.md")),
        ]

        duplicates = check_duplicate_titles(content_files)
        assert "Duplicate" in duplicates
        assert len(duplicates["Duplicate"]) == 2
        assert "Unique" not in duplicates

    def test_filter_content_files(self):
        """Test filter_content_files by name and tags."""
        mock_prompt1 = MagicMock()
        mock_prompt1.title = "Prompt1"
        mock_prompt1.tags = ["tag1", "common"]

        mock_prompt2 = MagicMock()
        mock_prompt2.title = "Prompt2"
        mock_prompt2.tags = ["tag2", "common"]

        content_files = [
            (mock_prompt1, "prompt", Path("file1.md")),
            (mock_prompt2, "prompt", Path("file2.md")),
        ]

        # Filter by name
        filtered = filter_content_files(content_files, "Prompt1", None)
        assert len(filtered) == 1
        assert filtered[0][0].title == "Prompt1"

        # Filter by tag
        filtered = filter_content_files(content_files, None, ["tag2"])
        assert len(filtered) == 1
        assert filtered[0][0].title == "Prompt2"

        # Filter by multiple tags
        filtered = filter_content_files(content_files, None, ["common"])
        assert len(filtered) == 2

    def test_resolve_handler_base_path_cli_priority(self):
        """Test resolve_handler_base_path prioritizes CLI flag."""
        config = GitConfig(handlers={"continue": HandlerConfig(base_path="/config/path")})
        cli_path = Path("/cli/path")

        resolved = resolve_handler_base_path("continue", cli_path, config)
        assert resolved == cli_path

    def test_resolve_handler_base_path_config_fallback(self):
        """Test resolve_handler_base_path falls back to config."""
        config = GitConfig(handlers={"continue": HandlerConfig(base_path="/config/path")})

        resolved = resolve_handler_base_path("continue", None, config)
        assert str(resolved) == "/config/path"

    def test_determine_storage_dir(self):
        """Test determine_storage_dir precedence."""
        # 1. Explicit
        assert determine_storage_dir("/explicit", None) == Path("/explicit")

        # 2. Config
        config = GitConfig(storage_path="/config/path")
        assert determine_storage_dir(None, config) == Path("/config/path")

        # 3. Default
        assert ".prompt-unifier/storage" in str(determine_storage_dir(None, None))

    def test_determine_repo_configs_cli(self):
        """Test determine_repo_configs from CLI."""
        config = GitConfig(repos=[RepositoryConfig(url="config-url")])
        repos = ["cli-url"]

        configs = determine_repo_configs(repos, config)
        assert len(configs) == 1
        assert configs[0].url == "cli-url"

    def test_determine_repo_configs_config(self):
        """Test determine_repo_configs from config."""
        config = GitConfig(repos=[RepositoryConfig(url="config-url")])

        configs = determine_repo_configs(None, config)
        assert len(configs) == 1
        assert configs[0].url == "config-url"

    def test_determine_repo_configs_empty_raises(self):
        """Test determine_repo_configs raises error if no repos found."""
        config = GitConfig(repos=None)
        with pytest.raises(typer.Exit):
            determine_repo_configs(None, config)

    def test_resolve_validation_directory_explicit(self):
        """Test resolve_validation_directory with explicit path."""
        path = Path("/some/path")
        assert resolve_validation_directory(path, "dir", "file") == path

    @patch("prompt_unifier.cli.helpers.ConfigManager.load_config")
    @patch("pathlib.Path.exists")
    def test_resolve_validation_directory_config(self, mock_exists, mock_load):
        """Test resolve_validation_directory from config."""
        mock_exists.return_value = True
        mock_config = MagicMock()
        mock_config.storage_path = "/config/storage"
        mock_load.return_value = mock_config

        resolved = resolve_validation_directory(None, ".prompt-unifier", "config.yaml")
        assert str(resolved) == "/config/storage"

    def test_determine_validation_targets_hierarchy_detection(self, tmp_path: Path):
        """Test determine_validation_targets detects if already in prompts/rules."""
        prompts_subdir = tmp_path / "prompts" / "python"
        prompts_subdir.mkdir(parents=True)

        # Should return the directory directly if inside 'prompts'
        targets = determine_validation_targets(prompts_subdir, "all")
        assert targets == [prompts_subdir]

        # Should error if inside 'prompts' but type is 'rules'
        with pytest.raises(typer.Exit):
            determine_validation_targets(prompts_subdir, "rules")

    def test_determine_validation_targets_discovery(self, tmp_path: Path):
        """Test determine_validation_targets finds subdirectories."""
        base_dir = tmp_path / "base"
        prompts = base_dir / "prompts"
        rules = base_dir / "rules"
        prompts.mkdir(parents=True)
        rules.mkdir(parents=True)

        targets = determine_validation_targets(base_dir, "all")
        assert len(targets) == 2
        assert prompts in targets
        assert rules in targets

    @patch("rich.console.Console.print")
    def test_warn_missing_handler_dirs(self, mock_print):
        """Test _warn_missing_handler_dirs identifies missing directories."""
        handler = MagicMock()
        handler.prompts_dir = Path("/nonexistent/prompts")
        handler.rules_dir = Path("/nonexistent/rules")

        _warn_missing_handler_dirs(handler)
        assert mock_print.call_count == 2

    @patch("prompt_unifier.cli.helpers._build_preview_table")
    @patch("rich.console.Console.print")
    def test_display_dry_run_preview(self, mock_print, mock_build):
        """Test display_dry_run_preview prints info."""
        handler = MagicMock()
        handler.get_name.return_value = "test-handler"

        display_dry_run_preview([MagicMock()], [handler], Path("p"), Path("r"))
        assert mock_print.called

    @patch("rich.console.Console.print")
    def test_display_handler_completion(self, mock_print):
        """Test _display_handler_completion prints correct messages."""
        _display_handler_completion("handler", 5)
        _display_handler_completion("handler", 0)
        assert mock_print.call_count == 2
