"""Formatting utilities for human-readable output.

This module provides utility functions for formatting data in human-readable
formats, including timestamp formatting for relative time display.
"""

from datetime import UTC, datetime, timedelta

# Time thresholds for relative formatting: (max_seconds, divisor, unit_singular, unit_plural)
_TIME_THRESHOLDS = [
    (60, 1, "second", "seconds"),
    (3600, 60, "minute", "minutes"),
    (86400, 3600, "hour", "hours"),
    (604800, 86400, "day", "days"),
    (2592000, 604800, "week", "weeks"),
    (31536000, 2592000, "month", "months"),
]


def _get_relative_time(diff: timedelta) -> str | None:
    """Get relative time string for a time difference.

    Args:
        diff: Time difference to format.

    Returns:
        Relative time string or None if too old.
    """
    total_seconds = diff.total_seconds()

    if total_seconds < 60:
        return "just now"

    for max_seconds, divisor, singular, plural in _TIME_THRESHOLDS[1:]:  # Skip seconds
        if total_seconds < max_seconds:
            value = int(total_seconds / divisor)
            unit = singular if value == 1 else plural
            return f"{value} {unit} ago"

    return None


def format_timestamp(iso_timestamp: str) -> str:
    """Convert ISO 8601 timestamp to human-readable format.

    This function converts ISO 8601 timestamps to relative time strings
    (e.g., "2 hours ago", "3 days ago") for recent timestamps, or absolute
    format for older timestamps.

    Args:
        iso_timestamp: ISO 8601 formatted timestamp string

    Returns:
        Human-readable timestamp string

    Examples:
        >>> # Recent timestamp (assume current time is 2024-11-11 16:30:00 UTC)
        >>> format_timestamp("2024-11-11T14:30:00Z")
        '2 hours ago'

        >>> # Older timestamp
        >>> format_timestamp("2024-10-01T10:00:00Z")
        '2024-10-01 10:00:00'

        >>> # Just now
        >>> format_timestamp("2024-11-11T16:29:30Z")
        'just now'
    """
    try:
        # Parse ISO 8601 timestamp
        # Handle both 'Z' suffix and explicit timezone
        if iso_timestamp.endswith("Z"):
            timestamp = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
        else:
            timestamp = datetime.fromisoformat(iso_timestamp)

        # Get current time in UTC
        now = datetime.now(UTC)

        # Ensure timestamp is timezone-aware
        if timestamp.tzinfo is None:
            # Assume UTC if no timezone
            timestamp = timestamp.replace(tzinfo=UTC)

        # Calculate time difference
        diff = now - timestamp

        # Return relative time for recent timestamps
        relative = _get_relative_time(diff)
        if relative:
            return relative

        # For very old timestamps, return absolute format
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")

    except (ValueError, AttributeError):
        # If parsing fails, return the original string
        return iso_timestamp
