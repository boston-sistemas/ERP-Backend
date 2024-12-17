from src.core.exceptions import (
    DuplicateValueException,
    NotFoundException,
    UnprocessableEntityException,
)
from src.core.result import Failure

FABRIC_NOT_FOUND_FAILURE = Failure(
    NotFoundException(detail="El tejido especificado no existe.")
)


FABRIC_TYPE_NOT_FOUND_FABRIC_VALIDATION_FAILURE = Failure(
    NotFoundException(detail="El tipo de tejido especificado no existe.")
)

FABRIC_TYPE_DISABLED_FABRIC_VALIDATION_FAILURE = Failure(
    UnprocessableEntityException(
        detail="El tipo de tejido especificado está deshabilitado."
    )
)

INVALID_FABRIC_RECIPE_FAILURE = Failure(
    UnprocessableEntityException(
        detail="Receta inválida: las proporciones deben sumar 100%."
    )
)

DUPLICATE_YARN_IN_FABRIC_RECIPE_FAILURE = Failure(
    UnprocessableEntityException(
        detail="Receta inválida: una o más fibras están duplicadas."
    )
)

YARN_NOT_FOUND_IN_FABRIC_RECIPE_FAILURE = Failure(
    NotFoundException(
        detail="Receta inválida: uno o más hilados especificados no existen."
    )
)

YARN_DISABLED_IN_FABRIC_RECIPE_FAILURE = Failure(
    UnprocessableEntityException(
        detail="Receta inválida: uno o más hilados especificados están deshabilitados."
    )
)

FABRIC_ALREADY_EXISTS_FAILURE = Failure(
    DuplicateValueException(detail="El tejido ya está registrado en el sistema.")
)
