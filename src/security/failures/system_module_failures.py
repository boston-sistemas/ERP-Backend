from src.core.exceptions import (
    ForbiddenException,
    NotFoundException,
    UnprocessableEntityException,
)
from src.core.result import Failure

SYSTEM_MODULE_NOT_FOUND_FAILURE = Failure(
    NotFoundException(detail="El modulo de sistema especificado no existe.")
)
