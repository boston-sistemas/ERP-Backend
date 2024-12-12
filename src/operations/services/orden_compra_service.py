from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.operations.failures import PURCHASE_YARN_ORDER_NOT_FOUND_FAILURE
from src.operations.models import OrdenCompra
from src.operations.repositories import OrdenCompraRepository
from src.operations.schemas import OrdenCompraWithDetallesSchema


class OrdenCompraService:
    def __init__(self, db: AsyncSession) -> None:
        self.repository = OrdenCompraRepository(db)

    async def read_purchase_yarn_orders(
        self,
        include_detalle: bool = False,
    ) -> list[OrdenCompra]:
        return await self.repository.find_ordenes_yarn(include_detalle=include_detalle)

    async def _read_purchase_yarn_order(
        self,
        purchase_order_number: str,
        include_detalle: bool = False,
    ) -> Result[OrdenCompra, CustomException]:
        orden = await self.repository.find_yarn_order_by_purchase_order_number(
            purchase_order_number=purchase_order_number, include_detalle=include_detalle
        )

        if orden is None:
            return PURCHASE_YARN_ORDER_NOT_FOUND_FAILURE

        return Success(orden)

    async def read_purchase_yarn_order(
        self,
        purchase_order_number: str,
        include_detalle: bool = False,
    ) -> OrdenCompra | None:
        purchase_yarn_order_result = await self._read_purchase_yarn_order(
            purchase_order_number=purchase_order_number, include_detalle=include_detalle
        )

        if purchase_yarn_order_result.is_failure:
            return purchase_yarn_order_result

        return Success(
            OrdenCompraWithDetallesSchema.model_validate(
                purchase_yarn_order_result.value
            )
        )
