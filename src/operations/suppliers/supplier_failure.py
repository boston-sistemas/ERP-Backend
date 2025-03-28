from src.core.exceptions import (
    NotFoundException,
)
from src.core.result import Failure


class SupplierFailures:
    SUPPLIER_NOT_FOUND_FAILURE = Failure(
        NotFoundException(detail="El proveedor especificado no existe.")
    )

    SUPPLIER_INACTIVE_FAILURE = Failure(
        NotFoundException(detail="El proveedor especificado se encuentra inactivo.")
    )

    SUPPLIER_SERVICE_NOT_FOUND_FAILURE = Failure(
        NotFoundException(detail="El servicio del proveedor especificado no existe.")
    )
    SUPPLIER_WITH_MECSA_COLOR_ALREADY_EXISTS_FAILURE = Failure(
        NotFoundException(
            detail="El proveedor especificado ya tiene un color Mecsa asociado."
        )
    )
