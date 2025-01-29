from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.operations.models import InventoryItem

from ..fabric_service import FabricService
from .finished_fabric_failure import FINISHED_FABRIC_NOT_FOUND_FAILURE
from .finished_fabric_repository import FinishedFabricRepository


class FinishedFabricService(FabricService):
    def __init__(self, db: AsyncSession, promec_db: AsyncSession):
        self.repository = FinishedFabricRepository(db=promec_db)

    async def _read_fabric(
        self, fabric_id: str
    ) -> Result[InventoryItem, CustomException]:
        fabric = await self.repository.find_fabric_by_id(fabric_id=fabric_id)
        if fabric:
            return Success(fabric)

        return FINISHED_FABRIC_NOT_FOUND_FAILURE

    async def read_finished_fabric(
        self, fabric_id: str
    ) -> Result[InventoryItem, CustomException]:
        fabric = await self.repository.find_fabric_by_id(fabric_id=fabric_id)
        return Success(fabric)

    async def read_finished_fabrics(
        self,
    ) -> Result[list[InventoryItem], CustomException]:
        fabrics = await self.repository.find_fabrics()
        return Success(fabrics)

    async def create_finished_fabric(self, form: dict) -> Result[None, CustomException]:
        await self.repository.create_fabric(fabric_data=form)
        return Success(None)

    async def update_finished_fabric(
        self, fabric_id: str, form: dict
    ) -> Result[None, CustomException]:
        await self.repository.update_fabric(fabric_id=fabric_id, fabric_data=form)
        return Success(None)
