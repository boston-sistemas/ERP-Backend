from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.repository import BaseRepository
from src.core.result import Result, Success
from src.operations.failures import (
    SUPPLIER_NOT_FOUND_FAILURE,
    SUPPLIER_SERVICE_NOT_FOUND_FAILURE,
)
from src.operations.models import Supplier
from src.operations.models import SupplierService as SupplierServiceModel
from src.operations.repositories import SupplierRepository
from src.operations.schemas import (
    SupplierListSchema,
    SupplierSchema,
    SupplierSimpleListSchema,
)


class SupplierService:
    def __init__(self, promec_db: AsyncSession) -> None:
        self.promec_db = promec_db
        self.repository = SupplierRepository(promec_db)
        self.supplier_service_repository = BaseRepository[SupplierServiceModel](
            model=SupplierServiceModel, db=promec_db
        )

    async def _read_supplier(
        self,
        supplier_code: str,
        include_inactive: bool = False,
        include_service: bool = False,
        include_colors: bool = False,
        include_other_addresses: bool = False,
    ) -> Result[Supplier, CustomException]:
        supplier = await self.repository.find_supplier_by_code(
            supplier_code=supplier_code,
            include_service=include_service,
            include_colors=include_colors,
            include_other_addresses=include_other_addresses,
        )

        if supplier is None:
            return SUPPLIER_NOT_FOUND_FAILURE

        return Success(supplier)

    async def read_supplier(
        self,
        supplier_code: str,
        include_inactive: bool = False,
        include_service: bool = False,
        include_colors: bool = False,
        include_other_addresses: bool = False,
    ) -> Result[SupplierSchema, CustomException]:
        supplier = await self._read_supplier(
            supplier_code=supplier_code,
            include_inactive=include_inactive,
            include_service=include_service,
            include_colors=include_colors,
            include_other_addresses=include_other_addresses,
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
            (SupplierServiceModel.supplier_code == supplier_code)
            & (SupplierServiceModel.service_code == service_code),
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
        include_other_addresses: bool = False,
    ) -> Result[list[SupplierSchema], CustomException]:
        suppliers = await self.repository.find_suppliers_by_service(
            service_code=service_code,
            limit=limit,
            offset=offset,
            include_inactive=include_inactive,
            include_other_addresses=include_other_addresses,
        )

        return Success(SupplierSimpleListSchema(suppliers=suppliers))

    async def reads_supplier_initials_by_id(
        self,
        ids: dict[str, str],
    ) -> Result[SupplierListSchema, CustomException]:
        for supplier_code in ids:
            supplier = await self.read_supplier(supplier_code=supplier_code)
            if supplier.is_failure:
                continue

            ids[supplier_code] = supplier.value.initials

        return Success(ids)
