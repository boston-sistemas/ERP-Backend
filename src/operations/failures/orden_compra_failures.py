from src.core.exceptions import (
    NotFoundException,
)
from src.core.result import Failure

PURCHASE_YARN_ORDER_NOT_FOUND_FAILURE = Failure(
    NotFoundException(detail="Orden de compra de hilado no encontrada.")
)
