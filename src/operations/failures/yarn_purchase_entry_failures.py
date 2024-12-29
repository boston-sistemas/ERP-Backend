from src.core.exceptions import (
    CustomException,
    ForbiddenException,
    NotFoundException,
    UnprocessableEntityException,
)
from src.core.result import Failure

YARN_PURCHASE_ENTRY_NOT_FOUND_FAILURE = Failure(
    NotFoundException(
        detail="El movimiento de ingreso de compra de hilado especificado no existe."
    )
)

YARN_PURCHASE_ENTRY_CONE_COUNT_MISMATCH_FAILURE = Failure(
    UnprocessableEntityException(
        detail="El número total de conos especificado no coincide con la cantidad de conos de la guía."
    )
)

YARN_PURCHASE_ENTRY_PACKAGE_COUNT_MISMATCH_FAILURE = Failure(
    UnprocessableEntityException(
        detail="El número total de paquetes especificado no coincide con la cantidad de paquetes de la guía."
    )
)

YARN_PURCHASE_ENTRY_UPDATE_INVENTORY_FAILURE = Failure(
    CustomException(detail="No se pudo actualizar el inventario de los hilados.")
)


YARN_PURCHASE_ENTRY_YARN_NOT_FOUND_FAILURE = Failure(
    NotFoundException(detail="La orden de compra no contiene el hilado especificado.")
)

YARN_PURCHASE_ENTRY_ALREADY_ACCOUNTED_FAILURE = Failure(
    ForbiddenException(
        detail="El movimiento de ingreso de compra de hilado ya ha sido contabilizado."
    )
)

YARN_PURCHASE_ENTRY_ALREADY_ANULLED_FAILURE = Failure(
    ForbiddenException(
        detail="El movimiento de ingreso de compra de hilado ya ha sido anulado."
    )
)

YARN_PURCHASE_ENTRY_HAS_MOVEMENT_FAILURE = Failure(
    ForbiddenException(
        detail="El movimiento de ingreso de compra de hilado ya tiene un movimiento asociado."
    )
)

YARN_PURCHASE_ENTRY_ALREADY_QUANTITY_RECEIVED_FAILURE = Failure(
    ForbiddenException(
        detail="Toda la cantidad ordenada de la orden de compra asociada ya ha sido recibida."
    )
)

YARN_PURCHASE_ENTRY_YARN_ALREADY_QUANTITY_RECEIVED_FAILURE = Failure(
    ForbiddenException(
        detail="La cantidad especificada de uno o más hilados indicados ya ha sido recibida."
    )
)
