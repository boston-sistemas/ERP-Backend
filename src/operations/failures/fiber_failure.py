from src.core.exceptions import (
    DuplicateValueException,
    NotFoundException,
    UnprocessableEntityException,
)
from src.core.result import Failure

FIBER_NOT_FOUND_FAILURE = Failure(NotFoundException(detail="Fibra no encontrada."))
FIBER_CATEGORY_NOT_FOUND_WHEN_CREATING_FIBER_FAILURE = Failure(
    NotFoundException(detail="Categoría no encontrada. No se pudo crear la fibra.")
)
FIBER_CATEGORY_DISABLED_WHEN_CREATING_FIBER_FAILURE = Failure(
    UnprocessableEntityException(
        detail="La categoría está deshabilitada. No se pudo crear la fibra."
    )
)
COLOR_NOT_FOUND_WHEN_CREATING_FIBER_FAILURE = Failure(
    NotFoundException(detail="Color no encontrado. No se pudo crear la fibra.")
)
COLOR_DISABLED_WHEN_CREATING_FIBER_FAILURE = Failure(
    UnprocessableEntityException(
        detail="El color está deshabilitado. No se pudo crear la fibra."
    )
)
FIBER_ALREADY_EXISTS_FAILURE = Failure(
    DuplicateValueException(detail="La fibra ya está registrada en el sistema.")
)
