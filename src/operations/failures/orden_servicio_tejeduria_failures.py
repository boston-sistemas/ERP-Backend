from src.core.exceptions import (
    NotFoundException,
)
from src.core.result import Failure


class OrdenServicioTejeduriaFailures:
    _ORDEN_NOT_FOUND_ERROR = NotFoundException(
        detail="Orden de servicio de tejeduría no encontrada."
    )
    _ORDEN_NOT_FOUND_WHEN_UPDATING_MULTIPLE_ORDERS_ERROR = NotFoundException(
        detail="Orden de servicio de tejeduría no encontrada. No se actualizaron las ordenes de servicio."
    )

    ORDEN_NOT_FOUND_FAILURE = Failure(_ORDEN_NOT_FOUND_ERROR)
    ORDEN_NOT_FOUND_WHEN_UPDATING_MULTIPLE_ORDERS_FAILURE = Failure(
        _ORDEN_NOT_FOUND_WHEN_UPDATING_MULTIPLE_ORDERS_ERROR
    )
