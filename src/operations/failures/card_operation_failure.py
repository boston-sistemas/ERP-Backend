from src.core.exceptions import (
    NotFoundException,
)
from src.core.result import Failure

CARD_OPERATION_NOT_FOUND_FAILURE = Failure(
    NotFoundException(detail="La tarjeta especificada no existe.")
)
