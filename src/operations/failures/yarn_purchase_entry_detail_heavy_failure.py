from src.core.exceptions import (
    NotFoundException,
)
from src.core.result import Failure

YARN_PURCHASE_ENTRY_DETAIL_HEAVY_NOT_FOUND_FAILURE = Failure(
    NotFoundException(
        detail="El detalle del pesaje del movimiento de ingreso de hilado especificado no existe."
    )
)
