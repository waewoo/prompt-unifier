"""Tests for UTF-8 encoding validation logic."""

from pathlib import Path
from unittest.mock import patch

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

    def test_permission_error_handling(self):
        """Test permission error handling."""
        validator = EncodingValidator()

        with patch("pathlib.Path.read_text") as mock_read:
            mock_read.side_effect = PermissionError("Permission denied")

            test_file = Path("/tmp/test.md")
            content, issues = validator.validate_encoding(test_file)

            assert content is None
            assert len(issues) == 1
            assert issues[0].severity == ValidationSeverity.ERROR
            assert issues[0].code == ErrorCode.INVALID_ENCODING.value
            assert "Permission denied" in issues[0].message
            assert "permissions" in issues[0].suggestion.lower()

    def test_os_error_variants(self):
        """Test different OSError variants."""
        validator = EncodingValidator()

        # Test with different types of OSError
        error_types = [
            OSError("Generic OS error"),
            OSError(1, "Operation not permitted"),
            OSError(2, "No such file or directory"),
            OSError(5, "I/O error"),
        ]

        for error in error_types:
            with patch("pathlib.Path.read_text") as mock_read:
                mock_read.side_effect = error

                test_file = Path("/tmp/test.md")
                content, issues = validator.validate_encoding(test_file)

                assert content is None
                assert len(issues) == 1
                assert issues[0].severity == ValidationSeverity.ERROR
                assert issues[0].code == ErrorCode.INVALID_ENCODING.value
                assert (
                    "Error reading file" in issues[0].message
                    or "Permission denied" in issues[0].message
                    or "File not found" in issues[0].message
                    or "does not exist" in issues[0].message
                )

    def test_unicode_decode_error_variants(self):
        """Test different UnicodeDecodeError variants."""
        validator = EncodingValidator()

        # Create different types of decoding errors
        test_cases = [
            # Invalid UTF-8
            b"\xff\xfe\x00\x00invalid utf-8",
            # Incomplete sequence
            b"\xc2",  # UTF-8 incomplete sequence
            # Invalid sequence
            b"\x80\x81",  # Invalid UTF-8 sequence
            # Latin-1 characters invalid in UTF-8
            b"\xe9\x20",  # Latin-1 'é' followed by space
        ]

        for i, invalid_bytes in enumerate(test_cases):
            test_file = Path(f"/tmp/invalid_{i}.md")
            test_file.write_bytes(invalid_bytes)

            content, issues = validator.validate_encoding(test_file)

            assert content is None
            assert len(issues) == 1
            assert issues[0].severity == ValidationSeverity.ERROR
            assert issues[0].code == ErrorCode.INVALID_ENCODING.value
            assert "UTF-8" in issues[0].message

            # Clean up
            if test_file.exists():
                test_file.unlink()

    def test_file_not_found_with_complex_path(self):
        """Test FileNotFoundError with complex paths."""
        validator = EncodingValidator()

        # Complex paths that don't exist
        complex_paths = [
            Path("/tmp/nonexistent/deeply/nested/file.md"),
            Path("/root/nonexistent/file.md"),  # Requires special permissions
            Path("./relative/nonexistent/file.md"),
            Path("~/nonexistent/file.md").expanduser(),
        ]

        for path in complex_paths:
            content, issues = validator.validate_encoding(path)

            assert content is None
            assert len(issues) == 1
            assert issues[0].severity == ValidationSeverity.ERROR
            assert issues[0].code == ErrorCode.INVALID_ENCODING.value
            assert (
                "not found" in issues[0].message.lower()
                or "does not exist" in issues[0].message.lower()
            )

    def test_encoding_with_special_file_names(self):
        """Test encoding with special file names."""
        validator = EncodingValidator()

        # Create files with special names
        special_names = [
            "file with spaces.md",
            "file-with-dashes.md",
            "file_with_underscores.md",
            "file.multiple.dots.md",
            "file(avec)parens.md",
            "file[avec]brackets.md",
            "file{avec}braces.md",
        ]

        for name in special_names:
            test_file = Path(f"/tmp/{name}")
            test_file.write_text("Valid UTF-8 content", encoding="utf-8")

            content, issues = validator.validate_encoding(test_file)

            assert content is not None
            assert len(issues) == 0
            assert "Valid UTF-8 content" in content

            # Clean up
            if test_file.exists():
                test_file.unlink()

    def test_encoding_with_very_long_content(self):
        """Test encoding with very long content."""
        validator = EncodingValidator()

        # Create very long content
        long_content = "Test line\n" * 10000  # 10000 lines

        test_file = Path("/tmp/long_content.md")
        test_file.write_text(long_content, encoding="utf-8")

        content, issues = validator.validate_encoding(test_file)

        assert content is not None
        assert len(issues) == 0
        assert len(content) == len(long_content)
        assert content == long_content

        # Clean up
        if test_file.exists():
            test_file.unlink()

    def test_encoding_with_mixed_line_endings(self):
        """Test encoding with different line ending types."""
        validator = EncodingValidator()

        # Create content with different line ending types
        mixed_content = "Line 1\nLine 2\r\nLine 3\rLine 4\n"

        test_file = Path("/tmp/mixed_lines.md")
        test_file.write_text(mixed_content, encoding="utf-8")

        content, issues = validator.validate_encoding(test_file)

        assert content is not None
        assert len(issues) == 0
        # Python normalizes line endings, so we check normalized content
        normalized_content = content.replace("\r\n", "\n").replace("\r", "\n")
        normalized_mixed = mixed_content.replace("\r\n", "\n").replace("\r", "\n")
        assert normalized_content == normalized_mixed

        # Clean up
        if test_file.exists():
            test_file.unlink()

    def test_encoding_with_unicode_bom_variants(self):
        """Test different BOM (Byte Order Mark) variants."""
        validator = EncodingValidator()

        # Different types of BOM
        bom_types = [
            (b"\xef\xbb\xbf", "UTF-8 BOM"),
            (b"\xff\xfe", "UTF-16 LE BOM"),
            (b"\xfe\xff", "UTF-16 BE BOM"),
            (b"\xff\xfe\x00\x00", "UTF-32 LE BOM"),
            (b"\x00\x00\xfe\xff", "UTF-32 BE BOM"),
        ]

        content = "Test content with BOM"

        for bom_bytes, description in bom_types:
            test_file = Path(f"/tmp/bom_{description.replace(' ', '_').lower()}.md")
            test_file.write_bytes(bom_bytes + content.encode("utf-8"))

            file_content, issues = validator.validate_encoding(test_file)

            # Python should handle UTF-8 BOM correctly
            if bom_bytes == b"\xef\xbb\xbf":
                assert file_content is not None
                assert len(issues) == 0
                assert content in file_content
            else:
                # Other BOMs should cause encoding errors
                assert file_content is None
                assert len(issues) == 1
                assert issues[0].severity == ValidationSeverity.ERROR

            # Clean up
            if test_file.exists():
                test_file.unlink()

    def test_encoding_with_control_characters(self):
        """Test encoding with control characters."""
        validator = EncodingValidator()

        # Valid control characters in UTF-8
        control_chars = [
            "\x00",  # Null character
            "\x01",  # Start of Heading
            "\x02",  # Start of Text
            "\x03",  # End of Text
            "\x04",  # End of Transmission
            "\x05",  # Enquiry
            "\x06",  # Acknowledge
            "\x07",  # Bell
            "\x08",  # Backspace
            "\x0b",  # Vertical Tab
            "\x0c",  # Form Feed
            "\x0e",  # Shift Out
            "\x0f",  # Shift In
            "\x10",  # Data Link Escape
            "\x11",  # Device Control 1
            "\x12",  # Device Control 2
            "\x13",  # Device Control 3
            "\x14",  # Device Control 4
            "\x15",  # Negative Acknowledge
            "\x16",  # Synchronous Idle
            "\x17",  # End of Transmission Block
            "\x18",  # Cancel
            "\x19",  # End of Medium
            "\x1a",  # Substitute
            "\x1b",  # Escape
            "\x1c",  # File Separator
            "\x1d",  # Group Separator
            "\x1e",  # Record Separator
            "\x1f",  # Unit Separator
        ]

        for char in control_chars:
            test_file = Path(f"/tmp/control_{ord(char):02x}.md")
            content_with_control = f"Before{char}After"
            test_file.write_text(content_with_control, encoding="utf-8")

            file_content, issues = validator.validate_encoding(test_file)

            # Control characters are valid in UTF-8
            assert file_content is not None
            assert len(issues) == 0
            assert content_with_control in file_content

            # Clean up
            if test_file.exists():
                test_file.unlink()

    def test_encoding_with_surrogate_pairs(self):
        """Test encoding with Unicode surrogate pairs."""
        validator = EncodingValidator()

        # Characters that require surrogate pairs in UTF-16
        # but are handled correctly in UTF-8
        surrogate_chars = [
            "😀",  # Grinning Face
            "🎉",  # Party Popper
            "💻",  # Personal Computer
            "🚀",  # Rocket
            "🔥",  # Fire
            "💡",  # Light Bulb
            "✅",  # Check Mark Button
            "❌",  # Cross Mark
        ]

        for char in surrogate_chars:
            test_file = Path(f"/tmp/surrogate_{ord(char):x}.md")
            content_with_emoji = f"Text with emoji: {char}"
            test_file.write_text(content_with_emoji, encoding="utf-8")

            file_content, issues = validator.validate_encoding(test_file)

            assert file_content is not None
            assert len(issues) == 0
            assert content_with_emoji in file_content

            # Clean up
            if test_file.exists():
                test_file.unlink()

    def test_encoding_with_invalid_utf8_sequences(self):
        """Test with specific invalid UTF-8 sequences."""
        validator = EncodingValidator()

        # Specific invalid UTF-8 sequences
        invalid_sequences = [
            b"\x80",  # Continuation byte without start
            b"\xbf",  # Continuation byte without start
            b"\xc0\x80",  # Overlong encoding of NULL
            b"\xc1\xbf",  # Overlong encoding
            b"\xe0\x80\x80",  # Overlong encoding of NULL
            b"\xf0\x80\x80\x80",  # Overlong encoding of NULL
            b"\xf8\x80\x80\x80\x80",  # 5-byte sequence (invalid)
            b"\xfc\x80\x80\x80\x80\x80",  # 6-byte sequence (invalid)
            b"\xff",  # Invalid start byte
            b"\xfe",  # Invalid start byte
        ]

        for i, invalid_seq in enumerate(invalid_sequences):
            test_file = Path(f"/tmp/invalid_utf8_{i}.md")
            test_file.write_bytes(invalid_seq)

            content, issues = validator.validate_encoding(test_file)

            assert content is None
            assert len(issues) == 1
            assert issues[0].severity == ValidationSeverity.ERROR
            assert issues[0].code == ErrorCode.INVALID_ENCODING.value
            assert "UTF-8" in issues[0].message

            # Clean up
            if test_file.exists():
                test_file.unlink()

    def test_encoding_with_mixed_encodings(self):
        """Test with files containing mixed encodings."""
        validator = EncodingValidator()

        # Create a file with valid UTF-8 followed by invalid sequences
        test_file = Path("/tmp/mixed_encoding.md")

        # Valid UTF-8
        valid_utf8 = "This is valid UTF-8 text.\n"

        # Invalid UTF-8 sequences
        invalid_utf8 = b"\xff\xfe\x00\x00invalid"

        # Combine
        mixed_content = valid_utf8.encode("utf-8") + invalid_utf8
        test_file.write_bytes(mixed_content)

        content, issues = validator.validate_encoding(test_file)

        # Should fail due to invalid sequences
        assert content is None
        assert len(issues) == 1
        assert issues[0].severity == ValidationSeverity.ERROR
        assert issues[0].code == ErrorCode.INVALID_ENCODING.value

        # Clean up
        if test_file.exists():
            test_file.unlink()

    def test_encoding_with_empty_file_after_bom(self):
        """Test with BOM followed by nothing."""
        validator = EncodingValidator()

        test_file = Path("/tmp/bom_empty.md")
        # UTF-8 BOM alone
        test_file.write_bytes(b"\xef\xbb\xbf")

        content, issues = validator.validate_encoding(test_file)

        # Should succeed, it's valid UTF-8 (BOM + empty content)
        assert content is not None
        assert len(issues) == 0
        # BOM is present but it's valid content
        assert content == "\ufeff"  # BOM alone

        # Clean up
        if test_file.exists():
            test_file.unlink()

    def test_encoding_validator_reuse(self):
        """Test that validator can be reused multiple times."""
        validator = EncodingValidator()

        # Create multiple test files
        test_files = []
        for i in range(5):
            test_file = Path(f"/tmp/reuse_test_{i}.md")
            if i % 2 == 0:
                # Valid files
                test_file.write_text(f"Valid content {i}", encoding="utf-8")
            else:
                # Invalid files
                test_file.write_bytes(b"\xff\xfe\x00invalid")
            test_files.append(test_file)

        # Validate all files
        for i, test_file in enumerate(test_files):
            content, issues = validator.validate_encoding(test_file)

            if i % 2 == 0:
                assert content is not None
                assert len(issues) == 0
                assert f"Valid content {i}" in content
            else:
                assert content is None
                assert len(issues) == 1
                assert issues[0].severity == ValidationSeverity.ERROR

            # Clean up
            if test_file.exists():
                test_file.unlink()

    def test_encoding_with_symlink(self):
        """Test encoding with symbolic links."""
        validator = EncodingValidator()

        # Create a target file
        target_file = Path("/tmp/symlink_target.md")
        target_file.write_text("Target file content", encoding="utf-8")

        # Create a symbolic link
        symlink_file = Path("/tmp/symlink.md")
        if symlink_file.exists() or symlink_file.is_symlink():
            symlink_file.unlink()
        symlink_file.symlink_to(target_file)

        content, issues = validator.validate_encoding(symlink_file)

        # Should read target file content
        assert content is not None
        assert len(issues) == 0
        assert "Target file content" in content

        # Clean up
        if symlink_file.exists() or symlink_file.is_symlink():
            symlink_file.unlink()
        if target_file.exists():
            target_file.unlink()

    def test_encoding_with_binary_file(self):
        """Test encoding with binary file."""
        validator = EncodingValidator()

        # Create a binary file
        test_file = Path("/tmp/binary_file.md")
        binary_data = bytes(range(256))  # All bytes from 0 to 255
        test_file.write_bytes(binary_data)

        content, issues = validator.validate_encoding(test_file)

        # Should fail because it's not valid UTF-8 text
        assert content is None
        assert len(issues) == 1
        assert issues[0].severity == ValidationSeverity.ERROR
        assert issues[0].code == ErrorCode.INVALID_ENCODING.value

        # Clean up
        if test_file.exists():
            test_file.unlink()

    def test_file_not_found_handling(self, tmp_path: Path):
        """Test that non-existent files are handled correctly."""
        validator = EncodingValidator()
        non_existent_file = tmp_path / "does_not_exist.md"

        content, issues = validator.validate_encoding(non_existent_file)

        assert content is None
        assert len(issues) == 1
        assert issues[0].severity == ValidationSeverity.ERROR
        assert issues[0].code == ErrorCode.INVALID_ENCODING.value

    def test_empty_file_is_valid_utf8(self, validator: EncodingValidator, tmp_path: Path):
        """Test that empty file is considered valid UTF-8."""
        empty_file = tmp_path / "empty.md"
        empty_file.write_text("", encoding="utf-8")

        content, issues = validator.validate_encoding(empty_file)

        assert content == ""
        assert len(issues) == 0

    def test_valid_utf8_with_special_characters(self, validator: EncodingValidator, tmp_path: Path):
        """Test that file with special UTF-8 characters is valid."""
        test_file = tmp_path / "special.md"

        # Content with special UTF-8 characters
        content_with_special = "Test with emojis: 🎉🚀 and accents: éàêçù"
        test_file.write_text(content_with_special, encoding="utf-8")

        content, issues = validator.validate_encoding(test_file)

        assert content is not None
        assert len(issues) == 0
        assert "emojis: 🎉🚀" in content

    def test_invalid_utf8_bytes_trigger_error_simple(
        self, validator: EncodingValidator, tmp_path: Path
    ):
        """Test that invalid UTF-8 bytes trigger an error."""
        invalid_file = tmp_path / "invalid.md"

        # Write invalid UTF-8 bytes
        invalid_bytes = b"Valid text\n\xff\xfe\x00\x00Invalid UTF-8"
        invalid_file.write_bytes(invalid_bytes)

        content, issues = validator.validate_encoding(invalid_file)

        assert content is None
        assert len(issues) == 1
        assert issues[0].severity == ValidationSeverity.ERROR
        assert issues[0].code == ErrorCode.INVALID_ENCODING.value
