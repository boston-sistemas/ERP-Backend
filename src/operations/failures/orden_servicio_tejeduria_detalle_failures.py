from src.core.exceptions import (
    NotFoundException,
)
from src.core.result import Failure


class OrdenServicioTejeduriaDetalleFailures:
    _SUBORDER_NOT_FOUND = NotFoundException(
        detail="Suborden de servicio de tejeduría no encontrada."
    )
    _SUBORDER_NOT_FOUND_WHEN_UPDATING_MULTIPLE_SUBORDERS_ERROR = NotFoundException(
        detail="Suborden de servicio de tejeduría no encontrada. No se actualizaron las subordenes"
    )

    SUBORDER_NOT_FOUND_FAILURE = Failure(_SUBORDER_NOT_FOUND)
    SUBORDER_NOT_FOUND_WHEN_UPDATING_MULTIPLE_SUBORDERS_FAILURE = Failure(
        _SUBORDER_NOT_FOUND_WHEN_UPDATING_MULTIPLE_SUBORDERS_ERROR
    )
