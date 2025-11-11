"""Tests for formatting utilities."""

from datetime import UTC, datetime, timedelta

from prompt_manager.utils.formatting import format_timestamp


class TestTimestampFormatting:
    """Tests for human-readable timestamp formatting."""

    def test_format_timestamp_just_now(self) -> None:
        """Test timestamp formatting for very recent time (< 1 minute)."""
        # Create timestamp from 30 seconds ago
        now = datetime.now(UTC)
        recent = now - timedelta(seconds=30)
        iso_timestamp = recent.isoformat()

        result = format_timestamp(iso_timestamp)
        assert result == "just now"

    def test_format_timestamp_minutes_ago(self) -> None:
        """Test timestamp formatting for recent minutes."""
        # Create timestamp from 5 minutes ago
        now = datetime.now(UTC)
        recent = now - timedelta(minutes=5)
        iso_timestamp = recent.isoformat()

        result = format_timestamp(iso_timestamp)
        assert result == "5 minutes ago"

    def test_format_timestamp_one_minute_ago(self) -> None:
        """Test timestamp formatting for exactly 1 minute (singular)."""
        now = datetime.now(UTC)
        recent = now - timedelta(minutes=1)
        iso_timestamp = recent.isoformat()

        result = format_timestamp(iso_timestamp)
        assert result == "1 minute ago"

    def test_format_timestamp_hours_ago(self) -> None:
        """Test timestamp formatting for recent hours."""
        now = datetime.now(UTC)
        recent = now - timedelta(hours=3)
        iso_timestamp = recent.isoformat()

        result = format_timestamp(iso_timestamp)
        assert result == "3 hours ago"

    def test_format_timestamp_one_hour_ago(self) -> None:
        """Test timestamp formatting for exactly 1 hour (singular)."""
        now = datetime.now(UTC)
        recent = now - timedelta(hours=1)
        iso_timestamp = recent.isoformat()

        result = format_timestamp(iso_timestamp)
        assert result == "1 hour ago"

    def test_format_timestamp_days_ago(self) -> None:
        """Test timestamp formatting for recent days."""
        now = datetime.now(UTC)
        recent = now - timedelta(days=3)
        iso_timestamp = recent.isoformat()

        result = format_timestamp(iso_timestamp)
        assert result == "3 days ago"

    def test_format_timestamp_one_day_ago(self) -> None:
        """Test timestamp formatting for exactly 1 day (singular)."""
        now = datetime.now(UTC)
        recent = now - timedelta(days=1)
        iso_timestamp = recent.isoformat()

        result = format_timestamp(iso_timestamp)
        assert result == "1 day ago"

    def test_format_timestamp_weeks_ago(self) -> None:
        """Test timestamp formatting for recent weeks."""
        now = datetime.now(UTC)
        recent = now - timedelta(weeks=2)
        iso_timestamp = recent.isoformat()

        result = format_timestamp(iso_timestamp)
        assert result == "2 weeks ago"

    def test_format_timestamp_months_ago(self) -> None:
        """Test timestamp formatting for recent months."""
        now = datetime.now(UTC)
        recent = now - timedelta(days=60)  # ~2 months
        iso_timestamp = recent.isoformat()

        result = format_timestamp(iso_timestamp)
        assert result == "2 months ago"

    def test_format_timestamp_old_absolute_format(self) -> None:
        """Test timestamp formatting for old dates (> 1 year)."""
        # Create timestamp from over 1 year ago
        old_date = datetime(2023, 1, 15, 10, 30, 0, tzinfo=UTC)
        iso_timestamp = old_date.isoformat()

        result = format_timestamp(iso_timestamp)
        assert result == "2023-01-15 10:30:00"

    def test_format_timestamp_with_z_suffix(self) -> None:
        """Test timestamp formatting with 'Z' suffix (Zulu time)."""
        now = datetime.now(UTC)
        recent = now - timedelta(hours=2)
        iso_timestamp = recent.isoformat().replace("+00:00", "Z")

        result = format_timestamp(iso_timestamp)
        assert result == "2 hours ago"

    def test_format_timestamp_invalid_format_returns_original(self) -> None:
        """Test that invalid timestamp format returns original string."""
        invalid_timestamp = "not-a-valid-timestamp"

        result = format_timestamp(invalid_timestamp)
        assert result == invalid_timestamp

    def test_format_timestamp_empty_string_returns_original(self) -> None:
        """Test that empty string returns as-is."""
        result = format_timestamp("")
        assert result == ""
