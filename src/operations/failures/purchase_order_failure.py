from src.core.exceptions import ForbiddenException, NotFoundException
from src.core.result import Failure

YARN_PURCHASE_ORDER_NOT_FOUND_FAILURE = Failure(
    NotFoundException(detail="La Orden de Compra de hilado especificada no existe.")
)

YARN_PURCHASE_ORDER_ANULLED_FAILURE = Failure(
    ForbiddenException(detail="La Orden de Compra de hilado ha sido anulada.")
)
