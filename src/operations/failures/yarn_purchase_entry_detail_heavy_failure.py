from src.core.exceptions import (
    CustomException,
    NotFoundException,
    UnprocessableEntityException,
    ForbiddenException,
)
from src.core.result import Failure

YARN_PURCHASE_ENTRY_DETAIL_HEAVY_NOT_FOUND_FAILURE = Failure(
    NotFoundException(
        detail="El detalle del movimiento de ingreso de hilado pesado especificado no existe."
    )
)
