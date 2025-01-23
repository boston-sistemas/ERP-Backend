from src.core.exceptions import (
    DuplicateValueException,
    NotFoundException,
    UnprocessableEntityException,
)
from src.core.result import Failure

MECSA_COLOR_NOT_FOUND_FAILURE = Failure(
    NotFoundException(detail="El color especificado no existe.")
)


def MECSA_COLOR_NAME_ALREADY_EXISTS_FAILURE(name: str | None = None):
    name = f" {name} " if name else " "
    return Failure(
        DuplicateValueException(
            f"El nombre'{name}'ya está en uso por otro color. Por favor, ingrese un nombre diferente."
        )
    )


def MECSA_COLOR_SKU_ALREADY_EXISTS_FAILURE(sku: str):
    return Failure(
        DuplicateValueException(
            f"El SKU '{sku}' ya está en uso por otro color. Por favor, ingrese un SKU diferente."
        )
    )


MECSA_COLOR_DISABLED_FAILURE = Failure(
    UnprocessableEntityException(detail="El color especificado está inactivo.")
)
