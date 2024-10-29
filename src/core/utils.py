from datetime import UTC, datetime, timedelta

import pytz

PERU_TIMEZONE = pytz.timezone("America/Lima")


def calculate_time(
    minutes: float = 0, hours: float = 0, days: float = 0, timezone=UTC
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

    current_time = datetime.now(timezone).replace(tzinfo=None)
    return current_time + timedelta(minutes=minutes, hours=hours, days=days)
