"""Tests for UTF-8 encoding validation logic."""

from pathlib import Path

import pytest

from prompt_manager.core.encoding import EncodingValidator
from prompt_manager.models.validation import ErrorCode, ValidationSeverity


class TestEncodingValidator:
    """Tests for EncodingValidator class."""

    @pytest.fixture
    def validator(self) -> EncodingValidator:
        """Create an EncodingValidator instance."""
        return EncodingValidator()

    def test_valid_utf8_file_loads_successfully(
        self, validator: EncodingValidator, tmp_path: Path
    ) -> None:
        """Test that a valid UTF-8 file loads successfully."""
        test_file = tmp_path / "test.md"
        content = (
            "name: test\ndescription: A test prompt\n>>>\nThis is valid UTF-8 content with emoji 🎉"
        )
        test_file.write_text(content, encoding="utf-8")

        file_content, issues = validator.validate_encoding(test_file)

        assert file_content is not None
        assert content in file_content or file_content == content
        assert len(issues) == 0

    def test_invalid_utf8_bytes_trigger_error(
        self, validator: EncodingValidator, tmp_path: Path
    ) -> None:
        """Test that invalid UTF-8 bytes trigger INVALID_ENCODING error."""
        test_file = tmp_path / "invalid.md"
        # Write invalid UTF-8 bytes directly
        test_file.write_bytes(b"name: test\n\xff\xfe\nInvalid UTF-8")

        file_content, issues = validator.validate_encoding(test_file)

        assert file_content is None
        assert len(issues) == 1
        assert issues[0].code == ErrorCode.INVALID_ENCODING.value
        assert issues[0].severity == ValidationSeverity.ERROR
        assert "UTF-8" in issues[0].message or "encoding" in issues[0].message.lower()
        assert "UTF-8" in issues[0].suggestion

    def test_file_not_found_error_handling(
        self, validator: EncodingValidator, tmp_path: Path
    ) -> None:
        """Test that file not found error is handled gracefully."""
        non_existent_file = tmp_path / "does_not_exist.md"

        file_content, issues = validator.validate_encoding(non_existent_file)

        assert file_content is None
        assert len(issues) == 1
        assert issues[0].severity == ValidationSeverity.ERROR
        assert (
            "not found" in issues[0].message.lower()
            or "does not exist" in issues[0].message.lower()
        )

    def test_empty_file_handling(self, validator: EncodingValidator, tmp_path: Path) -> None:
        """Test that empty file is read but will fail validation later."""
        test_file = tmp_path / "empty.md"
        test_file.write_text("", encoding="utf-8")

        file_content, issues = validator.validate_encoding(test_file)

        # Empty file is valid UTF-8, so no encoding errors
        # It will fail at separator validation stage
        assert file_content == ""
        assert len(issues) == 0

    def test_utf8_with_bom_handling(self, validator: EncodingValidator, tmp_path: Path) -> None:
        """Test UTF-8 BOM (Byte Order Mark) handling."""
        test_file = tmp_path / "bom.md"
        # UTF-8 BOM: EF BB BF
        content = "name: test\ndescription: Test"
        test_file.write_bytes(b"\xef\xbb\xbf" + content.encode("utf-8"))

        file_content, issues = validator.validate_encoding(test_file)

        # Python should handle BOM transparently with utf-8-sig or accept it
        assert file_content is not None
        # BOM may or may not be stripped depending on implementation
        assert len(issues) == 0

    def test_latin1_encoded_file_triggers_error(
        self, validator: EncodingValidator, tmp_path: Path
    ) -> None:
        """Test that Latin-1 encoded file triggers error when read as UTF-8."""
        test_file = tmp_path / "latin1.md"
        # Write Latin-1 specific bytes that are invalid UTF-8
        # 0xE9 is 'é' in Latin-1 but invalid as standalone UTF-8
        test_file.write_bytes(b"name: test\nCaf\xe9")

        file_content, issues = validator.validate_encoding(test_file)

        # Should trigger encoding error
        assert file_content is None
        assert len(issues) == 1
        assert issues[0].code == ErrorCode.INVALID_ENCODING.value
        assert issues[0].severity == ValidationSeverity.ERROR
