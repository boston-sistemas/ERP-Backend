from src.core.exceptions import (
    CustomException,
    ForbiddenException,
    NotFoundException,
    UnprocessableEntityException,
)
from src.core.result import Failure

WEAVING_SERVICE_ENTRY_NOT_FOUND_FAILURE = Failure(
    NotFoundException(
        detail="El movimiento de ingreso por servicio de tejeduría especificado no existe."
    )
)
