from src.core.exceptions import NotFoundException
from src.core.result import Failure

PRODUCT_INVENTORY_NOT_FOUND_FAILURE = Failure(
    NotFoundException(
        detail="El producto especificado no esta registrado en almacen especificado."
    )
)
