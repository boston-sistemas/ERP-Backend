from datetime import UTC, datetime, timedelta
from typing import Any

import pytz
from pydantic import BaseModel

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


def to_safe_str(value: Any | None) -> str:
    """
    Converts an optional value to a safe string.

    If the value is `None`, returns an empty string. Otherwise, converts it to `str`.

    Args:
        value (int | None): The optional value to convert.

    Returns:
        str: String representation of the value, or an empty string if `None`.
    """
    return str(value) if value is not None else ""


def generate_doc(
    response_model: BaseModel, description: str = "", responses: dict = {}
):
    return {
        "description": description,
        "response_model": response_model,
        **({} if not responses else {"responses": responses}),
    }


def generate_response_doc(
    status_code: int = 200,
    description: str = "Successful Response",
    content: dict = None,
):
    return {
        status_code: {
            "description": description,
            **({} if not content else {"content": content}),
        }
    }


def generate_response_content(type: str = "application/json", examples: dict = {}):
    n = len(examples)
    field = "examples" if n > 1 else "example"
    return {type: {field: examples}}
