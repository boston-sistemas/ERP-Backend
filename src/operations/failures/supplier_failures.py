from src.core.exceptions import (
    NotFoundException,
)
from src.core.result import Failure

SUPPLIER_NOT_FOUND_FAILURE = Failure(
    NotFoundException(detail="El proveedor especificado no existe.")
)
