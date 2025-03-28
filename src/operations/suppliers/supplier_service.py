from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.repository import BaseRepository
from src.core.result import Result, Success
from src.core.utils import map_active_status
from src.operations.models import Supplier, SupplierColor
from src.operations.models import SupplierService as SupplierServiceModel
from src.operations.schemas import MecsaColorSchema
from src.operations.services.mecsa_color_service import MecsaColorService

from .supplier_failure import SupplierFailures
from .supplier_repository import SupplierRepository
from .supplier_schema import (
    SupplierCreateSupplierColorSchema,
    SupplierFilterParams,
    SupplierListSchema,
    SupplierSchema,
    SupplierSimpleListSchema,
)
from .suppliers_colors.supplier_color_failures import SupplierColorFailures
from .suppliers_colors.supplier_color_schema import (
    SupplierColorFilterParams,
    SupplierColorSchema,
    SupplierColorUpdateSchema,
)
from .suppliers_colors.supplier_color_service import SupplierColorService


class SupplierService:
    def __init__(self, promec_db: AsyncSession) -> None:
        self.promec_db = promec_db
        self.repository = SupplierRepository(promec_db)
        self.supplier_service_repository = BaseRepository[SupplierServiceModel](
            model=SupplierServiceModel, db=promec_db
        )
        # self.supplier_color_repository = SupplierColorRepository(promec_db)
        self.supplier_color_service = SupplierColorService(promec_db=promec_db)
        self.mecsa_color_service = MecsaColorService(promec_db=promec_db)

    async def _read_supplier(
        self,
        supplier_code: str,
        include_inactives: bool = False,
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
            return SupplierFailures.SUPPLIER_NOT_FOUND_FAILURE

        return Success(supplier)

    async def read_supplier(
        self,
        supplier_code: str,
        include_inactives: bool = False,
        include_service: bool = False,
        include_colors: bool = False,
        include_other_addresses: bool = False,
    ) -> Result[SupplierSchema, CustomException]:
        supplier = await self._read_supplier(
            supplier_code=supplier_code,
            include_inactives=include_inactives,
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
            return SupplierFailures.SUPPLIER_SERVICE_NOT_FOUND_FAILURE

        value = supplier_service.sequence_number

        supplier_service.sequence_number += 1
        await self.supplier_service_repository.save(supplier_service, flush=True)

        return Success(value)

    async def read_suppliers_by_service(
        self,
        service_code: str,
        filter_params: SupplierFilterParams = SupplierFilterParams(),
    ) -> Result[list[SupplierSchema], CustomException]:
        suppliers = await self.repository.find_suppliers_by_service(
            service_code=service_code, **filter_params.model_dump(exclude={"page"})
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

    async def _validate_supplier_color_data(
        self,
        data: SupplierCreateSupplierColorSchema,
    ) -> Result[None, CustomException]:
        validation_result = await self._read_supplier(
            supplier_code=data.supplier_id,
        )
        if validation_result.is_failure:
            return validation_result

        validation_result = await self.supplier_color_service.read_supplier_color(
            id=data.id,
        )
        if validation_result.is_success:
            return SupplierColorFailures.SUPPLIER_COLOR_ALREADY_EXISTS_FAILURE

        validation_result = await self.supplier_color_service.read_supplier_colors(
            filter_params=SupplierColorFilterParams(
                supplier_ids=[data.supplier_id],
                mecsa_color_id=data.mecsa_color_id,
            )
        )
        if validation_result.is_success:
            return SupplierFailures.SUPPLIER_WITH_MECSA_COLOR_ALREADY_EXISTS_FAILURE

        validation_result = await self.mecsa_color_service.read_mecsa_color(
            color_id=data.mecsa_color_id,
        )
        if validation_result.is_failure:
            return validation_result

        color = validation_result.value
        if not color.is_active:
            return SupplierColorFailures.SUPPLIER_COLOR_NOT_ACTIVE_FAILURE

        return Success(None)

    async def create_supplier_color(
        self,
        form: SupplierCreateSupplierColorSchema,
    ) -> Result[SupplierCreateSupplierColorSchema, CustomException]:
        validation_result = await self._validate_supplier_color_data(form)

        if validation_result.is_failure:
            return validation_result

        supplier_color = SupplierColor(
            id=form.id,
            supplier_id=form.supplier_id,
            description=form.description,
            mecsa_color_id=form.mecsa_color_id,
            is_active=True,
        )
        await self.repository.save(supplier_color)

        return Success(SupplierColorSchema.model_validate(supplier_color))

    async def _validate_supplier_color_data_update(
        self,
        data: SupplierColorUpdateSchema,
    ) -> Result[None, CustomException]:
        return Success(None)

    async def _validate_update_supplier_color(
        self,
        supplier_color_service: SupplierColor,
    ) -> Result[None, CustomException]:
        return Success(None)

    async def update_supplier_color(
        self,
        id: str,
        form: SupplierColorUpdateSchema,
    ) -> Result[SupplierColor, CustomException]:
        supplier_color_result: Success = (
            await self.supplier_color_service.read_supplier_color(
                id=id,
            )
        )
        if supplier_color_result.is_failure:
            return supplier_color_result
        supplier_color: SupplierColor = supplier_color_result.value

        validation_result = await self._validate_update_supplier_color(
            supplier_color_service=supplier_color,
        )
        if validation_result.is_failure:
            return validation_result

        validation_result = await self._validate_supplier_color_data_update(data=form)
        if validation_result.is_failure:
            return validation_result

        supplier_color.description = form.description

        await self.repository.save(supplier_color)

        return Success(SupplierColorSchema.model_validate(supplier_color))
