from src.core.exceptions import (
    DuplicateValueException,
    NotFoundException,
    UnprocessableEntityException,
)
from src.core.result import Failure

YARN_NOT_FOUND_FAILURE = Failure(
    NotFoundException(detail="El hilado especificado no existe.")
)

SPINNING_METHOD_NOT_FOUND_YARN_VALIDATION_FAILURE = Failure(
    NotFoundException(detail="El acabado de hilado especificado no existe.")
)

SPINNING_METHOD_DISABLED_YARN_VALIDATION_FAILURE = Failure(
    UnprocessableEntityException(
        detail="El acabado de hilado especificado está deshabilitado."
    )
)

INVALID_YARN_RECIPE_FAILURE = Failure(
    UnprocessableEntityException(
        detail="Receta inválida: las proporciones deben sumar 100%."
    )
)

DUPLICATE_FIBER_IN_YARN_RECIPE_FAILURE = Failure(
    UnprocessableEntityException(
        detail="Receta inválida: una o más fibras están duplicadas."
    )
)

FIBER_NOT_FOUND_IN_YARN_RECIPE_FAILURE = Failure(
    NotFoundException(
        detail="Receta inválida: una o más fibras especificadas no existen."
    )
)

FIBER_DISABLED_IN_YARN_RECIPE_FAILURE = Failure(
    UnprocessableEntityException(
        detail="Receta inválida: una o más fibras especificadas están deshabilitadas."
    )
)

YARN_ALREADY_EXISTS_FAILURE = Failure(
    DuplicateValueException(detail="El hilado ya está registrado en el sistema.")
)

YARN_COUNT_NULL_VALIDATION_FAILURE = Failure(
    UnprocessableEntityException(detail="El titulo del hilado no puede ser nulo.")
)

YARN_NUMBERING_NULL_VALIDATION_FAILURE = Failure(
    UnprocessableEntityException(
        detail="La unidad de medida del titulo del hilado no puede ser nulo."
    )
)

YARN_RECIPE_NULL_VALIDATION_FAILURE = Failure(
    UnprocessableEntityException(detail="La receta del hilado no puede ser nula.")
)
