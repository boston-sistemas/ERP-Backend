from sqlalchemy.ext.asyncio import AsyncSession

from src.core.constants import MECSA_COMPANY_CODE
from src.core.exceptions import CustomException
from src.core.repository import BaseRepository
from src.core.result import Result, Success
from src.core.utils import PERU_TIMEZONE, calculate_time
from src.operations.constants import (
    CANCELLED_SERVICE_ORDER_ID,
    CATEGORY_SERVICE_ORDER_ID,
    FINISHED_SERVICE_ORDER_ID,
    SERVICE_CODE_SUPPLIER_WEAVING,
    STARTED_SERVICE_ORDER_ID,
    UNSTARTED_SERVICE_ORDER_ID,
)
from src.operations.failures import (
    SERVICE_ORDER_ALREADY_ANULLED_FAILURE,
    SERVICE_ORDER_ALREADY_SUPPLIED_FAILURE,
    SERVICE_ORDER_NOT_FOUND_FAILURE,
    SERVICE_ORDER_STATUS_NOT_VALID_FAILURE,
    SERVICE_ORDER_SUPPLIER_NOT_ASSOCIATED_WITH_WEAVING_FAILURE,
)
from src.operations.models import (
    ServiceOrder,
    ServiceOrderDetail,
)
from src.operations.repositories import ServiceOrderRepository
from src.operations.schemas import (
    ServiceOrderCreateSchema,
    ServiceOrderDetailSchema,
    ServiceOrderFilterParams,
    ServiceOrderListSchema,
    ServiceOrderProgressReviewListSchema,
    ServiceOrderSchema,
    ServiceOrderUpdateSchema,
)
from src.security.services import ParameterService

from .fabric_service import FabricService
from .service_order_supply_service import ServiceOrderSupplyDetailService
from .supplier_service import SupplierService


# TODO: Refactor this service
class ServiceOrderService:
    def __init__(self, promec_db: AsyncSession, db: AsyncSession) -> None:
        self.promec_db = promec_db
        self.repository = ServiceOrderRepository(promec_db=promec_db)
        self.supplier_service = SupplierService(promec_db=promec_db)
        self.service_order_detail_repository = BaseRepository(
            model=ServiceOrderDetail, db=promec_db
        )
        self.parameter_service = ParameterService(db=db)
        self.fabric_service = FabricService(promec_db=promec_db, db=db)
        self.service_order_supply_service = ServiceOrderSupplyDetailService(
            promec_db=promec_db
        )

    async def read_service_orders(
        self,
        order_type: str,
        filter_params: ServiceOrderFilterParams = ServiceOrderFilterParams(),
        include_status: bool = False,
    ) -> Result[ServiceOrderListSchema, CustomException]:
        service_orders = await self.repository.find_service_orders_by_order_type(
            order_type=order_type,
            **filter_params.model_dump(),
            order_by=ServiceOrder.issue_date.desc(),
        )

        if include_status:
            for service_order in service_orders:
                # TODO: Make this better
                status = await self.parameter_service.read_parameter(
                    parameter_id=service_order.status_param_id
                )
                if status.is_failure:
                    service_order.status = None
                else:
                    service_order.status = status.value

                if filter_params.include_detail:
                    for detail in service_order.detail:
                        status = await self.parameter_service.read_parameter(
                            parameter_id=detail.status_param_id
                        )

                        if status.is_failure:
                            detail.status = None
                        else:
                            detail.status = status.value

        return Success(ServiceOrderListSchema(service_orders=service_orders))

    async def _read_service_order(
        self,
        order_id: str,
        order_type: str,
        include_detail: bool = False,
    ) -> Result[ServiceOrderSchema, CustomException]:
        service_order = (
            await self.repository.find_service_order_by_order_id_and_order_type(
                order_id=order_id,
                order_type=order_type,
                include_detail=include_detail,
            )
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
        )

        if service_order.is_failure:
            return service_order

        service_order = service_order.value

        if include_status:
            status = await self.parameter_service.read_parameter(
                parameter_id=service_order.status_param_id
            )

            if status.is_failure:
                service_order.status = None
            else:
                service_order.status = status.value

        if include_detail:
            for detail in service_order.detail:
                status = await self.parameter_service.read_parameter(
                    parameter_id=detail.status_param_id
                )

                if status.is_failure:
                    detail.status = None
                else:
                    detail.status = status.value

        return Success(ServiceOrderSchema.model_validate(service_order))

    async def _validate_service_order_data(
        self,
        data: ServiceOrderCreateSchema,
    ) -> Result[None, CustomException]:
        # TODO: This be done in the supplier service
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

    async def _validate_service_order_data_update(
        self,
        data: ServiceOrderUpdateSchema,
    ) -> Result[None, CustomException]:
        status = await self.parameter_service.read_parameter(
            parameter_id=data.status_param_id
        )

        if status.is_failure:
            return status

        if status.value.category_id != CATEGORY_SERVICE_ORDER_ID:
            return SERVICE_ORDER_STATUS_NOT_VALID_FAILURE

        return Success(None)

    async def _validate_service_order_detail_data(
        self,
        data: list[ServiceOrderDetailSchema],
    ) -> Result[None, CustomException]:
        for detail in data:
            fabric = await self.fabric_service.read_fabric(
                fabric_id=detail.fabric_id,
            )

            if fabric.is_failure:
                return fabric

        return Success(None)

    async def _validate_service_order_detail_data_update(
        self,
        data: list[ServiceOrderDetailSchema],
    ) -> Result[None, CustomException]:
        for detail in data:
            fabric = await self.fabric_service.read_fabric(
                fabric_id=detail.fabric_id,
            )

            if fabric.is_failure:
                return fabric

            status = await self.parameter_service.read_parameter(
                parameter_id=detail.status_param_id
            )

            if status.is_failure:
                return status

            if status.value.category_id != CATEGORY_SERVICE_ORDER_ID:
                return SERVICE_ORDER_STATUS_NOT_VALID_FAILURE
        return Success(None)

    async def create_weaving_service_order(
        self,
        form: ServiceOrderCreateSchema,
    ) -> Result[ServiceOrderSchema, CustomException]:
        validation_result = await self._validate_service_order_data(data=form)

        if validation_result.is_failure:
            return validation_result

        supplier = validation_result.value

        validation_result = await self._validate_service_order_detail_data(
            data=form.detail
        )

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
            user_id="DESA01",  # TODO: Set the current user's username as user_id for PROMEC
            flgatc="N",
            flgprt="N",
            status_param_id=UNSTARTED_SERVICE_ORDER_ID,
        )

        service_order_detail = []

        for detail in form.detail:
            service_order_detail_value = ServiceOrderDetail(
                company_code=MECSA_COMPANY_CODE,
                order_id=purchase_service_number,
                order_type=order_type,
                product_id=detail.fabric_id,
                quantity_ordered=detail.quantity_ordered,
                quantity_supplied=0,
                price=detail.price,
                status_param_id=UNSTARTED_SERVICE_ORDER_ID,
            )
            service_order_detail.append(service_order_detail_value)

        await self.repository.save(service_order, flush=True)

        service_order.detail = service_order_detail

        await self.service_order_detail_repository.save_all(service_order_detail)

        return Success(ServiceOrderSchema.model_validate(service_order))

    async def _delete_detail(
        self,
        service_order_detail: ServiceOrderDetail,
    ) -> None:
        await self.service_order_detail_repository.delete(
            service_order_detail, flush=True
        )

    async def _delete_service_order_detail(
        self,
        service_order_detail: list[ServiceOrderDetail],
        form: ServiceOrderUpdateSchema,
    ) -> list[ServiceOrderDetail]:
        fabric_ids = [detail.fabric_id for detail in form.detail]

        for detail in service_order_detail:
            if detail.product_id not in fabric_ids:
                await self._delete_detail(detail)
                service_order_detail.remove(detail)

        return service_order_detail

    async def _validate_update_service_order(
        self,
        service_order: ServiceOrder,
    ) -> Result[None, CustomException]:
        if service_order.status_param_id == CANCELLED_SERVICE_ORDER_ID:
            return SERVICE_ORDER_ALREADY_ANULLED_FAILURE

        if service_order.status_param_id == FINISHED_SERVICE_ORDER_ID:
            return SERVICE_ORDER_ALREADY_SUPPLIED_FAILURE

        for detail in service_order.detail:
            if detail.quantity_supplied > 0:
                return SERVICE_ORDER_ALREADY_SUPPLIED_FAILURE

        return Success(None)

    async def _find_service_order_detail(
        self,
        service_order_detail: list[ServiceOrderDetail],
        fabric_id: str,
    ) -> ServiceOrderDetail | None:
        for detail in service_order_detail:
            if detail.product_id == fabric_id:
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

        validation_result = await self._validate_service_order_data_update(data=form)
        if validation_result.is_failure:
            return validation_result

        validation_result = await self._validate_service_order_detail_data_update(
            data=form.detail
        )

        if validation_result.is_failure:
            return validation_result

        service_order.status_param_id = form.status_param_id

        service_order.detail = await self._delete_service_order_detail(
            service_order_detail=service_order.detail,
            form=form,
        )

        for detail in form.detail:
            service_order_detail_result = await self._find_service_order_detail(
                service_order_detail=service_order.detail,
                fabric_id=detail.fabric_id,
            )

            if service_order_detail_result is not None:
                service_order_detail_result.quantity_ordered = detail.quantity_ordered
                service_order_detail_result.price = detail.price
                service_order_detail_result.status_param_id = detail.status_param_id

            else:
                service_order_detail_value = ServiceOrderDetail(
                    company_code=MECSA_COMPANY_CODE,
                    order_id=order_id,
                    order_type="TJ",
                    product_id=detail.fabric_id,
                    quantity_ordered=detail.quantity_ordered,
                    quantity_supplied=0,
                    price=detail.price,
                    status_param_id=detail.status_param_id,
                )
                service_order.detail.append(service_order_detail_value)

        count_unsupplied = 0

        for detail in service_order.detail:
            if detail.status_param_id == STARTED_SERVICE_ORDER_ID:
                service_order.status_param_id = STARTED_SERVICE_ORDER_ID
                service_order.status_flag = "P"
                count_unsupplied += 1
                break

            if (
                detail.status_param_id != FINISHED_SERVICE_ORDER_ID
                or detail.status_param_id != CANCELLED_SERVICE_ORDER_ID
            ):
                count_unsupplied += 1

        if count_unsupplied > 0:
            service_order.status_param_id = STARTED_SERVICE_ORDER_ID
            service_order.status_flag = "P"
        else:
            service_order.status_param_id = FINISHED_SERVICE_ORDER_ID
            service_order.status_flag = "C"

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

        await self.repository.save(service_order, flush=True)
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

    async def update_quantity_supplied_by_fabric_id(
        self,
        order_id: str,
        fabric_id: str,
        quantity_supplied: int,
    ) -> Result[None, CustomException]:
        service_order = await self._read_service_order(
            order_id=order_id,
            order_type="TJ",
            include_detail=True,
        )

        if service_order.is_failure:
            return service_order

        service_order: ServiceOrder = service_order.value

        detail_amount = len(service_order.detail)
        count_unsupplied = 0

        for detail in service_order.detail:
            if detail.product_id == fabric_id:
                detail.quantity_supplied += quantity_supplied

                if detail.quantity_supplied >= detail.quantity_ordered:
                    detail.status_param_id = FINISHED_SERVICE_ORDER_ID

            if (
                detail.status_param_id == FINISHED_SERVICE_ORDER_ID
                or detail.status_param_id == CANCELLED_SERVICE_ORDER_ID
            ):
                count_unsupplied += 1

        if count_unsupplied == detail_amount:
            service_order.status_param_id = FINISHED_SERVICE_ORDER_ID
            service_order.status_flag = "C"

        await self.service_order_detail_repository.save_all(service_order.detail)
        await self.repository.save(service_order, flush=True)
        return Success(None)

    async def rollback_quantity_supplied_by_fabric_id(
        self,
        order_id: str,
        fabric_id: str,
        quantity_supplied: int,
    ) -> Result[None, CustomException]:
        service_order = await self._read_service_order(
            order_id=order_id,
            order_type="TJ",
            include_detail=True,
        )

        if service_order.is_failure:
            return service_order

        service_order: ServiceOrder = service_order.value

        count_unsupplied = 0

        for detail in service_order.detail:
            if detail.product_id == fabric_id:
                detail.quantity_supplied -= quantity_supplied

                if detail.quantity_supplied < detail.quantity_ordered:
                    detail.status_param_id = STARTED_SERVICE_ORDER_ID

            if (
                detail.status_param_id != FINISHED_SERVICE_ORDER_ID
                or detail.status_param_id != CANCELLED_SERVICE_ORDER_ID
            ):
                count_unsupplied += 1

        if count_unsupplied > 0:
            service_order.status_param_id = STARTED_SERVICE_ORDER_ID
            service_order.status_flag = "P"

        await self.service_order_detail_repository.save_all(service_order.detail)
        await self.repository.save(service_order, flush=True)
        return Success(None)

    async def read_service_orders_in_progress_review(
        self,
        period: int,
        limit: int = None,
        offset: int = None,
    ) -> Result[ServiceOrderProgressReviewListSchema, CustomException]:
        service_orders_progress = (
            await self.service_order_supply_service.read_service_orders_supply_stock(
                period=period,
                limit=limit,
                offset=offset,
            )
        )

        if service_orders_progress.is_failure:
            return service_orders_progress

        return Success(service_orders_progress.value)
