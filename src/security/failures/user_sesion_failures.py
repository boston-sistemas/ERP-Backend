from src.core.exceptions import (
    NotFoundException,
    UnauthorizedException,
)
from src.core.result import Failure


class UserSesionFailures:
    _SESION_NOT_FOUND_ERROR = NotFoundException(detail="Sesión no encontrada.")
    _SESION_EXPIRED_ERROR = UnauthorizedException(detail="La sesión ha expirado.")

    SESION_NOT_FOUND_FAILURE = Failure(_SESION_NOT_FOUND_ERROR)
    SESION_EXPIRED_FAILURE = Failure(_SESION_EXPIRED_ERROR)
