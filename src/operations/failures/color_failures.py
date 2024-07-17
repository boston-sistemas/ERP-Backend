from src.core.exceptions import (
    NotFoundException,
)
from src.core.result import Failure


class ColorFailures:
    _COLOR_NOT_FOUND_ERROR = NotFoundException(detail="Color no encontrado.")

    COLOR_NOT_FOUND_FAILURE = Failure(_COLOR_NOT_FOUND_ERROR)
