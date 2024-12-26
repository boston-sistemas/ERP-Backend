from src.core.exceptions import (
    CustomException,
    NotFoundException,
    UnprocessableEntityException,
    ForbiddenException,
)
from src.core.result import Failure

YARN_WEAVING_DISPATCH_NOT_FOUND_FAILURE = Failure(
    NotFoundException(
        detail="El movimiento de salida de hilado a tejeduria especificado no existe."
    )
)

YARN_WEAVING_DISPATCH_SUPPLIER_WITHOUT_STORAGE_FAILURE = Failure(
    UnprocessableEntityException(
        detail="El proveedor especificado no tiene almacen asociado."
    )
)

YARN_WEAVING_DISPATCH_SUPPLIER_NOT_ASSOCIATED_FAILURE = Failure(
    ForbiddenException(
        detail="El proveedor especificado no es del servicio de tejeduria."
    )
)

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
    ForbiddenException(
        detail="El grupo seleccionado ya ha sido despachado."
    )
)

YARN_WEAVING_DISPATCH_GROUP_ANULLED_FAILURE = Failure(
    ForbiddenException(
        detail="El grupo seleccionado fue anulado."
    )
)
