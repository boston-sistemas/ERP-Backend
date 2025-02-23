from src.core.exceptions import ForbiddenException, NotFoundException
from src.core.result import Failure


class AccesoFailures:
    _ACCESO_NOT_FOUND_ERROR = NotFoundException(detail="Acceso no encontrado.")

    ACCESO_NOT_FOUND_FAILURE = Failure(_ACCESO_NOT_FOUND_ERROR)

    ACCESS_SYSTEM_MODULE_ANULLED_FAILURE = Failure(
        ForbiddenException(detail="El modulo de sistema especificado fue anulado.")
    )
