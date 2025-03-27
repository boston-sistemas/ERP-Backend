from datetime import UTC, datetime, timedelta
from typing import Any

import pytz
from pydantic import BaseModel

from src.core.constants import ACTIVE_STATUS_PROMEC, INACTIVE_STATUS_PROMEC

PERU_TIMEZONE = pytz.timezone("America/Lima")

import re

import unidecode
import webcolors
from deep_translator import GoogleTranslator


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


HEX_COLOR_REGEX = re.compile(r"^#(?:[0-9a-fA-F]{3}){1,2}$")


def is_valid_hexadecimal(hexadecimal: str) -> bool:
    """
    Checks if the hexadecimal color is valid.

    Args:
        hexadecimal (str): The hexadecimal color code.

    Returns:
        bool: True if the hexadecimal color is valid, False otherwise.
    """
    return bool(HEX_COLOR_REGEX.fullmatch(hexadecimal))


def generate_color_name(hex_color: str) -> str:
    """
    Generates a color name from the hexadecimal color code.

    Args:
        hex_color (str): The hexadecimal color code.

    Returns:
        str: The name of the color.
    """
    color_name = webcolors.hex_to_name(hex_color)

    color_name = GoogleTranslator(source="en", target="es").translate(color_name)
    return color_name


def generate_sku(color_name: str) -> str:
    """
    Generates a SKU from the color name.

    Args:
        color_name (str): The name of the color.

    Returns:
        str: The SKU.
    """
    name = unidecode.unidecode(color_name.strip().upper())
    words = name.split()

    if len(words) == 1:
        return words[0][:4]

    return "".join(word[0] for word in words)[:4]
