from src.core.exceptions import (
    BadRequestException,
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
        detail="La categoría de fibra especificada está inactiva."
    )
)
DENOMINATION_NOT_FOUND_FIBER_VALIDATION_FAILURE = Failure(
    NotFoundException(detail="La Variedad/Marca especificada no existe.")
)
DENOMINATION_DISABLED_FIBER_VALIDATION_FAILURE = Failure(
    NotFoundException(detail="La Variedad/Marca especificada está inactiva.")
)
FIBER_ALREADY_EXISTS_FAILURE = Failure(
    DuplicateValueException(detail="La fibra ya está registrada en el sistema.")
)
FIBER_UPDATE_FAILURE_DUE_TO_YARN_RECIPE_IN_USE = Failure(
    BadRequestException(
        detail="La fibra está siendo utilizada en al menos una receta de hilado."
    )
)
FIBER_DISABLED_FAILURE = Failure(
    BadRequestException(detail="La fibra especificada está inactiva.")
)
