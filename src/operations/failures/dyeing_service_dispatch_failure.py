from src.core.exceptions import (
    ForbiddenException,
    NotFoundException,
)
from src.core.result import Failure

DYEING_SERVICE_DISPATCH_NOT_FOUND_FAILURE = Failure(
    NotFoundException(
        detail="El movimiento de salida por servicio de tintorería especificado no existe."
    )
)

DYEING_SERVICE_DISPATCH_NOT_ASSOCIATED_SUPPLIER_FAILURE = Failure(
    ForbiddenException(
        detail="El proveedor especificado no es del servicio de tintorería."
    )
)

DYEING_SERVICE_DISPATCH_NOT_ASSOCIATED_SUPPLIER_STORAGE_FAILURE = Failure(
    ForbiddenException(
        detail="El proveedor especificado no tiene almacen asociado."
    )
)

DYEING_SERVICE_DISPATCH_SUPPLIER_NOT_ASSOCIATED_ADDRESS_FAILURE = Failure(
    ForbiddenException(
        detail="El proveedor especificado no tiene dirección asociada."
    )
)

DYEING_SERVICE_DISPATCH_SUPPLIER_NOT_ASSOCIATED_COLOR_ID_FAILURE = Failure(
    ForbiddenException(
        detail="El proveedor especificado no tiene el color especificado."
    )
)

DYEING_SERVICE_DISPATCH_CARD_OPERATION_ALREADY_ASSOCIATED_FAILURE = Failure(
    ForbiddenException(
        detail="La tarjeta especificada ya está asociada a otro movimiento de salida por servicio de tintorería."
    )
)

DYEING_SERVICE_DISPATCH_CARD_OPERATION_ANULLED_FAILURE = Failure(
    ForbiddenException(
        detail="La tarjeta especificada ha sido anulada."
    )
)

DYEING_SERVICE_DISPATCH_CARD_OPERATION_NOT_ASSOCIATED_SUPPLIER_FAILURE = Failure(
    ForbiddenException(
        detail="La tarjeta especificada no es del proveedor especificado."
    )
)

DYEING_SERVICE_DISPATCH_ANULLED_FAILURE = Failure(
    ForbiddenException(
        detail="El movimiento de salida por servicio de tintorería ha sido anulado."
    )
)

DYEING_SERVICE_DISPATCH_ALREADY_ACCOUNTED_FAILURE = Failure(
    ForbiddenException(
        detail="El movimiento de salida por servicio de tintorería ya ha sido contabilizado."
    )
)
