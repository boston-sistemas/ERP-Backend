from sqlalchemy.ext.asyncio import AsyncSession

from src.core.constants import MECSA_COMPANY_CODE
from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.operations.failures import (
    YARN_PURCHASE_ENTRY_UPDATE_INVENTORY_FAILURE,
)
from src.operations.models import ProductInventory
from src.operations.repositories import MovementRepository

from src.core.repository import (
    BaseRepository,
)
from .product_inventory_service import ProductInventoryService

from src.operations.models import (
    Movement,
    MovementDetail,
    FabricWarehouse,
    CardOperation,
)

class MovementService:
    def __init__(self, promec_db: AsyncSession) -> None:
        self.promec_db = promec_db
        self.repository = MovementRepository(promec_db=promec_db)
        self.movement_detail_repository = BaseRepository(
            model=MovementDetail, db=promec_db
        )
        self.fabric_warehouse_repository = BaseRepository(
            model=FabricWarehouse, db=promec_db
        )
        self.card_operation_repository = BaseRepository(
            model=CardOperation, db=promec_db
        )
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

                await self.product_inventory_service.create_product_inventory(product_inventory)
                return Success(product_inventory)
            return YARN_PURCHASE_ENTRY_UPDATE_INVENTORY_FAILURE

        return Success(product_inventory.value)

    async def create_movement(
        self,
        movement: Movement,
        movement_detail: list[MovementDetail] = [],
        movement_detail_fabric: list[FabricWarehouse] = [],
        movement_detail_card: list[CardOperation] = [],
    ) -> Result[None, CustomException]:

        await self.repository.save(movement)

        for detail in movement_detail:
            await self.movement_detail_repository.save(detail)

        for detail in movement_detail_fabric:
            await self.fabric_warehouse_repository.save(detail)

        for detail in movement_detail_card:
            await self.card_operation_repository.save(detail)

        return Success(None)
