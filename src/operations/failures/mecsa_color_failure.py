from src.core.exceptions import DuplicateValueException, NotFoundException
from src.core.result import Failure

MECSA_COLOR_NOT_FOUND_FAILURE = Failure(
    NotFoundException(detail="Color MECSA no encontrado.")
)


def MECSA_COLOR_NAME_ALREADY_EXISTS_FAILURE(name: str):
    return Failure(
        DuplicateValueException(f"El nombre del color '{name}' ya está en uso")
    )


def MECSA_COLOR_SKU_ALREADY_EXISTS_FAILURE(sku: str):
    return Failure(DuplicateValueException(f"El SKU del color '{sku}' ya está en uso"))
