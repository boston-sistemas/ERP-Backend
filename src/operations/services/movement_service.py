from sqlalchemy.ext.asyncio import AsyncSession

from src.core.constants import MECSA_COMPANY_CODE
from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.operations.failures import (
    YARN_PURCHASE_ENTRY_UPDATE_INVENTORY_FAILURE,
)
from src.operations.models import ProductInventory
from src.operations.repositories import MovementRepository

from .product_inventory_service import ProductInventoryService


class MovementService:
    def __init__(self, promec_db: AsyncSession) -> None:
        self.promec_db = promec_db
        self.repository = MovementRepository(promec_db=promec_db)
        self.product_inventory_service = ProductInventoryService(promec_db=promec_db)

    async def _read_or_create_product_inventory(
        self,
        storage_code: str,
        product_code: str,
        period: int,
        enable_create: bool = False,
    ) -> Result[ProductInventory, CustomException]:
        product_inventory = (
            await self.product_inventory_service._read_product_inventory(
                storage_code=storage_code,
                product_code=product_code,
                period=period,
            )
        )

        if product_inventory.is_failure:
            if enable_create:
                product_inventory = ProductInventory(
                    company_code=MECSA_COMPANY_CODE,
                    storage_code=storage_code,
                    product_code=product_code,
                    period=period,
                    current_stock=0,
                )

                # await self.product_inventory_service.save(product_inventory)
                return Success(product_inventory)
            return YARN_PURCHASE_ENTRY_UPDATE_INVENTORY_FAILURE

        return Success(product_inventory.value)
