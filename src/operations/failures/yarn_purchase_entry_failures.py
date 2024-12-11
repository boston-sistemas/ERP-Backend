from src.core.exceptions import (
    DuplicateValueException,
    NotFoundException,
    UnprocessableEntityException,
)

from src.core.result import Failure

YARN_PURCHASE_ENTRY_NOT_FOUND_FAILURE = Failure(
    NotFoundException(detail="El ingreso de compra de hilado especificado no existe.")
)
