from src.core.exceptions import (
    NotFoundException,
    UnprocessableEntityException,
)
from src.core.result import Failure


class SupplierColorFailures:
    SUPPLIER_COLOR_NOT_FOUND_FAILURE = Failure(
        NotFoundException(detail="El color especificado del proveedor no existe.")
    )
    SUPPLIER_COLOR_ALREADY_EXISTS_FAILURE = Failure(
        NotFoundException(detail="El color especificado del proveedor ya existe.")
    )
    SUPPLIER_COLOR_NOT_ACTIVE_FAILURE = Failure(
        UnprocessableEntityException(
            detail="El color del proveedor especificado no se encuentra activo."
        )
    )
