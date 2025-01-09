from sqlalchemy import BinaryExpression
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.constants import MECSA_COMPANY_CODE
from src.core.repository import BaseRepository
from src.operations.models import OrdenCompraDetalle


class PurchaseOrderDetailRepository(BaseRepository[OrdenCompraDetalle]):
    def __init__(self, promec_db: AsyncSession, flush: bool = False) -> None:
        super().__init__(OrdenCompraDetalle, promec_db, flush)

    async def find_purchase_order_detail_by_order_number_and_product_code(
        self,
        order_number: str,
        product_code: str,
        filter: BinaryExpression = None,
    ) -> OrdenCompraDetalle | None:
        base_filter = (
            (OrdenCompraDetalle.company_code == MECSA_COMPANY_CODE)
            & (OrdenCompraDetalle.order_number == order_number)
            & (OrdenCompraDetalle.product_code == product_code)
        )

        filter = base_filter & filter if filter is not None else base_filter

        purchase_order_detail = await self.find(filter=filter)
        return purchase_order_detail
