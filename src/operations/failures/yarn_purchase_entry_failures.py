from src.core.exceptions import (
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

YARN_PURCHASE_ENTRY_YARN_NOT_FOUND_FAILURE = Failure(
    NotFoundException(detail="La ordén de compra no contiene el hilado especificado.")
)
