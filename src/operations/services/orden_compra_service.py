from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.operations.failures import (
    PURCHASE_YARN_ORDER_NOT_FOUND_FAILURE,
    PURCHASE_YARN_ORDER_ANULLED_FAILURE,
)
from src.operations.models import OrdenCompra
from src.operations.repositories import (
    OrdenCompraRepository,
    PurchaseOrderDetailRepository,
)
from src.operations.schemas import OrdenCompraWithDetailSchema


class OrdenCompraService:
    def __init__(self, db: AsyncSession) -> None:
        self.repository = OrdenCompraRepository(db)
        self.purchase_order_detail_service = PurchaseOrderDetailRepository(db)

    async def read_purchase_yarn_orders(
        self,
        include_detalle: bool = False,
    ) -> list[OrdenCompra]:
        return await self.repository.find_ordenes_yarn(include_detalle=include_detalle)

    async def _read_purchase_yarn_order(
        self,
        purchase_order_number: str,
        include_detalle: bool = False,
        include_annulled: bool = False,
    ) -> Result[OrdenCompra, CustomException]:
        orden = await self.repository.find_yarn_order_by_purchase_order_number(
            purchase_order_number=purchase_order_number,
            include_detalle=include_detalle,
        )

        if orden is None:
            return PURCHASE_YARN_ORDER_NOT_FOUND_FAILURE

        if not include_annulled and orden.status_flag == "A":
            return PURCHASE_YARN_ORDER_ANULLED_FAILURE

        return Success(orden)

    async def read_purchase_yarn_order(
        self,
        purchase_order_number: str,
        include_detalle: bool = False,
        include_annulled: bool = False,
    ) -> OrdenCompra | None:
        purchase_yarn_order_result = await self._read_purchase_yarn_order(
            purchase_order_number=purchase_order_number,
            include_detalle=include_detalle,
            include_annulled=include_annulled,
        )

        if purchase_yarn_order_result.is_failure:
            return purchase_yarn_order_result

        return Success(
            OrdenCompraWithDetailSchema.model_validate(
                purchase_yarn_order_result.value
            )
        )

    async def rollback_quantity_supplied_by_product_code(
        self,
        purchase_order_number: str,
        product_code: str,
        quantity_supplied: int,
    ) -> Result[OrdenCompra, CustomException]:
        purchase_order_result = await self._read_purchase_yarn_order(
            purchase_order_number=purchase_order_number,
            include_detalle=True,
            include_all=True,
        )

        if purchase_order_result.is_failure:
            return purchase_order_result

        purchase_order: OrdenCompra = purchase_order_result.value

        count_unsupplied = 0

        for detail in purchase_order.detail:
            if detail.product_code == product_code:
                detail.quantity_supplied -= quantity_supplied

                if detail.quantity_supplied < detail.quantity_ordered:
                    detail.status_flag = "P"

            if detail.status_flag == "P":
                count_unsupplied += 1

        if count_unsupplied > 0:
            purchase_order.status_flag = "P"

        await self.purchase_order_detail_service.save_all(purchase_order.detail)
        await self.repository.save(purchase_order)

        return Success(None)

    async def update_quantity_supplied_by_product_code(
        self,
        purchase_order_number: str,
        product_code: str,
        quantity_supplied: int,
    ) -> Result[OrdenCompra, CustomException]:
        purchase_order_result = await self._read_purchase_yarn_order(
            purchase_order_number=purchase_order_number,
            include_detalle=True,
        )

        if purchase_order_result.is_failure:
            return purchase_order_result

        purchase_order: OrdenCompra = purchase_order_result.value

        detail_amount = len(purchase_order.detail)

        count_supplied = 0

        for detail in purchase_order.detail:
            if detail.product_code == product_code:
                detail.quantity_supplied += quantity_supplied

                if detail.quantity_supplied >= detail.quantity_ordered:
                    detail.status_flag = "C"

            if detail.status_flag == "C":
                count_supplied += 1

        if count_supplied == detail_amount:
            purchase_order.status_flag = "C"

        await self.purchase_order_detail_service.save_all(purchase_order.detail)
        await self.repository.save(purchase_order)

        return Success(None)
