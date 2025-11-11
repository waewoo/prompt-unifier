"""Formatting utilities for human-readable output.

This module provides utility functions for formatting data in human-readable
formats, including timestamp formatting for relative time display.
"""

from datetime import UTC, datetime


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
        if diff.total_seconds() < 60:
            return "just now"
        if diff.total_seconds() < 3600:  # Less than 1 hour
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        if diff.total_seconds() < 86400:  # Less than 1 day
            hours = int(diff.total_seconds() / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        if diff.days < 7:  # Less than 1 week
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        if diff.days < 30:  # Less than 1 month
            weeks = diff.days // 7
            return f"{weeks} week{'s' if weeks != 1 else ''} ago"
        if diff.days < 365:  # Less than 1 year
            months = diff.days // 30
            return f"{months} month{'s' if months != 1 else ''} ago"

        # For very old timestamps, return absolute format
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")

    except (ValueError, AttributeError):
        # If parsing fails, return the original string
        return iso_timestamp
