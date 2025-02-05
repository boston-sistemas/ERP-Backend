from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, load_only
from sqlalchemy.orm.strategy_options import Load

from src.core.constants import MECSA_COMPANY_CODE
from src.core.repository import BaseRepository
from src.operations.models import Supplier, SupplierService


# TODO: Review this repository
class SupplierRepository(BaseRepository[Supplier]):
    def __init__(self, db: AsyncSession, flush: bool = False) -> None:
        super().__init__(Supplier, db, flush)

    @staticmethod
    def get_supplier_fields() -> tuple:
        return (
            Supplier.code,
            Supplier.name,
            Supplier.address,
            Supplier.ruc,
            Supplier.is_active,
            Supplier.storage_code,
            Supplier.initials,
            Supplier.email,
        )

    @staticmethod
    def include_service():
        base_options = [joinedload(Supplier.services)]

        return base_options

    def get_load_options(
        self,
        include_service: bool = False,
        include_colors: bool = False,
        include_other_addresses: bool = False,
    ):
        options = []

        options.append(load_only(*self.get_supplier_fields()))

        if include_service:
            options.extend(self.include_service())

        if include_other_addresses:
            options.append(joinedload(Supplier.other_addresses))

        if include_colors:
            options.append(joinedload(Supplier.colors))

        return options

    async def find_supplier_by_code(
        self,
        supplier_code: str,
        include_service: bool = False,
        include_colors: bool = False,
        include_other_addresses: bool = False,
    ) -> Supplier | None:
        id = {"company_code": MECSA_COMPANY_CODE, "code": supplier_code}

        options = self.get_load_options(
            include_service=include_service,
            include_other_addresses=include_other_addresses,
            include_colors=include_colors,
        )

        supplier = await self.find_by_id(id=id, options=options)

        return supplier

    async def find_suppliers_by_service(
        self,
        service_code: str,
        limit: int,
        offset: int,
        include_inactive: bool = False,
        include_other_addresses: bool = False,
    ) -> list[Supplier]:
        options: list[Load] = []
        joins: list[tuple] = []

        joins.append(Supplier.services)

        options = self.get_load_options(include_other_addresses=include_other_addresses)

        base_filter = (Supplier.company_code == MECSA_COMPANY_CODE) & (
            SupplierService.service_code == service_code
        )

        if not include_inactive:
            base_filter = base_filter & (Supplier.is_active == "A")

        suppliers = await self.find_all(
            filter=base_filter,
            options=options,
            joins=joins,
            limit=limit,
            offset=offset,
            apply_unique=True,
        )

        return suppliers
