from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.operations.models import InventoryItem

from ..fabric_service import FabricService
from .raw_fabric_failure import RAW_FABRIC_NOT_FOUND_FAILURE
from .raw_fabric_repository import RawFabricRepository


class RawFabricService(FabricService):
    def __init__(self, db: AsyncSession, promec_db: AsyncSession):
        self.repository = RawFabricRepository(db=promec_db)

    async def _read_fabric(
        self, fabric_id: str
    ) -> Result[InventoryItem, CustomException]:
        fabric = await self.repository.find_fabric_by_id(fabric_id=fabric_id)
        if fabric:
            return Success(fabric)

        return RAW_FABRIC_NOT_FOUND_FAILURE

    async def read_raw_fabric(self, fabric_id: str) -> Result[None, CustomException]:
        fabric = await self.repository.find_fabric_by_id(fabric_id=fabric_id)
        return Success(None)

    async def read_raw_fabrics(self) -> Result[list[InventoryItem], CustomException]:
        fabrics = await self.repository.find_fabrics()
        return Success(None)

    async def create_raw_fabric(self, form: dict) -> Result[None, CustomException]:
        return Success(None)

    async def update_raw_fabric(
        self, fabric_id: str, form: dict
    ) -> Result[None, CustomException]:
        return Success(None)
