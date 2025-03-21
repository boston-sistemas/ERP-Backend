from src.core.exceptions import (
    ForbiddenException,
    NotFoundException,
)
from src.core.result import Failure

WEAVING_SERVICE_ENTRY_NOT_FOUND_FAILURE = Failure(
    NotFoundException(
        detail="El movimiento de ingreso por servicio de tejeduría especificado no existe."
    )
)

WEAVING_SERVICE_ENTRY_CARD_OPERATION_ALREADY_DISPATCHED_FAILURE = Failure(
    ForbiddenException(
        detail="Una o más tarjeta(s) asociada(s) al movimiento de ingreso por servicio de tejeduría ya ha(n) sido despachada(s)."
    )
)

WEAVING_SERVICE_ENTRY_SUPPLIER_NOT_ASSOCIATED_FAILURE = Failure(
    ForbiddenException(
        detail="El proveedor especificado no ofrece el servicio de tejeduría."
    )
)

WEAVING_SERVICE_ENTRY_SUPPLIER_WITHOUT_STORAGE_FAILURE = Failure(
    ForbiddenException(detail="El proveedor especificado no tiene almacén asociado.")
)

WEAVING_SERVICE_ENTRY_FABRIC_NOT_FOUND_FAILURE = Failure(
    NotFoundException(
        detail="La orden de servicio de tejeduría no contiene el tejido especificado."
    )
)

WEAVING_SERVICE_ENTRY_FABRIC_RATE_MISSING_FAILURE = Failure(
    ForbiddenException(detail="El tejido especificado no tiene una tarifa asociada.")
)

WEAVING_SERVICE_ENTRY_FABRIC_TINTORERIA_RATE_MISSING_FAILURE = Failure(
    ForbiddenException(
        detail="El tejido especificado no tiene una tarifa de tintorería asociada."
    )
)

WEAVING_SERVICE_ENTRY_SUPPLIER_COLOR_NOT_FOUND_FAILURE = Failure(
    NotFoundException(detail="El proveedor no tiene el color especificado.")
)

WEAVING_SERVICE_ENTRY_ALREADY_QUANTITY_RECEIVED_FAILURE = Failure(
    ForbiddenException(
        detail="La cantidad total ordenada en la O/S de Tejeduría ya ha sido completamente recibida."
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
        detail="La cantidad total ordenada del tejido especificado en la O/S ya ha sido completamente recibida."
    )
)

WEAVING_SERVICE_ENTRY_FABRIC_ALREADY_ANULLED_FAILURE = Failure(
    ForbiddenException(
        detail="El tejido especificado de la orden de servicio ha sido anulado."
    )
)

WEAVING_SERVICE_ENTRY_SERVICE_ORDER_ANULLED_FAILURE = Failure(
    ForbiddenException(detail="La O/S de Tejeduría asociada ha sido anulada.")
)

WEAVING_SERVICE_ENTRY_SERVICE_ORDER_NOT_STARTED_FAILURE = Failure(
    ForbiddenException(detail="La O/S de Tejeduría asociada no ha sido iniciada.")
)

WEAVING_SERVICE_ENTRY_SERVICE_ORDER_NOT_SUPPLIED_YARNS_FAILURE = Failure(
    ForbiddenException(
        detail="La O/S de Tejeduría asociada no tiene hilados asociados."
    )
)

WEAVING_SERVICE_ENTRY_SERVICE_ORDER_NOT_SUPPLIED_FABRIC_YARNS_FAILURE = Failure(
    ForbiddenException(
        detail="La O/S de Tejeduría no tiene hilados asociados para el tejido indicado."
    )
)

WEAVING_SERVICE_ENTRY_SUPPLIER_NOT_ASSOCIATED_TO_DYEING_FAILURE = Failure(
    ForbiddenException(
        detail="El proveedor especificado no ofrece el servicio de tintorería."
    )  # TODO: This failure is repetead
)


class WeavingServiceEntryFailures:
    WEAVING_SERVICE_ENTRY_SERVICE_ORDER_CANCELLED_FAILURE = Failure(
        ForbiddenException(detail="La O/S de Tejeduría asociada ha sido cancelada.")
    )

    WEAVING_SERVICE_ENTRY_CARD_NOT_FOUND_FAILURE = Failure(
        NotFoundException(
            detail="La tarjeta de tejeduría especificada no existe o no pertenece al ingreso"
        )
    )

    WEAVING_SERVICE_ENTRY_REGENERATE_CARDS_FAILURE = Failure(
        ForbiddenException(
            detail="No puede volver a generar las tarjetas, habiendo ya tarjetas generadas."
        )
    )
