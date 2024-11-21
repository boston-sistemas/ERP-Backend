from src.core.exceptions import NotFoundException
from src.core.result import Failure

FIBER_NOT_FOUND_FAILURE = Failure(NotFoundException(detail="Fibra no encontrada."))
