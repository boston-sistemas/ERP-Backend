from src.core.exceptions import (
    ForbiddenException,
    NotFoundException,
)
from src.core.result import Failure

SERVICE_ORDER_NOT_FOUND_FAILURE = Failure(
    NotFoundException(detail="La orden de servicio especificada no existe.")
)

SERVICE_ORDER_SUPPLIER_NOT_ASSOCIATED_WITH_WEAVING_FAILURE = Failure(
    ForbiddenException(
        detail="El proveedor especificado no ofrece el servicio de tejeduría."
    )
)

SERVICE_ORDER_ALREADY_ANULLED_FAILURE = Failure(
    ForbiddenException(detail="La orden de servicio especificada fue anulada.")
)

SERVICE_ORDER_ALREADY_SUPPLIED_FAILURE = Failure(
    ForbiddenException(
        detail="La orden de servicio especificada ya ha sido abastecida."
    )
)

SERVICE_ORDER_STATUS_NOT_VALID_FAILURE = Failure(
    ForbiddenException(detail="El estado de la O/S indicado no es válido.")
)
