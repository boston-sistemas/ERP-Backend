from src.core.exceptions import (
    NotFoundException,
)
from src.core.result import Failure

class OrdenCompraFailures:

    _ORDEN_NOT_FOUND_ERROR = NotFoundException(
        detail="Orden de compra no encontrada."
    )

    ORDEN_NOT_FOUND_FAILURE = Failure(_ORDEN_NOT_FOUND_ERROR)
