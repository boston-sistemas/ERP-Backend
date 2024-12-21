from src.core.exceptions import (
    NotFoundException,
)
from src.core.result import Failure

PURCHASE_ORDER_DETAIL_NOT_FOUND_FAILURE = Failure(
    NotFoundException(detail="Detalle de orden de compra no encontrado.")
)

