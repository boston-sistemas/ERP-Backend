from sqlalchemy.ext.asyncio import AsyncSession

from src.core.constants import MECSA_COMPANY_CODE
from src.core.exceptions import CustomException
from src.core.repository import (
    BaseRepository,
)
from src.core.result import Result, Success
from src.operations.failures import (
    YARN_PURCHASE_ENTRY_UPDATE_INVENTORY_FAILURE,
)
from src.operations.models import (
    CardOperation,
    FabricWarehouse,
    Movement,
    MovementDetail,
    MovementDetailAux,
    MovementYarnOCHeavy,
    ProductInventory,
)
from src.operations.repositories import MovementRepository

from .product_inventory_service import ProductInventoryService


class MovementService:
    def __init__(self, promec_db: AsyncSession) -> None:
        self.promec_db = promec_db
        self.repository = MovementRepository(promec_db=promec_db)
        self.movement_detail_repository = BaseRepository(
            model=MovementDetail, db=promec_db
        )
        self.movement_detail_aux_repository = BaseRepository(
            model=MovementDetailAux, db=promec_db
        )
        self.movement_detail_heavy_repository = BaseRepository(
            model=MovementYarnOCHeavy, db=promec_db
        )
        self.fabric_warehouse_repository = BaseRepository(
            model=FabricWarehouse, db=promec_db
        )
        self.card_operation_repository = BaseRepository(
            model=CardOperation, db=promec_db
        )
        self.product_inventory_service = ProductInventoryService(promec_db=promec_db)

    async def read_movement(
        self,
        document_number: str,
        storage_code: str,
        movement_type: str,
        movement_code: str,
        document_code: str,
        period: int,
        include_detail: bool = False,
    ) -> Result[Movement, CustomException]:
        base_filter = (
            (Movement.storage_code == storage_code)
            & (Movement.movement_type == movement_type)
            & (Movement.movement_code == movement_code)
            & (Movement.document_code == document_code)
            & (Movement.period == period)
        )

        movement = await self.repository.find_movement_by_document_number(
            document_number=document_number,
            filter=base_filter,
            include_detail=include_detail,
        )

        return Success(movement)

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

                await self.product_inventory_service.create_product_inventory(
                    product_inventory
                )
                return Success(product_inventory)
            return YARN_PURCHASE_ENTRY_UPDATE_INVENTORY_FAILURE

        return Success(product_inventory.value)

    async def delete_movement(
        self,
        movement: Movement = None,
        movement_detail: list[MovementDetail] = [],
        movememt_detail_aux: list[MovementDetailAux] = [],
        movement_detail_heavy: list[MovementYarnOCHeavy] = [],
        movement_detail_fabric: list[FabricWarehouse] = [],
        movement_detail_card: list[CardOperation] = [],
    ) -> Result[None, CustomException]:
        if movement:
            await self.repository.delete(movement, flush=True)

        if movement_detail:
            await self.movement_detail_repository.delete_all(
                movement_detail, flush=True
            )

        if movememt_detail_aux:
            await self.movement_detail_aux_repository.delete_all(
                movememt_detail_aux, flush=True
            )

        if movement_detail_heavy:
            await self.movement_detail_heavy_repository.delete_all(
                movement_detail_heavy, flush=True
            )

        if movement_detail_fabric:
            await self.fabric_warehouse_repository.delete_all(
                movement_detail_fabric, flush=True
            )

        if movement_detail_card:
            await self.card_operation_repository.delete_all(
                movement_detail_card, flush=True
            )

        return Success(None)

    async def save_movement(
        self,
        movement: Movement = None,
        movement_detail: list[MovementDetail] = [],
        movememt_detail_aux: list[MovementDetailAux] = [],
        movement_detail_heavy: list[MovementYarnOCHeavy] = [],
        movement_detail_fabric: list[FabricWarehouse] = [],
        movement_detail_card: list[CardOperation] = [],
    ) -> Result[None, CustomException]:
        if movement:
            await self.repository.save(movement, flush=True)

        if movement_detail:
            await self.movement_detail_repository.save_all(movement_detail, flush=True)

        if movememt_detail_aux:
            await self.movement_detail_aux_repository.save_all(
                movememt_detail_aux, flush=True
            )

        if movement_detail_heavy:
            await self.movement_detail_heavy_repository.save_all(
                movement_detail_heavy, flush=True
            )

        if movement_detail_fabric:
            await self.fabric_warehouse_repository.save_all(
                movement_detail_fabric, flush=True
            )

        if movement_detail_card:
            await self.card_operation_repository.save_all(
                movement_detail_card, flush=True
            )

        return Success(None)
