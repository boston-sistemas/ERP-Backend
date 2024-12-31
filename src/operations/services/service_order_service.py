from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success

from src.core.repository import BaseRepository
from src.operations.schemas import (
    ServiceOrderSimpleListSchema,
    ServiceOrderSchema,
    ServiceOrderCreateSchema,
    ServiceOrderDetailSchema,
    ServiceOrderUpdateSchema,
)
from src.core.constants import MECSA_COMPANY_CODE
from src.core.utils import PERU_TIMEZONE, calculate_time
from src.operations.models import (
    ServiceOrder,
    ServiceOrderDetail,
)
from src.operations.repositories import ServiceOrderRepository
from src.operations.failures import (
    SERVICE_ORDER_NOT_FOUND_FAILURE,
    SERVICE_ORDER_SUPPLIER_NOT_ASSOCIATED_WITH_WEAVING_FAILURE,
    SERVICE_ORDER_ALREADY_ANULLED_FAILURE,
    SERVICE_ORDER_ALREADY_SUPPLIED_FAILURE,
)
from src.operations.constants import (
    SERVICE_CODE_SUPPLIER_WEAVING,
)
from .supplier_service import SupplierService
from src.security.services import ParameterService

class ServiceOrderService:
    def __init__(self, promec_db: AsyncSession, db: AsyncSession) -> None:
        self.promec_db = promec_db
        self.repository = ServiceOrderRepository(promec_db=promec_db)
        self.supplier_service = SupplierService(promec_db=promec_db)
        self.service_order_detail_repository = BaseRepository(
            model=ServiceOrderDetail, db=promec_db
        )
        self.parameter_service = ParameterService(db=db)

    async def read_service_orders(
        self,
        order_type: str,
        limit: int,
        offset: int,
        include_inactive: bool = False,
        include_status: bool = False,
    ) -> Result[ServiceOrderSimpleListSchema, CustomException]:
        service_orders = await self.repository.find_service_orders_by_order_type(
            order_type=order_type,
            limit=limit,
            offset=offset,
            include_inactive=include_inactive,
            order_by=ServiceOrder.issue_date.desc(),
        )

        if include_status:
            for service_order in service_orders:
                status = await self.parameter_service.read_parameter(
                    parameter_id=service_order.status_param_id
                )
                if status.is_failure:
                    service_order.status = None
                else:
                    service_order.status = status.value

        return Success(ServiceOrderSimpleListSchema(service_orders=service_orders))

    async def _read_service_order(
        self,
        order_id: str,
        order_type: str,
        include_detail: bool = False,
    ) -> Result[ServiceOrderSchema, CustomException]:
        service_order = await self.repository.find_service_order_by_order_id_and_order_type(
            order_id=order_id,
            order_type=order_type,
            include_detail=include_detail,
        )

        if service_order is None:
            return SERVICE_ORDER_NOT_FOUND_FAILURE

        return Success(service_order)

    async def read_service_order(
        self,
        order_id: str,
        order_type: str,
        include_detail: bool = False,
        include_status: bool = False,
    ) -> Result[ServiceOrderSchema, CustomException]:
        service_order = await self._read_service_order(
            order_id=order_id,
            order_type=order_type,
            include_detail=include_detail,
            include_status=include_status,
        )

        if service_order.is_failure:
            return service_order

        service_order = service_order.value

        if include_status:
            status = await self.parameter_service.read_parameter(
                parameter_id=service_order.status_param_id
            )

            if status.is_failure:
                return status

            service_order.status = status.value

        return Success(ServiceOrderSchema.model_validate(service_order))

    async def _validate_service_order_data(
        self,
        data: ServiceOrderCreateSchema,
    ) -> Result[None, CustomException]:
        supplier = await self.supplier_service.read_supplier(
            supplier_code=data.supplier_id,
            include_service=True,
        )

        if supplier.is_failure:
            return supplier

        services = [service.service_code for service in supplier.value.services]
        if SERVICE_CODE_SUPPLIER_WEAVING not in services:
            return SERVICE_ORDER_SUPPLIER_NOT_ASSOCIATED_WITH_WEAVING_FAILURE
        return supplier

    async def _validate_service_order_detail_data(
        self,
        data: list[ServiceOrderDetailSchema],
    ) -> Result[None, CustomException]:

        # Validacion de que el tejido existe
        return Success(None)

    async def create_weaving_service_order(
        self,
        form: ServiceOrderCreateSchema,
    ) -> Result[ServiceOrderSchema, CustomException]:

        validation_result = await self._validate_service_order_data(data=form)

        if validation_result.is_failure:
            return validation_result

        supplier = validation_result.value

        validation_result = await self._validate_service_order_detail_data(data=form.detail)

        if validation_result.is_failure:
            return validation_result

        sequence_number = await self.supplier_service.next_service_sequence(
            supplier_code=form.supplier_id,
            service_code=SERVICE_CODE_SUPPLIER_WEAVING,
        )

        if sequence_number.is_failure:
            return sequence_number

        sequence_number = sequence_number.value

        purchase_service_number = supplier.initials + str(sequence_number)

        current_time = calculate_time(tz=PERU_TIMEZONE)
        issue_date = current_time.date()

        order_type = "TJ"

        service_order = ServiceOrder(
            company_code=MECSA_COMPANY_CODE,
            _type=order_type,
            id=purchase_service_number,
            supplier_id=form.supplier_id,
            issue_date=issue_date,
            storage_code="006",
            status_flag="P",
            user_id="DESA01",
            flgatc="N",
            flgprt="N",
            status_param_id=1023
        )

        service_order_detail = []

        for detail in form.detail:
            service_order_detail_value = ServiceOrderDetail(
                company_code=MECSA_COMPANY_CODE,
                order_id=purchase_service_number,
                order_type=order_type,
                product_id=detail.tissue_id,
                quantity_ordered=detail.quantity_ordered,
                quantity_supplied=0,
                price=detail.price,
                status_param_id=1023
            )
            service_order_detail.append(service_order_detail_value)

        await self.repository.save(service_order)

        service_order.detail = service_order_detail

        await self.service_order_detail_repository.save_all(service_order_detail)

        return Success(ServiceOrderSchema.model_validate(service_order))

    async def _delete_detail(
        self,
        service_order_detail: ServiceOrderDetail,
    ) -> None:
        await self.service_order_detail_repository.delete(service_order_detail)

    async def _delete_service_order_detail(
        self,
        service_order_detail: list[ServiceOrderDetail],
        form: ServiceOrderUpdateSchema,
    ) -> list[ServiceOrderDetail]:
        tissue_ids = [detail.tissue_id for detail in form.detail]

        for detail in service_order_detail:
            if detail.product_id not in tissue_ids:
                await self._delete_detail(detail)
                service_order_detail.remove(detail)

        return service_order_detail

    async def _validate_update_service_order(
        self,
        service_order: ServiceOrder,
    ) -> Result[None, CustomException]:
        if service_order.status_flag == "A":
            return SERVICE_ORDER_ALREADY_ANULLED_FAILURE

        if service_order.status_flag == "C":
            return SERVICE_ORDER_ALREADY_SUPPLIED_FAILURE

        for detail in service_order.detail:
            if detail.quantity_supplied > 0:
                return SERVICE_ORDER_ALREADY_SUPPLIED_FAILURE

        return Success(None)

    async def _find_service_order_detail(
        self,
        service_order_detail: list[ServiceOrderDetail],
        tissue_id: str,
    ) -> ServiceOrderDetail | None:
        for detail in service_order_detail:
            if detail.product_id == tissue_id:
                return detail

        return None

    async def update_weaving_service_order(
        self,
        order_id: str,
        form: ServiceOrderUpdateSchema,
    ) -> Result[ServiceOrderSchema, CustomException]:

        service_order = await self._read_service_order(
            order_id=order_id,
            order_type="TJ",
            include_detail=True,
        )

        if service_order.is_failure:
            return service_order

        service_order = service_order.value

        validation_result = await self._validate_update_service_order(
            service_order=service_order
        )

        if validation_result.is_failure:
            return validation_result

        validation_result = await self._validate_service_order_detail_data(data=form.detail)

        if validation_result.is_failure:
            return validation_result

        service_order.detail = await self._delete_service_order_detail( 
            service_order_detail=service_order.detail,
            form=form,
        )

        for detail in form.detail:
            service_order_detail_result = await self._find_service_order_detail(
                service_order_detail=service_order.detail,
                tissue_id=detail.tissue_id,
            )

            if service_order_detail_result is not None:
                service_order_detail_result.quantity_ordered = detail.quantity_ordered
                service_order_detail_result.price = detail.price

            else:
                service_order_detail_value = ServiceOrderDetail(
                    company_code=MECSA_COMPANY_CODE,
                    order_id=order_id,
                    order_type="TJ",
                    product_id=detail.tissue_id,
                    quantity_ordered=detail.quantity_ordered,
                    quantity_supplied=0,
                    price=detail.price,
                )
                service_order.detail.append(service_order_detail_value)

        await self.service_order_detail_repository.save_all(service_order.detail)

        return Success(ServiceOrderSchema.model_validate(service_order))

    async def anulate_weaving_service_order(
        self,
        order_id: str,
    ) -> Result[None, CustomException]:
        service_order = await self._read_service_order(
            order_id=order_id,
            order_type="TJ",
            include_detail=True,
        )

        if service_order.is_failure:
            return service_order

        service_order: ServiceOrder = service_order.value

        validation_result = await self._validate_update_service_order(
            service_order=service_order
        )

        if validation_result.is_failure:
            return validation_result

        service_order.status_flag = "A"

        for detail in service_order.detail:
            detail.status_flag = "A"

        await self.repository.save(service_order)
        await self.service_order_detail_repository.save_all(service_order.detail)

        return Success(None)

    async def is_updated_permission_weaving_service_order(
        self,
        order_id: str,
    ) -> Result[None, CustomException]:
        service_order = await self._read_service_order(
            order_id=order_id,
            order_type="TJ",
            include_detail=True,
        )

        if service_order.is_failure:
            return service_order

        service_order: ServiceOrder = service_order.value

        validation_result = await self._validate_update_service_order(
            service_order=service_order
        )

        if validation_result.is_failure:
            return validation_result

        return Success(None)
