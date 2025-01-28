from src.core.exceptions import (
    ForbiddenException,
    NotFoundException,
    UnprocessableEntityException,
)
from src.core.result import Failure

YARN_WEAVING_DISPATCH_NOT_FOUND_FAILURE = Failure(
    NotFoundException(
        detail="El movimiento de salida de hilado por O/S de Tejeduria especificado no existe."
    )
)

YARN_WEAVING_DISPATCH_SUPPLIER_WITHOUT_STORAGE_FAILURE = Failure(
    UnprocessableEntityException(
        detail="El proveedor especificado no tiene almacen asociado."
    )
)

YARN_WEAVING_DISPATCH_SUPPLIER_NOT_ASSOCIATED_FAILURE = Failure(
    ForbiddenException(
        detail="El proveedor especificado no ofrece el servicio de tejeduria."
    )
)  # TODO: This failure is repetead

YARN_WEAVING_DISPATCH_CONE_COUNT_MISMATCH_FAILURE = Failure(
    UnprocessableEntityException(
        detail="El número total de conos especificado no coincide con la cantidad de conos del grupo seleccionado."
    )
)

YARN_WEAVING_DISPATCH_PACKAGE_COUNT_MISMATCH_FAILURE = Failure(
    UnprocessableEntityException(
        detail="El número total de paquetes especificado no coincide con la cantidad de paquetes del grupo seleccionado."
    )
)

YARN_WEAVING_DISPATCH_GROUP_ALREADY_DISPATCHED_FAILURE = Failure(
    ForbiddenException(detail="El grupo seleccionado ya ha sido despachado.")
)

YARN_WEAVING_DISPATCH_GROUP_ANULLED_FAILURE = Failure(
    ForbiddenException(detail="El grupo seleccionado fue anulado.")
)

YARN_WEAVING_DISPATCH_ALREADY_ANULLED_FAILURE = Failure(
    ForbiddenException(
        detail="El movimiento de salida de hilado por O/S de Tejeduria especificado fue anulado."
    )
)

YARN_WEAVING_DISPATCH_ALREADY_ACCOUNTED_FAILURE = Failure(
    ForbiddenException(
        detail="El movimiento de salida de hilado por O/S de Tejeduria especificado ya ha sido contabilizado."
    )
)

YARN_WEAVING_DISPATCH_NOT_ADDRESS_ASSOCIATED_FAILURE = Failure(
    UnprocessableEntityException(
        detail="El proveedor especificado no tiene la dirección indicada de llegada para tejeduria."
    )
)

YARN_WEAVING_DISPATCH_YARN_NOT_ASSOCIATED_FABRIC_FAILURE = Failure(
    ForbiddenException(
        detail="El hilado especificado no pertenece a ningun tejido de la orden de servicio."
    )
)

YARN_WEAVING_DISPATCH_SERVICE_ORDER_ALREADY_CANCELLED_FAILURE = Failure(
    ForbiddenException(detail="La orden de servicio especificada ha sido cancelada.")
)

YARN_WEAVING_DISPATCH_SERVICE_ORDER_ALREADY_FINISHED_FAILURE = Failure(
    ForbiddenException(detail="La orden de servicio especificada ha sido finalizada.")
)

YARN_WEAVING_DISPATCH_FABRIC_NOT_ASSOCIATED_SERVICE_ORDER_FAILURE = Failure(
    ForbiddenException(
        detail="El tejido especificado no pertenece a la orden de servicio."
    )
)
