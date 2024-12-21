from sqlalchemy.ext.asyncio import AsyncSession

from src.core.constants import MECSA_COMPANY_CODE
from src.core.repository import BaseRepository
from src.operations.models import Supplier


class SupplierRepository(BaseRepository[Supplier]):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(Supplier, db, flush)

    async def find_supplier_by_code(
        self,
        supplier_code: str,
    ) -> Supplier | None:
        id = {"company_code": MECSA_COMPANY_CODE, "code": supplier_code}
        supplier = await self.find_by_id(id=id)

        return supplier
