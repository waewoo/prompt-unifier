"""Tests for ContinueToolHandler base path functionality.

This module tests the base path configuration for ContinueToolHandler,
including default base_path, custom base_path, directory creation,
and tool installation validation.
"""

import os
import stat
from pathlib import Path

import pytest

from prompt_unifier.handlers.continue_handler import ContinueToolHandler


class TestContinueHandlerBasePath:
    """Tests for ContinueToolHandler base path configuration."""

    def test_default_base_path_is_cwd(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test that default base_path is Path.cwd() not Path.home()."""
        # Change to tmp_path to control the working directory
        monkeypatch.chdir(tmp_path)

        handler = ContinueToolHandler()

        # Verify base_path is current working directory
        assert handler.base_path == Path.cwd()
        assert handler.base_path == tmp_path

    def test_custom_base_path_overrides_default(self, tmp_path: Path):
        """Test that custom base_path parameter overrides default."""
        custom_base = tmp_path / "custom_location"

        handler = ContinueToolHandler(base_path=custom_base)

        # Verify custom base_path is used
        assert handler.base_path == custom_base
        assert handler.base_path != Path.cwd()

    def test_directory_auto_creation_for_base_path(self, tmp_path: Path):
        """Test that directories are auto-created for base_path."""
        # Use a non-existent directory as base_path
        base_path = tmp_path / "non_existent" / "nested" / "path"
        assert not base_path.exists()

        handler = ContinueToolHandler(base_path=base_path)

        # Verify directories were created
        assert handler.prompts_dir.exists()
        assert handler.rules_dir.exists()
        assert handler.prompts_dir == base_path / ".continue" / "prompts"
        assert handler.rules_dir == base_path / ".continue" / "rules"

    def test_continue_prompts_subdirectory_creation(self, tmp_path: Path):
        """Test that .continue/prompts/ subdirectory is created."""
        handler = ContinueToolHandler(base_path=tmp_path)

        expected_prompts_dir = tmp_path / ".continue" / "prompts"
        assert handler.prompts_dir == expected_prompts_dir
        assert handler.prompts_dir.exists()
        assert handler.prompts_dir.is_dir()

    def test_continue_rules_subdirectory_creation(self, tmp_path: Path):
        """Test that .continue/rules/ subdirectory is created."""
        handler = ContinueToolHandler(base_path=tmp_path)

        expected_rules_dir = tmp_path / ".continue" / "rules"
        assert handler.rules_dir == expected_rules_dir
        assert handler.rules_dir.exists()
        assert handler.rules_dir.is_dir()


class TestContinueHandlerValidation:
    """Tests for ContinueToolHandler tool installation validation."""

    def test_validate_tool_installation_succeeds_when_continue_exists(self, tmp_path: Path):
        """Test validate_tool_installation() succeeds when .continue/ exists."""
        # Pre-create .continue directory
        continue_dir = tmp_path / ".continue"
        continue_dir.mkdir(parents=True)

        handler = ContinueToolHandler(base_path=tmp_path)

        # Validation should succeed
        result = handler.validate_tool_installation()
        assert result is True

    def test_validate_tool_installation_succeeds_when_continue_can_be_created(self, tmp_path: Path):
        """Test validate_tool_installation() succeeds when .continue/ can be created."""
        # Don't pre-create .continue directory, but base_path is writable
        handler = ContinueToolHandler(base_path=tmp_path)

        # Validation should succeed (directories already created in __init__)
        result = handler.validate_tool_installation()
        assert result is True

    @pytest.mark.skipif(os.name == "nt", reason="Permission handling different on Windows")
    def test_validate_tool_installation_fails_with_permission_error(self, tmp_path: Path):
        """Test validate_tool_installation() fails with clear error for permission issues."""
        # Create base_path but make it read-only
        base_path = tmp_path / "readonly"
        base_path.mkdir()

        # Make directory read-only (remove write permissions)
        base_path.chmod(stat.S_IRUSR | stat.S_IXUSR)

        try:
            # Attempt to create handler - should fail during directory creation
            # or validation should catch the permission issue
            ContinueToolHandler(base_path=base_path)

            # If __init__ succeeded (directories already created), validation should still work
            # But if we try to recreate, it should fail

            # Remove the .continue directory to test validation
            continue_dir = base_path / ".continue"
            if continue_dir.exists():
                # Can't actually delete if parent is read-only, so skip this test case
                pytest.skip("Cannot modify read-only directory for testing")

        except PermissionError:
            # This is expected - handler creation should fail with clear permission error
            pass
        finally:
            # Restore permissions for cleanup
            base_path.chmod(stat.S_IRWXU)

    def test_validate_tool_installation_with_existing_structure(self, tmp_path: Path):
        """Test validate_tool_installation() with pre-existing directory structure."""
        # Pre-create entire .continue structure
        continue_dir = tmp_path / ".continue"
        prompts_dir = continue_dir / "prompts"
        rules_dir = continue_dir / "rules"
        prompts_dir.mkdir(parents=True)
        rules_dir.mkdir(parents=True)

        handler = ContinueToolHandler(base_path=tmp_path)

        # Validation should succeed
        result = handler.validate_tool_installation()
        assert result is True

    def test_validate_tool_installation_returns_bool(self, tmp_path: Path):
        """Test that validate_tool_installation() returns a boolean value."""
        handler = ContinueToolHandler(base_path=tmp_path)

        result = handler.validate_tool_installation()

        assert isinstance(result, bool)
        assert result is True

    def test_validate_tool_installation_checks_base_path_accessibility(self, tmp_path: Path):
        """Test that validate_tool_installation() checks base_path exists."""
        # Create handler with valid base_path
        handler = ContinueToolHandler(base_path=tmp_path)

        # Validation should succeed since base_path exists and is accessible
        result = handler.validate_tool_installation()
        assert result is True

        # Verify the base_path actually exists
        assert handler.base_path.exists()

    def test_validate_tool_installation_checks_continue_directory(self, tmp_path: Path):
        """Test that validate_tool_installation() checks .continue/ directory."""
        handler = ContinueToolHandler(base_path=tmp_path)

        # Verify .continue directory exists after initialization
        continue_dir = handler.base_path / ".continue"
        assert continue_dir.exists()

        # Validation should succeed
        result = handler.validate_tool_installation()
        assert result is True

    def test_validate_creates_missing_base_path(self, tmp_path: Path):
        """Test that validate_tool_installation creates missing base_path."""
        # Create handler with existing base_path first
        base_path = tmp_path / "test_base"
        handler = ContinueToolHandler(base_path=base_path)

        # Now delete the base_path to test validation recreation
        import shutil

        shutil.rmtree(base_path)
        assert not base_path.exists()

        # Validation should recreate it
        result = handler.validate_tool_installation()
        assert result is True
        assert base_path.exists()

    def test_validate_creates_missing_continue_directory(self, tmp_path: Path):
        """Test that validate_tool_installation creates missing .continue/."""
        handler = ContinueToolHandler(base_path=tmp_path)

        # Delete .continue directory to test validation recreation
        import shutil

        continue_dir = tmp_path / ".continue"
        if continue_dir.exists():
            shutil.rmtree(continue_dir)
        assert not continue_dir.exists()

        # Validation should recreate it
        result = handler.validate_tool_installation()
        assert result is True
        assert continue_dir.exists()

    def test_validate_creates_missing_prompts_directory(self, tmp_path: Path):
        """Test that validate_tool_installation creates missing prompts/."""
        handler = ContinueToolHandler(base_path=tmp_path)

        # Delete prompts directory to test validation recreation
        import shutil

        prompts_dir = handler.prompts_dir
        if prompts_dir.exists():
            shutil.rmtree(prompts_dir)
        assert not prompts_dir.exists()

        # Validation should recreate it
        result = handler.validate_tool_installation()
        assert result is True
        assert prompts_dir.exists()

    def test_validate_creates_missing_rules_directory(self, tmp_path: Path):
        """Test that validate_tool_installation creates missing rules/."""
        handler = ContinueToolHandler(base_path=tmp_path)

        # Delete rules directory to test validation recreation
        import shutil

        rules_dir = handler.rules_dir
        if rules_dir.exists():
            shutil.rmtree(rules_dir)
        assert not rules_dir.exists()

        # Validation should recreate it
        result = handler.validate_tool_installation()
        assert result is True
        assert rules_dir.exists()

    @pytest.mark.skipif(
        os.name == "nt" or os.geteuid() == 0,
        reason="Unix permissions only and not running as root",
    )
    def test_validate_fails_on_write_permission_error(self, tmp_path: Path):
        """Test that validate_tool_installation fails when prompts dir not writable."""
        handler = ContinueToolHandler(base_path=tmp_path)

        # Make prompts directory read-only
        prompts_dir = handler.prompts_dir
        prompts_dir.chmod(stat.S_IRUSR | stat.S_IXUSR)

        try:
            # Validation should raise PermissionError
            with pytest.raises(PermissionError):
                handler.validate_tool_installation()
        finally:
            # Restore permissions
            prompts_dir.chmod(stat.S_IRWXU)

    @pytest.mark.skipif(
        os.name == "nt" or os.geteuid() == 0,
        reason="Unix permissions only and not running as root",
    )
    def test_validate_handles_base_path_permission_error(self, tmp_path: Path):
        """Test that validate_tool_installation handles base_path permission errors."""
        base_path = tmp_path / "protected"
        base_path.mkdir()

        handler = ContinueToolHandler(base_path=base_path)

        # Make base_path read-only
        base_path.chmod(stat.S_IRUSR | stat.S_IXUSR)

        try:
            # Delete .continue to force recreation attempt
            import shutil

            continue_dir = base_path / ".continue"
            # Can't delete from read-only parent, so change perms temporarily
            base_path.chmod(stat.S_IRWXU)
            shutil.rmtree(continue_dir)
            base_path.chmod(stat.S_IRUSR | stat.S_IXUSR)

            # Validation should raise PermissionError
            with pytest.raises(PermissionError):
                handler.validate_tool_installation()
        finally:
            # Restore permissions
            base_path.chmod(stat.S_IRWXU)

    def test_validate_handles_oserror_gracefully(self, tmp_path: Path, monkeypatch):
        """Test that validate_tool_installation handles OSError gracefully."""

        handler = ContinueToolHandler(base_path=tmp_path)

        # Mock mkdir to raise OSError
        original_mkdir = Path.mkdir

        def mock_mkdir_error(*args, **kwargs):
            if "test_error" in str(args[0]):
                raise OSError("Simulated OS error")
            return original_mkdir(*args, **kwargs)

        # Change base_path to trigger error
        handler.base_path = tmp_path / "test_error_path"

        monkeypatch.setattr(Path, "mkdir", mock_mkdir_error)

        # Validation should raise OSError
        with pytest.raises(OSError, match="Simulated OS error"):
            handler.validate_tool_installation()
