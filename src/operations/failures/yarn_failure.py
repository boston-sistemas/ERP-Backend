from src.core.exceptions import (
    BadRequestException,
    DuplicateValueException,
    NotFoundException,
    UnprocessableEntityException,
)
from src.core.result import Failure

YARN_NOT_FOUND_FAILURE = Failure(
    NotFoundException(detail="El hilado especificado no existe.")
)

YARN_DISABLED_FAILURE = Failure(
    NotFoundException(detail="El hilado especificado está inactivo.")
)

SPINNING_METHOD_NOT_FOUND_YARN_VALIDATION_FAILURE = Failure(
    NotFoundException(detail="El acabado de hilado especificado no existe.")
)

SPINNING_METHOD_DISABLED_YARN_VALIDATION_FAILURE = Failure(
    UnprocessableEntityException(
        detail="El acabado de hilado especificado está inactivo."
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
        detail="Receta inválida: una o más fibras especificadas están inactivas."
    )
)

YARN_ALREADY_EXISTS_FAILURE = Failure(
    DuplicateValueException(detail="El hilado ya está registrado en el sistema.")
)

YARN_COUNT_NULL_VALIDATION_FAILURE = Failure(
    UnprocessableEntityException(detail="El titulo del hilado no puede ser nulo.")
)

YARN_RECIPE_NULL_VALIDATION_FAILURE = Failure(
    UnprocessableEntityException(detail="La receta del hilado no puede ser nula.")
)

YARN_COUNT_NO_FOUND_FAILURE = Failure(
    NotFoundException("El titulo de hilado especificado no existe.")
)

YARN_COUNT_DISABLED_FAILURE = Failure(
    NotFoundException("El titulo de hilado especificado está inactivo.")
)

YARN_MANUFACTURING_SITE_NO_FOUND_FAILURE = Failure(
    NotFoundException("El lugar de fabricación del hilado especificado no existe.")
)

YARN_MANUFACTURING_SITE_DISABLED_FAILURE = Failure(
    NotFoundException("El lugar de producción del hilado especificado está inactivo.")
)

YARN_UPDATE_FAILURE_DUE_TO_FABRIC_RECIPE_IN_USE = Failure(
    BadRequestException(
        detail="El hilado especificado está siendo utilizado en al menos una receta de tejido."
    )
)

YARN_DISTINCTION_NO_FOUND_FAILURE = Failure(
    NotFoundException("La distinción de hilado especificado no existe.")
)

YARN_DISTINCTION_DISABLED_FAILURE = Failure(
    NotFoundException("La distinción de hilado especificado está inactivo.")
)


def YARN_PARTIAL_UPDATE_FAILURE(reason: str = None):
    detail = "Solo se permite la actualización de la descripción."
    detail = reason + " " + detail if reason else detail
    return Failure(BadRequestException(detail=detail))


YARN_UPDATE_FAILURE_DUE_TO_PURCHASE_ORDER_IN_USE = Failure(
    BadRequestException(
        detail="El hilado especificado está siendo utilizado en al menos una Orden de Compra."
    )
)

YARN_UPDATE_FAILURE_DUE_TO_MOVEMENT_IN_USE = Failure(
    BadRequestException(
        detail="El hilado especificado está siendo utilizado en al menos un Movimiento de Hilado."
    )
)
