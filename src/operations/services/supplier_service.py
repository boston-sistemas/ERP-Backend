from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.operations.failures import (
    SUPPLIER_NOT_FOUND_FAILURE,
    SUPPLIER_INACTIVE_FAILURE,
)
from src.operations.models import Supplier
from src.operations.repositories import SupplierRepository
from src.operations.schemas import SupplierSchema

from src.core.utils import is_active_status

class SupplierService:
    def __init__(self, promec_db: AsyncSession) -> None:
        self.promec_db = promec_db
        self.repository = SupplierRepository(promec_db)

    async def _read_supplier(
        self,
        supplier_code: str,
        include_inactive: bool = False,
        include_service: bool = False,
    ) -> Result[Supplier, CustomException]:
        supplier = await self.repository.find_supplier_by_code(
            supplier_code=supplier_code,
            include_service=include_service,
        )

        if supplier is None:
            return SUPPLIER_NOT_FOUND_FAILURE

        if not is_active_status(supplier.is_active) and not include_inactive:
            return SUPPLIER_INACTIVE_FAILURE

        return Success(supplier)

    async def read_supplier(
        self,
        supplier_code: str,
        include_inactive: bool = False,
        include_service: bool = False,
    ) -> Result[SupplierSchema, CustomException]:
        supplier = await self._read_supplier(
            supplier_code=supplier_code,
            include_inactive=include_inactive,
            include_service=include_service,
        )

        if supplier.is_failure:
            return supplier

        return Success(SupplierSchema.model_validate(supplier.value))
