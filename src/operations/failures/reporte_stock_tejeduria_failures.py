from src.core.exceptions import (
    NotFoundException,
)
from src.core.result import Failure


class ReporteStockTejeduriaFailures:
    _SUPPLIER_ID_NOT_FOUND_WHEN_RETRIEVING_ORDENES_TEJEDURIA_ERROR = NotFoundException(
        detail="El usuario no tiene asociado un código de proveedor de tejeduría. No se recuperaron las ordenes de servicio de tejeduría"
    )
    SUPPLIER_ID_NOT_FOUND_WHEN_RETRIEVING_ORDENES_TEJEDURIA_FAILURE = Failure(
        _SUPPLIER_ID_NOT_FOUND_WHEN_RETRIEVING_ORDENES_TEJEDURIA_ERROR
    )
