from src.core.exceptions import (
    NotFoundException,
)
from src.core.result import Failure


def SERIES_NOT_FOUND_FAILURE(series_name: str = ""):
    detail = "La serie especificada no existe"
    if not series_name:
        detail = f"La serie de {series_name} no existe."

    return Failure(NotFoundException(detail=detail))
