from src.core.exceptions import NotFoundException
from src.core.result import Failure

RAW_FABRIC_NOT_FOUND_FAILURE = Failure(
    NotFoundException(detail="El tejido crudo especificado no existe.")
)
