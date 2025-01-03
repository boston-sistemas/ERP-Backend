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
        detail="El proveedor especificado no es del servicio de tejeduria."
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
