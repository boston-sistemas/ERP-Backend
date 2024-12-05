from src.core.exceptions import (
    DuplicateValueException,
    NotFoundException,
    UnprocessableEntityException,
)
from src.core.result import Failure

FIBER_NOT_FOUND_FAILURE = Failure(
    NotFoundException(detail="La fibra especificada no existe.")
)
CATEGORY_NOT_FOUND_FIBER_VALIDATION_FAILURE = Failure(
    NotFoundException(detail="La categoría de fibra especificada no existe.")
)
CATEGORY_NULL_FIBER_VALIDATION_FAILURE = Failure(
    UnprocessableEntityException(detail="La categoría de fibra no puede ser nula.")
)
CATEGORY_DISABLED_FIBER_VALIDATION_FAILURE = Failure(
    UnprocessableEntityException(
        detail="La categoría de fibra especificada está deshabilitada."
    )
)
FIBER_ALREADY_EXISTS_FAILURE = Failure(
    DuplicateValueException(detail="La fibra ya está registrada en el sistema.")
)
