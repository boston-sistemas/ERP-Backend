from src.core.exceptions import (
    NotFoundException,
)
from src.core.result import Failure


class ProveedorFailures:
    _PROVEEDOR_NOT_FOUND_ERROR = NotFoundException(detail="Proveedor no encontrado.")

    PROVEEDOR_NOT_FOUND_FAILURE = Failure(_PROVEEDOR_NOT_FOUND_ERROR)
