from src.core.exceptions import DuplicateValueException, NotFoundException
from src.core.result import Failure

PARAMETER_CATEGORY_NOT_FOUND_FAILURE = Failure(
    NotFoundException(detail="Categoría de parámetro no encontrado")
)


def PARAMETER_CATEGORY_NAME_ALREADY_EXISTS(name: str):
    return Failure(
        DuplicateValueException(
            f"El nombre de la categoría de parámetro '{name}' está en uso"
        )
    )
