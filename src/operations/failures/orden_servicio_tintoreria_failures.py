from src.core.exceptions import (
    NotFoundException,
)
from src.core.result import Failure


class OrdenServicioTintoreriaFailures:
    _COLOR_NOT_FOUND_WHEN_CREATING_MULTIPLE_ORDERS_ERROR = NotFoundException(
        detail="Color no encontrado. No se crearon las ordenes de servicio de tintoreria."
    )

    COLOR_NOT_FOUND_WHEN_CREATING_MULTIPLE_ORDERS_FAILURE = Failure(
        _COLOR_NOT_FOUND_WHEN_CREATING_MULTIPLE_ORDERS_ERROR
    )
