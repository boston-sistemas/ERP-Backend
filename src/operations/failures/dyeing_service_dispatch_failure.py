from src.core.exceptions import (
    ForbiddenException,
    NotFoundException,
)
from src.core.result import Failure

DYEING_SERVICE_DISPATCH_NOT_FOUND_FAILURE = Failure(
    NotFoundException(
        detail="El movimiento de salida por servicio de tintorería especificado no existe."
    )
)
