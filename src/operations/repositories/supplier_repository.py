from sqlalchemy.ext.asyncio import AsyncSession

from src.core.constants import MECSA_COMPANY_CODE
from src.core.repository import BaseRepository
from src.operations.models import Supplier
from sqlalchemy.orm import joinedload


class SupplierRepository(BaseRepository[Supplier]):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(Supplier, db, flush)

    @staticmethod
    def include_service():
        base_options = [
            joinedload(Supplier.services)
        ]

        return base_options

    def get_load_options(
        self,
        include_service: bool = False,
    ):
        options = []

        if include_service:
            options.extend(self.include_service())

        return options

    async def find_supplier_by_code(
        self,
        supplier_code: str,
        include_service: bool = False,
    ) -> Supplier | None:
        id = {"company_code": MECSA_COMPANY_CODE, "code": supplier_code}
        options = self.get_load_options(include_service=include_service)

        supplier = await self.find_by_id(id=id, options=options)

        return supplier
