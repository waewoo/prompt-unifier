"""Tests for BatchValidator class for multi-file validation orchestration."""

from pathlib import Path

from prompt_manager.core.batch_validator import BatchValidator


class TestBatchValidator:
    """Test suite for BatchValidator class."""

    def test_validate_directory_multiple_files_independently(self, tmp_path: Path) -> None:
        """Test that multiple files are validated independently."""
        validator = BatchValidator()

        # Create valid and invalid files
        (tmp_path / "valid.md").write_text(
            "title: test\ndescription: A test prompt\n---\n\nThis is the content."
        )
        (tmp_path / "invalid.md").write_text("---\ntitle: test\n---\n\nMissing description.")

        summary = validator.validate_directory(tmp_path)

        assert summary.total_files == 2
        assert len(summary.results) == 2

    def test_validate_directory_error_aggregation(self, tmp_path: Path) -> None:
        """Test that errors are aggregated across all files."""
        validator = BatchValidator()

        # Create files with errors
        (tmp_path / "error1.md").write_text("---\ntitle: test\n---\n\nNo description")
        (tmp_path / "error2.md").write_text("description: test\n---\n\nNo name")

        summary = validator.validate_directory(tmp_path)

        # Both files should have errors
        assert summary.failed == 2
        assert summary.error_count >= 2  # At least 2 errors (missing required fields)
        assert summary.success is False

    def test_validate_directory_warning_aggregation(self, tmp_path: Path) -> None:
        """Test that warnings are aggregated across all files."""
        validator = BatchValidator()

        # Create files with warnings (missing optional fields)
        (tmp_path / "warn1.md").write_text(
            "---\ntitle: test1\ndescription: Test 1\n---\n\nContent here"
        )
        (tmp_path / "warn2.md").write_text(
            "---\ntitle: test2\ndescription: Test 2\n---\n\nContent here"
        )

        summary = validator.validate_directory(tmp_path)

        # Files should pass but have warnings
        assert summary.passed == 2
        assert summary.failed == 0
        assert summary.warning_count >= 2  # At least 2 warnings (missing version/author)
        assert summary.success is True  # Warnings don't block

    def test_validate_directory_summary_statistics(self, tmp_path: Path) -> None:
        """Test that summary statistics are computed correctly."""
        validator = BatchValidator()

        # Create mixed scenario
        (tmp_path / "pass1.md").write_text("---\ntitle: pass1\ndescription: Pass 1\n---\n\nContent")
        (tmp_path / "pass2.md").write_text("---\ntitle: pass2\ndescription: Pass 2\n---\n\nContent")
        (tmp_path / "fail1.md").write_text("---\ntitle: fail1\n---\n\nNo description")

        summary = validator.validate_directory(tmp_path)

        assert summary.total_files == 3
        assert summary.passed == 2
        assert summary.failed == 1
        assert summary.error_count >= 1
        assert summary.success is False  # At least one error

    def test_validate_directory_continues_after_errors(self, tmp_path: Path) -> None:
        """Test that validation continues even after encountering errors."""
        validator = BatchValidator()

        # Create files with various errors
        (tmp_path / "error1.md").write_text("invalid yaml: [")
        (tmp_path / "error2.md").write_text("---\ntitle: test\n---\n\nNo description")
        (tmp_path / "valid.md").write_text(
            "---\ntitle: valid\ndescription: Valid file\n---\n\nContent"
        )

        summary = validator.validate_directory(tmp_path)

        # All files should be validated despite errors
        assert summary.total_files == 3
        assert len(summary.results) == 3
        # At least one should pass (the valid file)
        assert summary.passed >= 1

    def test_validate_directory_mixed_results(self, tmp_path: Path) -> None:
        """Test mixed results with some passing and some failing."""
        validator = BatchValidator()

        # Create files with different outcomes
        (tmp_path / "pass.md").write_text(
            "---\ntitle: pass\ndescription: Pass\nversion: 1.0.0\nauthor: Test\n---\n\nContent"
        )
        (tmp_path / "warn.md").write_text(
            "---\ntitle: warn\ndescription: Warn\n---\n\nContent"  # Missing optional fields
        )
        (tmp_path / "fail.md").write_text(
            "---\ntitle: fail\n---\n\nNo description"  # Missing required field
        )

        summary = validator.validate_directory(tmp_path)

        assert summary.total_files == 3
        # Pass file should have no warnings (all fields present)
        # Warn file should pass but have warnings
        # Fail file should fail
        passed_results = [r for r in summary.results if r.status == "passed"]
        failed_results = [r for r in summary.results if r.status == "failed"]

        assert len(passed_results) == 2
        assert len(failed_results) == 1
        assert summary.passed == 2
        assert summary.failed == 1

    def test_validate_directory_all_files_pass(self, tmp_path: Path) -> None:
        """Test scenario where all files pass validation."""
        validator = BatchValidator()

        # Create only valid files
        (tmp_path / "valid1.md").write_text(
            "---\ntitle: valid1\ndescription: Valid 1\nversion: 1.0.0\n"
            "author: Test\n---\n\nContent 1"
        )
        (tmp_path / "valid2.md").write_text(
            "---\ntitle: valid2\ndescription: Valid 2\nversion: 2.0.0\n"
            "author: Test\n---\n\nContent 2"
        )

        summary = validator.validate_directory(tmp_path)

        assert summary.total_files == 2
        assert summary.passed == 2
        assert summary.failed == 0
        assert summary.error_count == 0
        assert summary.success is True
        assert all(r.status == "passed" for r in summary.results)
