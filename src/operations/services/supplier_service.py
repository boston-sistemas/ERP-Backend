from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.repository import BaseRepository
from src.core.result import Result, Success
from src.core.utils import is_active_status
from src.operations.failures import (
    SUPPLIER_INACTIVE_FAILURE,
    SUPPLIER_NOT_FOUND_FAILURE,
    SUPPLIER_SERVICE_NOT_FOUND_FAILURE,
)
from src.operations.models import Supplier
from src.operations.models import SupplierService as SupplierServic
from src.operations.repositories import SupplierRepository
from src.operations.schemas import SupplierSchema, SupplierSimpleListSchema


class SupplierService:
    def __init__(self, promec_db: AsyncSession) -> None:
        self.promec_db = promec_db
        self.repository = SupplierRepository(promec_db)
        self.supplier_service_repository = BaseRepository(
            model=SupplierServic, db=promec_db
        )

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

    async def next_service_sequence(
        self,
        supplier_code: str,
        service_code: str,
    ) -> Result[int, CustomException]:
        supplier_service = await self.supplier_service_repository.find(
            (SupplierServic.supplier_code == supplier_code)
            & (SupplierServic.service_code == service_code),
        )

        if supplier_service is None:
            return SUPPLIER_SERVICE_NOT_FOUND_FAILURE

        value = supplier_service.sequence_number

        supplier_service.sequence_number += 1

        await self.supplier_service_repository.save(supplier_service)

        return Success(value)

    async def read_suppliers_by_service(
        self,
        service_code: str,
        limit: int,
        offset: int,
        include_inactive: bool = False,
    ) -> Result[list[SupplierSchema], CustomException]:

        suppliers = await self.repository.find_suppliers_by_service(
            service_code=service_code,
            limit=limit,
            offset=offset,
            include_inactive=include_inactive,
        )

        return Success(SupplierSimpleListSchema(suppliers=suppliers))
