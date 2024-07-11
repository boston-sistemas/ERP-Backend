from src.core.exceptions import (
    NotFoundException,
)
from src.core.result import Failure


class AccesoFailures:
    _ACCESO_NOT_FOUND_ERROR = NotFoundException(detail="Acceso no encontrado.")

    ACCESO_NOT_FOUND_FAILURE = Failure(_ACCESO_NOT_FOUND_ERROR)
