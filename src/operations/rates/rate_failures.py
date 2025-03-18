from src.core.exceptions import (
    NotFoundException,
)
from src.core.result import Failure


class RateFailures:
    RATE_NOT_FOUND_FAILURE = Failure(
        NotFoundException(detail="La tarifa especificada no existe.")
    )
    RATE_SERVICE_NOT_FOUND_FAILURE = Failure(
        NotFoundException(
            detail="El servicio de la tarifa no se encuentra en los servicios del proveedor."
        )
    )
    RATE_UPATE_FAILURE = Failure(
        NotFoundException(
            detail="La tarifa especificada no es posible de actualizar ya que registra un movimiento facturado o tiene una orden de servicio en proceso."
        )
    )
