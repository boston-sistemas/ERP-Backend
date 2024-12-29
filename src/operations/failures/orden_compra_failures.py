from src.core.exceptions import ForbiddenException, NotFoundException
from src.core.result import Failure

PURCHASE_YARN_ORDER_NOT_FOUND_FAILURE = Failure(
    NotFoundException(detail="Orden de compra de hilado no encontrada.")
)

PURCHASE_YARN_ORDER_ANULLED_FAILURE = Failure(
    ForbiddenException(detail="La orden de compra de hilado ha sido anulada.")
)
