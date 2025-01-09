from src.core.exceptions import NotFoundException
from src.core.result import Failure

PRODUCT_INVENTORY_NOT_FOUND_FAILURE = Failure(
    NotFoundException(
        detail="El producto indicado no está registrado en el almacén especificado."
    )
)
