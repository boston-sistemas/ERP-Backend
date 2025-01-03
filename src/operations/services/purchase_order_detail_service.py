from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.operations.failures import PURCHASE_ORDER_DETAIL_NOT_FOUND_FAILURE
from src.operations.models import OrdenCompra
from src.operations.repositories import PurchaseOrderDetailRepository


class PurchaseOrderDetailService:
    def __init__(self, promec_db: AsyncSession) -> None:
        self.promec_db = promec_db
        self.repository = PurchaseOrderDetailRepository(promec_db=promec_db)

    async def _read_purchase_order_detail(
        self, order_number: str, product_code: str
    ) -> Result[OrdenCompra, CustomException]:
        purchase_order_detail = await self.repository.find_purchase_order_detail_by_order_number_and_product_code(
            order_number=order_number, product_code=product_code
        )

        if purchase_order_detail is None:
            return PURCHASE_ORDER_DETAIL_NOT_FOUND_FAILURE

        return Success(purchase_order_detail)
