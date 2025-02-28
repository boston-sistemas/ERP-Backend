from src.core.exceptions import NotFoundException
from src.core.result import Failure


class OperationFailures:
    OPERATION_NOT_FOUND_FAILURE = Failure(
        NotFoundException(detail="La operación especificada no existe.")
    )

    OPERATION_NOT_FOUND_WHEN_ADDING_FAILURE = Failure(
        NotFoundException(
            detail="La operación no existe. No se añadieron las operaciones especificadas."
        )
    )
