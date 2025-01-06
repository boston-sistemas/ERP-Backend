from src.core.exceptions import (
    NotFoundException,
    ForbiddenException,
)
from src.core.result import Failure

WEAVING_SERVICE_ENTRY_NOT_FOUND_FAILURE = Failure(
    NotFoundException(
        detail="El movimiento de ingreso por servicio de tejeduría especificado no existe."
    )
)

WEAVING_SERVICE_ENTRY_SUPPLIER_NOT_ASSOCIATED_FAILURE = Failure(
    ForbiddenException(
        detail="El proveedor especificado no es del servicio de tejeduría."
    )
)

WEAVING_SERVICE_ENTRY_SUPPLIER_WITHOUT_STORAGE_FAILURE = Failure(
    ForbiddenException(
        detail="El proveedor especificado no tiene almacen asociado."
    )
)

WEAVING_SERVICE_ENTRY_FABRIC_NOT_FOUND_FAILURE = Failure(
    NotFoundException(
        detail="La orden de servicio de tejeduría no contiene el tejido especificada."
    )
)

WEAVING_SERVICE_ENTRY_FABRIC_RATE_MISSING_FAILURE = Failure(
    ForbiddenException(
        detail="El tejido especificado no tiene una tarifa asociada."
    )
)

WEAVING_SERVICE_ENTRY_FABRIC_TINTORERIA_RATE_MISSING_FAILURE = Failure(
    ForbiddenException(
        detail="El tejido especificado no tiene una tarifa de tintorería asociada."
    )
)

WEAVING_SERVICE_ENTRY_SUPPLIER_COLOR_NOT_FOUND_FAILURE = Failure(
    NotFoundException(
        detail="El proveedor no tiene el color especificado."
    )
)

WEAVING_SERVICE_ENTRY_ALREADY_QUANTITY_RECEIVED_FAILURE = Failure(
    ForbiddenException(
        detail="Toda la cantidad ordenada de la orden de servicio de tejeduría asociada ya ha sido recibida."
    )
)

WEAVING_SERVICE_ENTRY_ALREADY_ACCOUNTED_FAILURE = Failure(
    ForbiddenException(
        detail="El movimiento de ingreso por servicio de tejeduría ya ha sido contabilizado."
    )
)

WEAVING_SERVICE_ENTRY_ALREADY_ANULLED_FAILURE = Failure(
    ForbiddenException(
        detail="El movimiento de ingreso por servicio de tejeduría ya ha sido anulado."
    )
)

WEAVING_SERVICE_ENTRY_FABRIC_ALREADY_QUANTITY_RECEIVED_FAILURE = Failure(
    ForbiddenException(
        detail="Toda la cantidad ordenada del tejido especificado de la orden de servicio ya ha sido recibida."
    )
)

WEAVING_SERVICE_ENTRY_FABRIC_ALREADY_ANULLED_FAILURE = Failure(
    ForbiddenException(
        detail="El tejido especificado de la orden de servicio ha sido anulado."
    )
)

WEAVING_SERVICE_ENTRY_SERVICE_ORDER_ANULLED_FAILURE = Failure(
    ForbiddenException(
        detail="La orden de servicio de tejeduría asociada ha sido anulada."
    )
)

WEAVING_SERVICE_ENTRY_SERVICE_ORDER_NOT_STARTED_FAILURE = Failure(
    ForbiddenException(
        detail="La orden de servicio de tejeduría asociada no ha sido iniciada."
    )
)

WEAVING_SERVICE_ENTRY_SERVICE_ORDER_NOT_SUPPLIED_YARNS_FAILURE = Failure(
    ForbiddenException(
        detail="La orden de servicio de tejeduría asociada no tiene hilados asociados."
    )
)

WEAVING_SERVICE_ENTRY_SERVICE_ORDER_NOT_SUPPLIED_FABRIC_YARNS_FAILURE = Failure(
    ForbiddenException(
        detail="La orden de servicio de tejeduría asciada no tiene hilados asociados para el tejido indicado."
    )
)
