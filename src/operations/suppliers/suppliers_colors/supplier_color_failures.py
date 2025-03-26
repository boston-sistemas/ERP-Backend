from src.core.exceptions import (
    NotFoundException,
)
from src.core.result import Failure


class SupplierColorFailures:
    SUPPLIER_COLOR_NOT_FOUND_FAILURE = Failure(
        NotFoundException(detail="El color especificado del proveedor no existe.")
    )
    SUPPLIER_COLOR_ALREADY_EXISTS_FAILURE = Failure(
        NotFoundException(detail="El color especificado del proveedor ya existe.")
    )
