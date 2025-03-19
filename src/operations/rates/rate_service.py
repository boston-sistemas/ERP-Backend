from sqlalchemy.ext.asyncio import AsyncSession

from src.core.constants import (
    MECSA_COMPANY_CODE,
)
from src.core.exceptions import CustomException
from src.core.repositories import SequenceRepository
from src.core.result import Result, Success
from src.core.utils import PERU_TIMEZONE, calculate_time
from src.operations.constants import (
    ANNULLED_SERVICE_ORDER_ID,
    SCHEDULED_SERVICE_ORDER_ID,
    UNIT_TEJ_DEFAULT_VALUE,
)
from src.operations.models import ServiceRate
from src.operations.sequences import rate_id_seq

from ..services.fabric_service import FabricService
from ..services.supplier_service import SupplierService
from .rate_failures import RateFailures
from .rate_repository import RateRepository
from .rate_schema import (
    RateCreateSchema,
    RateFilterParams,
    RateListSchema,
    RateSchema,
    RateUpdateSchema,
)


class RateService:
    def __init__(self, promec_db: AsyncSession) -> None:
        self.promec_db = promec_db
        self.repository = RateRepository(promec_db=promec_db)
        self.supplier_service = SupplierService(promec_db=promec_db)
        self.fabric_service = FabricService(db=promec_db, promec_db=promec_db)
        self.rate_service_sequence = SequenceRepository(
            sequence=rate_id_seq, db=promec_db
        )

    async def read_service_rates(
        self,
        filter_params: RateFilterParams,
    ) -> Result[RateListSchema, CustomException]:
        service_rates = await self.repository.find_rates(
            **filter_params.model_dump(exclude={"page"}),
        )
        return Success(RateListSchema(service_rates=service_rates))

    async def _read_service_rate(
        self,
        rate_id: str,
        include_order_service_detail_rate: bool = False,
    ) -> Result[RateSchema, CustomException]:
        service_rate = await self.repository.find_rate_by_id(
            rate_id=rate_id,
        )

        if service_rate is None:
            return RateFailures.RATE_NOT_FOUND_FAILURE

        return Success(service_rate)

    async def read_service_rate(
        self, rate_id: str
    ) -> Result[RateSchema, CustomException]:
        service_rate = await self._read_service_rate(
            rate_id=rate_id,
        )

        if service_rate.is_failure:
            return service_rate

        service_rate = service_rate.value

        return Success(RateSchema.model_validate(service_rate))

    async def _validate_service_rate_data(
        self, data: RateCreateSchema
    ) -> Result[None, CustomException]:
        validation_result = await self.supplier_service.read_supplier(
            supplier_code=data.supplier_id,
            include_service=True,
        )
        if validation_result.is_failure:
            return validation_result

        services = [
            service.service_code for service in validation_result.value.services
        ]
        if data.serial_code not in services:
            return RateFailures.RATE_SERVICE_NOT_FOUND_FAILURE

        validation_result = await self.fabric_service.read_fabric(
            fabric_id=data.fabric_id,
            include_recipe=True,
            include_color=True,
        )
        if validation_result.is_failure:
            return validation_result

        return Success(None)

    async def create_service_rate(
        self, form: RateCreateSchema
    ) -> Result[RateSchema, CustomException]:
        validation_result = await self._validate_service_rate_data(form)

        if validation_result.is_failure:
            return validation_result

        rate_id_seq = await self.rate_service_sequence.next_value()

        service_rate = ServiceRate(
            rate_id=rate_id_seq,
            serial_code=form.serial_code,
            supplier_id=form.supplier_id,
            fabric_id=form.fabric_id,
            company_code=MECSA_COMPANY_CODE,
            currency=form.currency,
            unit=UNIT_TEJ_DEFAULT_VALUE,
            rate=form.rate,
            extended_rate=form.extended_rate,
            project_rate=form.project_rate,
            period=form.period,
            month_number=form.month_number,
            os_beggining="",
            os_ending="",
            code=form.code,
        )

        await self.repository.save(service_rate)

        return Success(RateSchema.model_validate(service_rate))

    async def _validate_service_rate_data_update(
        self,
        data: RateUpdateSchema,
    ) -> Result[None, CustomException]:
        return Success(None)

    async def _validate_update_service_rate(
        self,
        service_rate: ServiceRate,
    ) -> Result[None, CustomException]:
        if not service_rate.order_service_detail_rate:
            return Success(None)

        for detail in service_rate.order_service_detail_rate:
            if (
                detail.status_param_id != SCHEDULED_SERVICE_ORDER_ID
                or detail.status_param_id != ANNULLED_SERVICE_ORDER_ID
            ):
                return RateFailures.RATE_UPDATE_FAILURE
        return Success(None)

    async def update_service_rate(
        self,
        rate_id: str,
        form: RateUpdateSchema,
    ) -> Result[RateSchema, CustomException]:
        service_rate_result: Success = await self._read_service_rate(
            rate_id=rate_id,
            include_order_service_detail_rate=True,
        )

        if service_rate_result.is_failure:
            return service_rate_result
        service_rate: ServiceRate = service_rate_result.value

        validation_result = await self._validate_update_service_rate(
            service_rate=service_rate,
        )

        if validation_result.is_failure:
            return validation_result

        validation_result = await self._validate_service_rate_data_update(data=form)
        if validation_result.is_failure:
            return validation_result

        service_rate.rate = form.rate
        service_rate.extended_rate = form.extended_rate
        service_rate.project_rate = form.project_rate

        await self.repository.save(service_rate)

        return Success(RateSchema.model_validate(service_rate))

    async def is_updated_permission_service_rate(
        self,
        rate_id: int,
    ) -> Result[None, CustomException]:
        service_rate_result: Success = await self._read_service_rate(
            rate_id=rate_id,
            include_order_service_detail_rate=True,
        )

        if service_rate_result.is_failure:
            return service_rate_result

        service_rate: ServiceRate = service_rate_result.value

        validation_result = await self._validate_update_service_rate(
            service_rate=service_rate,
        )

        if validation_result.is_failure:
            return validation_result

        return Success(None)

    async def initialize_os_beg_by_fabric(
        self, fabric_id: str, service_rates: ServiceRate, purchase_service_number: str
    ) -> Result[RateSchema, CustomException]:
        current_time = calculate_time(tz=PERU_TIMEZONE)
        current_period = current_time.date().year
        current_month_number = current_time.date().month
        service_rates: list[ServiceRate] = await self.repository.find_rates(
            fabric_id=fabric_id,
            period=current_period,
            month_number=current_month_number,
            limit=2,
        )
        if service_rates:
            return RateFailures.RATE_NOT_FOUND_FAILURE

        if len(service_rates) == 1:
            if not service_rates[0].os_beggining:
                service_rates[0].os_beggining = purchase_service_number
        else:
            if not service_rates[0].os_beggining:
                service_rates[0].os_beggining = purchase_service_number
                service_rates[1].os_ending = purchase_service_number

        await self.repository.save(service_rates)

        return Success(service_rates[0].rate_id)
