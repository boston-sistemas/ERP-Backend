from src.core.exceptions import NotFoundException
from src.core.result import Failure

FINISHED_FABRIC_NOT_FOUND_FAILURE = Failure(
    NotFoundException(detail="El tejido acabado especificado no existe.")
)
