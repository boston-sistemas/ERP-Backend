from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.operations.failures import SUPPLIER_NOT_FOUND_FAILURE
from src.operations.models import Supplier
from src.operations.repositories import SupplierRepository
from src.operations.schemas import SupplierSimpleSchema


class SupplierService:
    def __init__(self, promec_db: AsyncSession) -> None:
        self.promec_db = promec_db
        self.repository = SupplierRepository(promec_db)

    async def _read_supplier(
        self,
        supplier_code: str,
    ) -> Result[Supplier, CustomException]:
        supplier = await self.repository.find_supplier_by_code(
            supplier_code=supplier_code
        )

        if supplier is None:
            return SUPPLIER_NOT_FOUND_FAILURE

        return Success(supplier)

    async def read_supplier(
        self,
        supplier_code: str,
    ) -> Result[SupplierSimpleSchema, CustomException]:
        supplier = await self._read_supplier(supplier_code)

        if supplier.is_failure:
            return supplier

        return Success(SupplierSimpleSchema.model_validate(supplier.value))
