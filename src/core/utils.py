from datetime import UTC, datetime, timedelta

import pytz

from src.core.constants import ACTIVE_STATUS_PROMEC, INACTIVE_STATUS_PROMEC

PERU_TIMEZONE = pytz.timezone("America/Lima")


def calculate_time(
    minutes: float = 0, hours: float = 0, days: float = 0, tz=UTC
) -> datetime:
    """
    Returns the current UTC time plus the specified minutes and days.

    If no arguments are provided, the function returns the current UTC time.

    Args:
        minutes (float): Minutes to add. Defaults to 0.
        days (float): Days to add. Defaults to 0.

    Returns:
        datetime: The resulting datetime in UTC, without timezone info.
    """

    current_time = datetime.now(tz).replace(tzinfo=None)
    return current_time + timedelta(minutes=minutes, hours=hours, days=days)


def is_active_status(condition: str) -> bool:
    """
    Determines if the condition indicates an active state.
    Args:
        condition: The string value (e.g., "A" for active, "I" for inactive).

    Returns:
        bool: True if the condition is active ("A"), False otherwise.
    """
    return condition == ACTIVE_STATUS_PROMEC


def map_active_status(is_active: bool) -> str:
    """
    Converts a boolean value to the corresponding condition string.
    Args:
        is_active: Boolean indicating the active state.

    Returns:
        str: "A" if active, "I" otherwise.
    """
    return ACTIVE_STATUS_PROMEC if is_active else INACTIVE_STATUS_PROMEC
