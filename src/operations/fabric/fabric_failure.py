from src.core.exceptions import NotFoundException
from src.core.result import Failure

FABRIC_NOT_FOUND_FAILURE = Failure(
    NotFoundException(detail="El tejido especificado no existe.")
)
