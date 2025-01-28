from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.operations.failures import PRODUCT_INVENTORY_NOT_FOUND_FAILURE
from src.operations.models import ProductInventory
from src.operations.repositories import ProductInventoryRepository


class ProductInventoryService:
    def __init__(self, promec_db: AsyncSession) -> None:
        self.promec_db = promec_db
        self.repository = ProductInventoryRepository(promec_db=promec_db)

    async def _read_product_inventory(
        self,
        product_code: str,
        storage_code: str,
        period: int,
    ) -> Result[ProductInventory, CustomException]:
        product_inventory = await self.repository.find_product_inventory_by_product_code_and_storage_code(
            product_code=product_code, storage_code=storage_code, period=period
        )

        if product_inventory is None:
            return PRODUCT_INVENTORY_NOT_FOUND_FAILURE

        return Success(product_inventory)

    async def create_product_inventory(
        self,
        product_inventory: ProductInventory,
    ) -> Result[None, CustomException]:
        await self.repository.save(product_inventory, flush=True)

        return Success(None)

    async def _read_products_inventory(
        self, product_code: str, period: int
    ) -> Result[list[ProductInventory], CustomException]:
        products_inventory = (
            await self.repository.find_products_inventory_by_product_code(
                product_code=product_code, period=period
            )
        )

        return Success(products_inventory)

    async def rollback_currents_stock(
        self,
        storage_code: str,
        period: int,
        product_code: str,
        quantity: int,
    ) -> Result[None, CustomException]:
        result = await self._read_product_inventory(
            product_code=product_code, storage_code=storage_code, period=period
        )

        if result.is_failure:
            return result

        product_inventory: ProductInventory = result.value

        product_inventory.current_stock -= quantity

        await self.repository.save(product_inventory, flush=True)

        return Success(None)

    async def update_current_stock(
        self, product_code: str, storage_code: str, period: int, new_stock: int
    ) -> Result[None, CustomException]:
        result = await self._read_product_inventory(
            product_code=product_code, storage_code=storage_code, period=period
        )

        if result.is_failure:
            return result

        product_inventory: ProductInventory = result.value
        product_inventory.current_stock += new_stock

        await self.repository.save(product_inventory, flush=True)

        return Success(None)
