from datetime import date, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.constants import MECSA_COMPANY_CODE
from src.core.exceptions import CustomException
from src.core.repository import BaseRepository
from src.core.result import Result, Success
from src.core.utils import PERU_TIMEZONE, calculate_time
from src.operations.constants import (
    CANCELLED_SERVICE_ORDER_ID,
    ENTRY_DOCUMENT_CODE,
    ENTRY_MOVEMENT_TYPE,
    FINISHED_SERVICE_ORDER_ID,
    SERVICE_CODE_SUPPLIER_WEAVING,
    WEAVING_MOVEMENT_CODE,
    YARN_WEAVING_DISPATCH_DOCUMENT_CODE,
    YARN_WEAVING_DISPATCH_MOVEMENT_CODE,
    YARN_WEAVING_DISPATCH_MOVEMENT_TYPE,
    YARN_WEAVING_DISPATCH_STORAGE_CODE,
)
from src.operations.failures import (
    YARN_WEAVING_DISPATCH_ALREADY_ACCOUNTED_FAILURE,
    YARN_WEAVING_DISPATCH_ALREADY_ANULLED_FAILURE,
    YARN_WEAVING_DISPATCH_CONE_COUNT_MISMATCH_FAILURE,
    YARN_WEAVING_DISPATCH_FABRIC_NOT_ASSOCIATED_SERVICE_ORDER_FAILURE,
    YARN_WEAVING_DISPATCH_GROUP_ALREADY_DISPATCHED_FAILURE,
    YARN_WEAVING_DISPATCH_GROUP_ANULLED_FAILURE,
    YARN_WEAVING_DISPATCH_NOT_ADDRESS_ASSOCIATED_FAILURE,
    YARN_WEAVING_DISPATCH_NOT_FOUND_FAILURE,
    YARN_WEAVING_DISPATCH_PACKAGE_COUNT_MISMATCH_FAILURE,
    YARN_WEAVING_DISPATCH_SERVICE_ORDER_ALREADY_CANCELLED_FAILURE,
    YARN_WEAVING_DISPATCH_SERVICE_ORDER_ALREADY_FINISHED_FAILURE,
    YARN_WEAVING_DISPATCH_SUPPLIER_NOT_ASSOCIATED_FAILURE,
    YARN_WEAVING_DISPATCH_SUPPLIER_WITHOUT_STORAGE_FAILURE,
    YARN_WEAVING_DISPATCH_YARN_NOT_ASSOCIATED_FABRIC_FAILURE,
)
from src.operations.models import (
    Movement,
    MovementDetail,
    MovementDetailAux,
    MovementYarnOCHeavy,
    ServiceOrder,
    ServiceOrderSupplyDetail,
)
from src.operations.repositories import (
    YarnWeavingDispatchRepository,
)
from src.operations.schemas import (
    ServiceOrderSchema,
    SupplierSchema,
    YarnWeavingDispatchCreateSchema,
    YarnWeavingDispatchDetailCreateSchema,
    YarnWeavingDispatchFilterParams,
    YarnWeavingDispatchListSchema,
    YarnWeavingDispatchSchema,
    YarnWeavingDispatchUpdateSchema,
)
from src.operations.utils.movements.yarn_weaving_dispatch.pdf import generate_pdf

from .fabric_service import FabricService
from .movement_service import MovementService
from .series_service import (
    EntrySeries,
    YarnWeavingDispatchSeries,
)
from .service_order_service import ServiceOrderService
from .service_order_supply_service import ServiceOrderSupplyDetailService
from .supplier_service import SupplierService
from .yarn_purchase_entry_detail_heavy_service import (
    YarnPurchaseEntryDetailHeavyService,
)


class YarnWeavingDispatchService(MovementService):
    def __init__(self, promec_db: AsyncSession, db: AsyncSession) -> None:
        super().__init__(promec_db)
        self.repository = YarnWeavingDispatchRepository(promec_db)
        self.yarn_purchase_entry_detail_heavy_service = (
            YarnPurchaseEntryDetailHeavyService(promec_db=promec_db)
        )
        self.supplier_service = SupplierService(promec_db=promec_db)
        self.yarn_weaving_dispatch_series = YarnWeavingDispatchSeries(
            promec_db=promec_db
        )
        self.entry_series = EntrySeries(promec_db=promec_db)
        self.yarn_entry_detail_repository = BaseRepository(
            model=MovementDetail, db=promec_db
        )
        self.service_order_repository = BaseRepository(model=ServiceOrder, db=promec_db)
        self.service_order_supply_stock_repository = BaseRepository(
            model=ServiceOrderSupplyDetail, db=promec_db
        )
        self.service_order_supply_service = ServiceOrderSupplyDetailService(
            promec_db=promec_db
        )
        self.service_order_service = ServiceOrderService(promec_db=promec_db, db=db)
        self.fabric_service = FabricService(promec_db=promec_db, db=db)

    async def read_yarn_weaving_dispatches(
        self,
        filter_params: YarnWeavingDispatchFilterParams,
    ) -> Result[YarnWeavingDispatchListSchema, CustomException]:
        yarn_weaving_dispatches = await self.repository.find_yarn_weaving_dispatches(
            **filter_params.model_dump(exclude={"page"}),
            apply_unique=True,
        )

        return Success(
            YarnWeavingDispatchListSchema(
                yarn_weaving_dispatches=yarn_weaving_dispatches
            )
        )

    async def _read_yarn_weaving_dispatch(
        self,
        yarn_weaving_dispatch_number: str,
        period: int,
        include_detail: bool = False,
        include_detail_entry: bool = False,
    ) -> Result[YarnWeavingDispatchSchema, CustomException]:
        yarn_weaving_dispatch = (
            await self.repository.find_yarn_weaving_dispatch_by_dispatch_number(
                dispatch_number=yarn_weaving_dispatch_number,
                period=period,
                use_outer_joins=True,
                include_detail=include_detail,
                include_detail_entry=include_detail_entry,
            )
        )

        if yarn_weaving_dispatch is None:
            return YARN_WEAVING_DISPATCH_NOT_FOUND_FAILURE

        return Success(yarn_weaving_dispatch)

    async def read_yarn_weaving_dispatch(
        self,
        yarn_weaving_dispatch_number: str,
        period: int,
        include_detail: bool = False,
        include_detail_entry: bool = False,
    ) -> Result[YarnWeavingDispatchSchema, CustomException]:
        yarn_weaving_dispatch = await self._read_yarn_weaving_dispatch(
            yarn_weaving_dispatch_number=yarn_weaving_dispatch_number,
            period=period,
            include_detail=include_detail,
            include_detail_entry=include_detail_entry,
        )

        if yarn_weaving_dispatch.is_failure:
            return yarn_weaving_dispatch

        return Success(
            YarnWeavingDispatchSchema.model_validate(yarn_weaving_dispatch.value)
        )

    async def _validate_yarn_weaving_dispatch_data(
        self,
        data: YarnWeavingDispatchCreateSchema,
    ) -> Result[tuple[SupplierSchema, ServiceOrderSchema], CustomException]:
        service_order_result = await self.service_order_service.read_service_order(
            order_id=data.service_order_id,
            order_type="TJ",
            include_detail=True,
        )

        if service_order_result.is_failure:
            return service_order_result

        service_order = service_order_result.value

        if service_order.status_param_id == CANCELLED_SERVICE_ORDER_ID:
            return YARN_WEAVING_DISPATCH_SERVICE_ORDER_ALREADY_CANCELLED_FAILURE

        if service_order.status_param_id == FINISHED_SERVICE_ORDER_ID:
            return YARN_WEAVING_DISPATCH_SERVICE_ORDER_ALREADY_FINISHED_FAILURE

        supplier_result = await self.supplier_service.read_supplier(
            supplier_code=data.supplier_code,
            include_service=True,
            include_other_addresses=True,
        )

        if supplier_result.is_failure:
            return supplier_result

        supplier = supplier_result.value

        if supplier.storage_code == "":
            return YARN_WEAVING_DISPATCH_SUPPLIER_WITHOUT_STORAGE_FAILURE

        services = [service.service_code for service in supplier.services]
        if SERVICE_CODE_SUPPLIER_WEAVING not in services:
            return YARN_WEAVING_DISPATCH_SUPPLIER_NOT_ASSOCIATED_FAILURE

        if data.nrodir not in supplier.addresses.keys():
            return YARN_WEAVING_DISPATCH_NOT_ADDRESS_ASSOCIATED_FAILURE

        return Success((supplier, service_order))

    async def _validate_yarn_weaving_dispatch_update_data(
        self,
        data: YarnWeavingDispatchUpdateSchema,
        supplier_id: str,
    ) -> Result[tuple[SupplierSchema, ServiceOrderSchema], CustomException]:
        supplier_result = await self.supplier_service.read_supplier(
            supplier_code=supplier_id,
            include_other_addresses=True,
        )

        if supplier_result.is_failure:
            return supplier_result

        supplier = supplier_result.value

        if data.nrodir not in supplier.addresses.keys():
            return YARN_WEAVING_DISPATCH_NOT_ADDRESS_ASSOCIATED_FAILURE

        return Success(supplier)

    async def _validate_service_order_with_detail(
        self,
        service_order: ServiceOrderSchema,
        yarn_purchase_entry_detail_heavy: MovementYarnOCHeavy,
        fabric_id: str,
    ) -> Result[None, CustomException]:
        fabric_ids = [detail.fabric_id for detail in service_order.detail]
        if fabric_id not in fabric_ids:
            return YARN_WEAVING_DISPATCH_FABRIC_NOT_ASSOCIATED_SERVICE_ORDER_FAILURE

        fabric_result = await self.fabric_service.read_fabric(
            fabric_id=fabric_id,
            include_recipe=True,
        )
        if fabric_result.is_failure:
            return fabric_result

        fabric = fabric_result.value

        yarn_ids = [yarn.yarn_id for yarn in fabric.recipe]

        if yarn_purchase_entry_detail_heavy.yarn_id not in yarn_ids:
            return YARN_WEAVING_DISPATCH_YARN_NOT_ASSOCIATED_FABRIC_FAILURE

        return Success(None)

    async def _validate_yarn_weaving_dispatch_detail_data(
        self,
        data: list[YarnWeavingDispatchDetailCreateSchema],
        service_order: ServiceOrderSchema,
    ) -> Result[None, CustomException]:
        for detail in data:
            yarn_purchase_entry_detail_heavy_result = await self.yarn_purchase_entry_detail_heavy_service._read_yarn_purchase_entry_detail_heavy(
                ingress_number=detail.entry_number,
                item_number=detail.entry_item_number,
                group_number=detail.entry_group_number,
                period=detail.entry_period,
            )
            if yarn_purchase_entry_detail_heavy_result.is_failure:
                return yarn_purchase_entry_detail_heavy_result

            yarn_purchase_entry_detail_heavy = (
                yarn_purchase_entry_detail_heavy_result.value
            )

            detail._yarn_purchase_entry_heavy = yarn_purchase_entry_detail_heavy

            if yarn_purchase_entry_detail_heavy.status_flag == "A":
                return YARN_WEAVING_DISPATCH_GROUP_ANULLED_FAILURE

            if yarn_purchase_entry_detail_heavy.dispatch_status:
                return YARN_WEAVING_DISPATCH_GROUP_ALREADY_DISPATCHED_FAILURE

            validation_result = await self._validate_service_order_with_detail(
                service_order=service_order,
                yarn_purchase_entry_detail_heavy=yarn_purchase_entry_detail_heavy,
                fabric_id=detail.fabric_id,
            )

            if validation_result.is_failure:
                return validation_result

            validate_package = (
                yarn_purchase_entry_detail_heavy.packages_left - detail.package_count
            )
            validate_cones = (
                yarn_purchase_entry_detail_heavy.cones_left - detail.cone_count
            )

            if validate_package < 0:
                return YARN_WEAVING_DISPATCH_PACKAGE_COUNT_MISMATCH_FAILURE

            if validate_cones < 0:
                return YARN_WEAVING_DISPATCH_CONE_COUNT_MISMATCH_FAILURE

        return Success(data)

    async def _create_yarn_entry_with_dispatch(
        self,
        storage_code: str,
        period: int,
        entry_number: str,
        dispatch_number: str,
        current_time: datetime,
        supplier: SupplierSchema,
        purchase_service_number: str,
        detail: list[YarnWeavingDispatchDetailCreateSchema],
    ) -> Result[None, CustomException]:
        creation_date = current_time.date()
        creation_time = current_time.strftime("%H:%M:%S")

        reference_code = "G/R"
        reference_document = "O/S"

        supplier_code = supplier.code
        supplier_name = supplier.name

        entry_movement = Movement(
            company_code=MECSA_COMPANY_CODE,
            storage_code=storage_code,
            movement_type=ENTRY_MOVEMENT_TYPE,
            movement_code=WEAVING_MOVEMENT_CODE,
            document_code=ENTRY_DOCUMENT_CODE,
            document_number=entry_number,
            period=period,
            creation_date=creation_date,
            creation_time=creation_time,
            clfaux="_PRO",
            auxiliary_code=supplier_code,
            reference_code=reference_code,
            reference_number1=dispatch_number,
            reference_number2=purchase_service_number,
            status_flag="P",
            user_id="DESA01",
            auxiliary_name=supplier_name,
            reference_document=reference_document,
            origmov="A",
            serial_number="001",
            printed_flag="N",
            flgact="N",
            flgtras=False,
            flgreclamo="N",
            flgsit="A",
            servadi="N",
            tarfservadi=0,
            flgcbd="N",
            origin_station="SERVIDORDESA",
            undpesobrutototal="KGM",
            transaction_mode="02",
            intentosenvele=0,
        )

        entry_detail = []

        for i in range(len(detail)):
            entry_detail.append(
                MovementDetail(
                    company_code=MECSA_COMPANY_CODE,
                    storage_code=storage_code,
                    movement_type=ENTRY_MOVEMENT_TYPE,
                    movement_code=WEAVING_MOVEMENT_CODE,
                    document_code=ENTRY_DOCUMENT_CODE,
                    document_number=entry_number,
                    item_number=i + 1,
                    period=period,
                    creation_date=creation_date,
                    creation_time=creation_time,
                    product_code1=detail[i]._yarn_purchase_entry_heavy.yarn_id,
                    unit_code="KG",
                    factor=1,
                    mecsa_weight=detail[i].net_weight,
                    precto=0,
                    impcto=0,
                    reference_code="G/R",
                    reference_number=dispatch_number,
                    # impmn1=,
                    # impmn2=,
                    # stkgen=,
                    # stkalm=,
                    # ctomn1=,
                    # ctomn2=,
                    detdoc=detail[i].entry_number,
                    entry_item_number=detail[i].item_number,
                )
            )

            product_inventory_service = await self._read_or_create_product_inventory(
                product_code1=detail[i]._yarn_purchase_entry_heavy.yarn_id,
                period=period,
                storage_code=storage_code,
                enable_create=True,
            )
            if product_inventory_service.is_failure:
                return product_inventory_service

            update_result = await self.product_inventory_service.update_current_stock(
                product_code1=detail[i]._yarn_purchase_entry_heavy.yarn_id,
                period=period,
                storage_code=storage_code,
                new_stock=detail[i].net_weight,
            )
            if update_result.is_failure:
                return update_result

        creation_result = await self.save_movement(
            movement=entry_movement,
            movement_detail=entry_detail,
        )

        if creation_result.is_failure:
            return creation_result

        return Success(None)

    async def _anulate_yarn_entry_with_dispatch(
        self,
        entry_number: str,
        period: int,
        storage_code: str,
    ) -> Result[None, CustomException]:
        entry_movement_result = await self.read_movement(
            document_number=entry_number,
            period=period,
            storage_code=storage_code,
            movement_type=ENTRY_MOVEMENT_TYPE,
            movement_code=WEAVING_MOVEMENT_CODE,
            document_code=ENTRY_DOCUMENT_CODE,
            include_detail=True,
        )
        if not entry_movement_result:
            return Success(None)

        entry_movement = entry_movement_result.value

        entry_movement.status_flag = "A"

        for detail in entry_movement.detail:
            detail.status_flag = "A"

        update_result = await self.save_movement(
            movement=entry_movement,
            movement_detail=entry_movement.detail,
        )

        if update_result.is_failure:
            return update_result

        return Success(None)

    async def _create_yarn_entry_detail_with_dispatch(
        self,
        storage_code: str,
        period: int,
        dispatch_number: str,
        entry_item_number_supplier: int,
        current_time: datetime,
        supplier: SupplierSchema,
        purchase_service_number: str,
        entry_number: str,
        detail: YarnWeavingDispatchUpdateSchema,
    ) -> Result[None, CustomException]:
        creation_date = current_time.date()
        creation_time = current_time.strftime("%H:%M:%S")
        entry_detail = []
        entry_detail.append(
            MovementDetail(
                company_code=MECSA_COMPANY_CODE,
                storage_code=storage_code,
                movement_type=ENTRY_MOVEMENT_TYPE,
                movement_code=WEAVING_MOVEMENT_CODE,
                document_code=ENTRY_DOCUMENT_CODE,
                document_number=entry_number,
                item_number=entry_item_number_supplier,
                period=period,
                creation_date=creation_date,
                creation_time=creation_time,
                product_code1=detail._yarn_purchase_entry_heavy.yarn_id,
                unit_code="KG",
                factor=1,
                mecsa_weight=detail.net_weight,
                precto=0,
                impcto=0,
                reference_code="G/R",
                reference_number=dispatch_number,
                # impmn1=,
                # impmn2=,
                # stkgen=,
                # stkalm=,
                # ctomn1=,
                # ctomn2=,
                detdoc=detail.entry_number,
                entry_item_number=detail.item_number,
            )
        )

        product_inventory_service = await self._read_or_create_product_inventory(
            product_code1=detail._yarn_purchase_entry_heavy.yarn_id,
            period=period,
            storage_code=storage_code,
            enable_create=True,
        )
        if product_inventory_service.is_failure:
            return product_inventory_service

        update_result = await self.product_inventory_service.update_current_stock(
            product_code1=detail._yarn_purchase_entry_heavy.yarn_id,
            period=period,
            storage_code=storage_code,
            new_stock=detail.net_weight,
        )
        if update_result.is_failure:
            return update_result

        creation_result = await self.save_movement(
            movement_detail=entry_detail,
        )

        if creation_result.is_failure:
            return creation_result

        return Success(None)

    async def _update_yarn_entry_detail_with_dispatch(
        self,
        storage_code: str,
        period: int,
        entry_number: str,
        detail: YarnWeavingDispatchUpdateSchema,
    ) -> Result[None, CustomException]:
        filter = (
            (MovementDetail.document_number == entry_number)
            & (MovementDetail.company_code == MECSA_COMPANY_CODE)
            & (MovementDetail.storage_code == storage_code)
            & (MovementDetail.movement_type == ENTRY_MOVEMENT_TYPE)
            & (MovementDetail.movement_code == WEAVING_MOVEMENT_CODE)
            & (MovementDetail.document_code == ENTRY_DOCUMENT_CODE)
            & (MovementDetail.entry_item_number == detail.item_number)
            & (MovementDetail.period == period)
        )

        yarn_entry_detail = await self.yarn_entry_detail_repository.find(filter=filter)

        if yarn_entry_detail is not None:
            yarn_entry_detail.product_code1 = detail._yarn_purchase_entry_heavy.yarn_id
            yarn_entry_detail.mecsa_weight = detail.net_weight

        update_result = await self.product_inventory_service.update_current_stock(
            product_code1=detail._yarn_purchase_entry_heavy.yarn_id,
            period=period,
            storage_code=storage_code,
            new_stock=detail.net_weight,
        )
        if update_result.is_failure:
            return update_result

        yarn_entry_detail = [yarn_entry_detail]
        creation_result = await self.save_movement(
            movement_detail=yarn_entry_detail,
        )
        if creation_result.is_failure:
            return creation_result

        return Success(None)

    async def anulate_service_order(
        self,
        service_order_number: str,
    ) -> Result[None, CustomException]:
        filter = (
            (ServiceOrder.company_code == MECSA_COMPANY_CODE)
            & (ServiceOrder.service_order_type == "TJ")
            & (ServiceOrder.service_order_number == service_order_number)
        )

        service_order = await self.service_order_repository.find(filter=filter)

        if service_order is not None:
            service_order.status_flag = "A"

            await self.service_order_repository.save(service_order)

        return Success(None)

    async def _upsert_service_order_supply_stock(
        self,
        period: int,
        yarn_id: str,
        fabric_id: str,
        supplier_yarn_id: str,
        service_order_number: str,
        storage_code: str,
        quantity: float,
        supplier_id: str,
        issue_date: date,
    ) -> Result[None, CustomException]:
        # stock_service_orders_result = await self.service_order_supply_service._read_max_item_number_by_product_and_service_order(
        #     product_id=yarn_id,
        #     period=period,
        #     storage_code=storage_code,
        #     service_order_id=service_order_number,
        # )
        #
        # if stock_service_orders_result.is_failure:
        #     return stock_service_orders_result
        #
        # item_number = stock_service_orders_result.value

        service_order_supply_stock = ServiceOrderSupplyDetail(
            company_code=MECSA_COMPANY_CODE,
            period=period,
            product_code2=fabric_id,
            product_code1=yarn_id,
            # item_number=item_number + 1,
            reference_number=service_order_number,
            storage_code=storage_code,
            current_stock=quantity,
            provided_quantity=quantity,
            status_flag="P",
            supplier_code=supplier_id,
            creation_date=issue_date,
            pormer=0,
            quantity_received=0,
            quantity_dispatched=quantity,
            supplier_yarn_id=supplier_yarn_id,
        )

        upsert_result = (
            await self.service_order_supply_service.upsert_service_order_supply_stock(
                service_order_supply_stock=service_order_supply_stock,
            )
        )
        if upsert_result.is_failure:
            return upsert_result

        return Success(upsert_result.value)

    async def create_yarn_weaving_dispatch(
        self,
        form: YarnWeavingDispatchCreateSchema,
    ) -> Result[None, CustomException]:
        current_time = calculate_time(tz=PERU_TIMEZONE)
        validation_result = await self._validate_yarn_weaving_dispatch_data(data=form)

        if validation_result.is_failure:
            return validation_result

        supplier = validation_result.value[0]
        service_order = validation_result.value[1]

        validation_result = await self._validate_yarn_weaving_dispatch_detail_data(
            data=form.detail, service_order=service_order
        )

        if validation_result.is_failure:
            return validation_result

        form.detail = validation_result.value

        dispatch_number = await self.yarn_weaving_dispatch_series.next_number()

        creation_date = current_time.date()
        creation_time = current_time.strftime("%H:%M:%S")
        current_period = current_time.year
        service_order_id = service_order.id

        entry_number = await self.entry_series.next_number()

        yarn_weaving_dispatch = Movement(
            company_code=MECSA_COMPANY_CODE,
            storage_code=YARN_WEAVING_DISPATCH_STORAGE_CODE,
            movement_type=YARN_WEAVING_DISPATCH_MOVEMENT_TYPE,
            movement_code=YARN_WEAVING_DISPATCH_MOVEMENT_CODE,
            document_code=YARN_WEAVING_DISPATCH_DOCUMENT_CODE,
            document_number=dispatch_number,
            period=current_period,
            creation_date=creation_date,
            creation_time=creation_time,
            document_note=form.document_note,
            clfaux="_PRO",
            auxiliary_code=form.supplier_code,
            reference_code="P/I",
            reference_number1=entry_number,
            status_flag="P",
            user_id="DESA01",
            auxiliary_name=supplier.name,
            reference_document="O/S",
            reference_number2=service_order_id,
            origmov="A",
            transporter_code="080",
            serial_number="104",
            printed_flag="N",
            flgact="N",
            nrodir1="000",
            transaction_motive="17",
            flgreclamo="N",
            flgsit="A",
            servadi="N",
            tarfservadi=0,
            flgcbd="N",
            nrodir2=form.nrodir,
            origin_station="SERVIDORDESA",
            flgele="N",
            prefele="T",
            undpesobrutototal="KGM",
            transaction_mode="01",
        )

        yarn_weaving_dispatch_detail = []
        yarn_weaving_dispatch_detail_aux = []

        # print("------------------------")
        for detail in form.detail:
            creation_result = await self._upsert_service_order_supply_stock(
                period=current_period,
                yarn_id=detail._yarn_purchase_entry_heavy.yarn_id,
                fabric_id=detail.fabric_id,
                supplier_yarn_id=detail._yarn_purchase_entry_heavy.supplier_yarn_id,
                service_order_number=service_order_id,
                storage_code=supplier.storage_code,
                quantity=detail.net_weight,
                supplier_id=supplier.code,
                issue_date=creation_date,
            )
            if creation_result.is_failure:
                return creation_result

            service_order_supply_detail: ServiceOrderSupplyDetail = (
                creation_result.value
            )

            yarn_weaving_dispatch_detail_value = MovementDetail(
                company_code=MECSA_COMPANY_CODE,
                storage_code=YARN_WEAVING_DISPATCH_STORAGE_CODE,
                movement_type=YARN_WEAVING_DISPATCH_MOVEMENT_TYPE,
                movement_code=YARN_WEAVING_DISPATCH_MOVEMENT_CODE,
                document_code=YARN_WEAVING_DISPATCH_DOCUMENT_CODE,
                document_number=dispatch_number,
                item_number=detail.item_number,
                period=current_period,
                creation_date=creation_date,
                creation_time=creation_time,
                product_code1=detail._yarn_purchase_entry_heavy.yarn_id,
                unit_code="KG",
                factor=1,
                mecsa_weight=detail.net_weight,
                precto=0,
                impcto=0,
                reference_code="P/I",
                reference_number=detail.entry_number,
                # impmn1=,
                # impmn2=,
                # stkgen=,
                # stkalm=,
                # ctomn1=,
                # ctomn2=,
                nroreq=service_order_id,
                status_flag="P",
                entry_group_number=detail.entry_group_number,
                entry_item_number=detail.entry_item_number,
                entry_period=detail.entry_period,
                item_number_supply=service_order_supply_detail.item_number,
                product_code2=detail.fabric_id,
            )

            yarn_weaving_dispatch_detail_aux_value = MovementDetailAux(
                company_code=MECSA_COMPANY_CODE,
                document_code=YARN_WEAVING_DISPATCH_DOCUMENT_CODE,
                document_number=dispatch_number,
                item_number=detail.item_number,
                period=current_period,
                product_code1=detail._yarn_purchase_entry_heavy.yarn_id,
                unit_code="KG",
                factor=1,
                reference_code="P/I",
                reference_number=detail.entry_number,
                creation_date=creation_date,
                mecsa_weight=detail.net_weight,
                guide_net_weight=detail.gross_weight,
                guide_cone_count=detail.cone_count,
                guide_package_count=detail.package_count,
                group_number=detail.entry_group_number,
            )

            yarn_weaving_dispatch_detail_value.detail_aux = (
                yarn_weaving_dispatch_detail_aux_value
            )
            yarn_weaving_dispatch_detail_value.movement_ingress = (
                detail._yarn_purchase_entry_heavy
            )
            yarn_weaving_dispatch_detail.append(yarn_weaving_dispatch_detail_value)
            yarn_weaving_dispatch_detail_aux.append(
                yarn_weaving_dispatch_detail_aux_value
            )

            update_yarn_entry_detail_heavy_result = await self.yarn_purchase_entry_detail_heavy_service.update_yarn_purchase_entry_detail_heavy_by_yarn_dispatch(
                entry_number=detail.entry_number,
                item_number=detail.entry_item_number,
                group_number=detail.entry_group_number,
                period=detail.entry_period,
                cone_count=detail.cone_count,
                package_count=detail.package_count,
                dispatch_number=dispatch_number,
            )

            if update_yarn_entry_detail_heavy_result.is_failure:
                return update_yarn_entry_detail_heavy_result

            update_result = await self.product_inventory_service.update_current_stock(
                product_code1=detail._yarn_purchase_entry_heavy.yarn_id,
                period=current_period,
                storage_code=YARN_WEAVING_DISPATCH_STORAGE_CODE,
                new_stock=-detail.net_weight,
            )

            if update_result.is_failure:
                return update_result

        creation_result = await self.save_movement(
            movement=yarn_weaving_dispatch,
            movement_detail=yarn_weaving_dispatch_detail,
            movememt_detail_aux=yarn_weaving_dispatch_detail_aux,
        )
        if creation_result.is_failure:
            return creation_result

        yarn_weaving_dispatch.detail = yarn_weaving_dispatch_detail

        creation_result = await self._create_yarn_entry_with_dispatch(
            storage_code=supplier.storage_code,
            period=current_period,
            entry_number=entry_number,
            dispatch_number=dispatch_number,
            current_time=current_time,
            supplier=supplier,
            purchase_service_number=service_order_id,
            detail=form.detail,
        )

        if creation_result.is_failure:
            return creation_result

        return Success(YarnWeavingDispatchSchema.model_validate(yarn_weaving_dispatch))

    async def _validate_update_yarn_weaving_dispatch(
        self,
        yarn_weaving_dispatch: Movement,
    ) -> Result[None, CustomException]:
        if yarn_weaving_dispatch.status_flag == "A":
            return YARN_WEAVING_DISPATCH_ALREADY_ANULLED_FAILURE

        if yarn_weaving_dispatch.flgcbd == "S":
            return YARN_WEAVING_DISPATCH_ALREADY_ACCOUNTED_FAILURE

        # //! Validar si se puede anular el ingreso de insumos

        return Success(None)

    async def _delete_detail(
        self,
        yarn_weaving_dispatch_detail: MovementDetail,
        entry_number: str,
        supplier: SupplierSchema,
    ) -> Result[None, CustomException]:
        filter = (
            (MovementDetail.document_number == entry_number)
            & (MovementDetail.company_code == MECSA_COMPANY_CODE)
            & (MovementDetail.storage_code == supplier.storage_code)
            & (MovementDetail.movement_type == ENTRY_MOVEMENT_TYPE)
            & (MovementDetail.movement_code == WEAVING_MOVEMENT_CODE)
            & (MovementDetail.document_code == ENTRY_DOCUMENT_CODE)
            & (
                MovementDetail.entry_item_number
                == yarn_weaving_dispatch_detail.item_number
            )
            & (MovementDetail.period == yarn_weaving_dispatch_detail.period)
        )

        yarn_entry_detail = await self.yarn_entry_detail_repository.find(filter=filter)

        # delete_result = await self.service_order_supply_service.delete_service_order_supply_stock(
        #     product_code1=yarn_weaving_dispatch_detail.product_code1,
        #     period=yarn_weaving_dispatch_detail.period,
        #     storage_code=supplier.storage_code,
        #     reference_number=yarn_weaving_dispatch_detail.nroreq,
        #     item_number=yarn_weaving_dispatch_detail.entry_item_number,
        # )
        #
        # if delete_result.is_failure:
        #     return delete_result

        movement_detail = [yarn_entry_detail, yarn_weaving_dispatch_detail]

        delete_result = await self.delete_movement(
            movement_detail=movement_detail,
            movememt_detail_aux=[yarn_weaving_dispatch_detail.detail_aux],
        )
        if delete_result.is_failure:
            return delete_result

        return Success(None)

    async def _delete_yarn_weaving_dispatch_detail(
        self,
        yarn_weaving_dispatch_detail: list[MovementDetail],
        supplier: SupplierSchema,
        entry_number: str,
        form: YarnWeavingDispatchUpdateSchema,
    ) -> Result[list[MovementDetail], CustomException]:
        item_numbers = [detail.item_number for detail in form.detail]
        yarn_weaving_dispatch_detail_result = []
        for detail in yarn_weaving_dispatch_detail:
            if detail.item_number not in item_numbers:
                delete_result = await self._delete_detail(
                    yarn_weaving_dispatch_detail=detail,
                    entry_number=entry_number,
                    supplier=supplier,
                )
                if delete_result.is_failure:
                    return delete_result
            else:
                yarn_weaving_dispatch_detail_result.append(detail)

        return Success(yarn_weaving_dispatch_detail_result)

    async def _find_yarn_weaving_dispatch_detail(
        self,
        yarn_weaving_dispatch_detail: list[MovementDetail],
        item_number: int,
    ) -> MovementDetail | None:
        for detail in yarn_weaving_dispatch_detail:
            if detail.item_number == item_number:
                return detail

        return None

    async def _find_yarn_weaving_dispatch_detail_aux(
        self,
        yarn_weaving_dispatch_detail_aux: list[MovementDetail],
        item_number: int,
    ) -> MovementDetailAux | None:
        for detail in yarn_weaving_dispatch_detail_aux:
            if detail.detail_aux.item_number == item_number:
                return detail.detail_aux
        return None

    async def rollback_yarn_weaving_dispatch(
        self,
        yarn_weaving_dispatch: Movement,
    ) -> Result[None, CustomException]:
        supplier_result = await self.supplier_service.read_supplier(
            supplier_code=yarn_weaving_dispatch.auxiliary_code,
        )
        if supplier_result.is_failure:
            return supplier_result

        supplier = supplier_result.value

        for detail in yarn_weaving_dispatch.detail:
            rollback_result = (
                await self.product_inventory_service.rollback_currents_stock(
                    product_code1=detail.product_code1,
                    period=detail.period,
                    storage_code=supplier.storage_code,
                    quantity=detail.mecsa_weight,
                )
            )
            if rollback_result.is_failure:
                return rollback_result

            rollback_result = (
                await self.product_inventory_service.rollback_currents_stock(
                    product_code1=detail.product_code1,
                    period=detail.period,
                    storage_code=YARN_WEAVING_DISPATCH_STORAGE_CODE,
                    quantity=-detail.mecsa_weight,
                )
            )
            if rollback_result.is_failure:
                return rollback_result

            rollback_result = await self.yarn_purchase_entry_detail_heavy_service.rollback_yarn_purchase_entry_detail_heavy_by_yarn_dispatch(
                package_count=detail.detail_aux.guide_package_count,
                cone_count=detail.detail_aux.guide_cone_count,
                item_number=detail.entry_item_number,
                group_number=detail.entry_group_number,
                entry_number=detail.reference_number,
                period=detail.entry_period,
            )
            if rollback_result.is_failure:
                return rollback_result

            rollback_result = (
                await self.service_order_supply_service.rollback_current_stock(
                    storage_code=supplier.storage_code,
                    reference_number=detail.nroreq,
                    item_number=detail.item_number_supply,
                    quantity=detail.mecsa_weight,
                )
            )
            if rollback_result.is_failure:
                return rollback_result

        return Success(None)

    async def update_yarn_weaving_dispatch(
        self,
        yarn_weaving_dispatch_number: str,
        period: int,
        form: YarnWeavingDispatchUpdateSchema,
    ) -> Result[None, CustomException]:
        yarn_weaving_dispatch_result = await self._read_yarn_weaving_dispatch(
            yarn_weaving_dispatch_number=yarn_weaving_dispatch_number,
            period=period,
            include_detail=True,
            include_detail_entry=True,
        )
        if yarn_weaving_dispatch_result.is_failure:
            return yarn_weaving_dispatch_result

        current_time = calculate_time(tz=PERU_TIMEZONE)

        yarn_weaving_dispatch: Movement = yarn_weaving_dispatch_result.value
        self.repository.expunge(yarn_weaving_dispatch)
        rollback_result = await self.rollback_yarn_weaving_dispatch(
            yarn_weaving_dispatch=yarn_weaving_dispatch
        )
        if rollback_result.is_failure:
            return rollback_result

        validation_result = await self._validate_update_yarn_weaving_dispatch(
            yarn_weaving_dispatch=yarn_weaving_dispatch
        )

        if validation_result.is_failure:
            return validation_result

        validation_result = await self._validate_yarn_weaving_dispatch_update_data(
            data=form, supplier_id=yarn_weaving_dispatch.auxiliary_code
        )

        if validation_result.is_failure:
            return validation_result

        supplier = validation_result.value

        service_order_result = await self.service_order_service.read_service_order(
            order_id=yarn_weaving_dispatch.reference_number2,
            order_type="TJ",
            include_detail=True,
        )
        if service_order_result.is_failure:
            return service_order_result

        service_order = service_order_result.value
        validation_result = await self._validate_yarn_weaving_dispatch_detail_data(
            data=form.detail,
            service_order=service_order,
        )
        if validation_result.is_failure:
            return validation_result

        form.detail = validation_result.value

        delete_result = await self._delete_yarn_weaving_dispatch_detail(
            yarn_weaving_dispatch_detail=yarn_weaving_dispatch.detail,
            supplier=supplier,
            entry_number=yarn_weaving_dispatch.reference_number1,
            form=form,
        )

        if delete_result.is_failure:
            return delete_result

        yarn_weaving_dispatch.detail = delete_result.value

        yarn_weaving_dispatch_detail = []
        yarn_weaving_dispatch_detail_aux = []

        entry_item_number_supplier = (
            await self.repository.find_max_item_number_by_movement(
                storage_code=supplier.storage_code,
                movement_type=ENTRY_MOVEMENT_TYPE,
                movement_code=WEAVING_MOVEMENT_CODE,
                document_code=ENTRY_DOCUMENT_CODE,
                document_number=yarn_weaving_dispatch.reference_number1,
                period=period,
            )
        )

        for detail in form.detail:
            yarn_weaving_dispatch_detail_result = (
                await self._find_yarn_weaving_dispatch_detail(
                    yarn_weaving_dispatch_detail=yarn_weaving_dispatch.detail,
                    item_number=detail.item_number,
                )
            )

            yarn_weaving_dispatch_detail_aux_result = (
                await self._find_yarn_weaving_dispatch_detail_aux(
                    yarn_weaving_dispatch_detail_aux=yarn_weaving_dispatch.detail,
                    item_number=detail.item_number,
                )
            )

            if yarn_weaving_dispatch_detail_result is not None:
                yarn_weaving_dispatch_detail_result.mecsa_weight = detail.net_weight
                yarn_weaving_dispatch_detail_result.product_code1 = (
                    detail._yarn_purchase_entry_heavy.yarn_id
                )

                update_result = (
                    await self.product_inventory_service.update_current_stock(
                        product_code1=detail._yarn_purchase_entry_heavy.yarn_id,
                        period=period,
                        storage_code=YARN_WEAVING_DISPATCH_STORAGE_CODE,
                        new_stock=-detail.net_weight,
                    )
                )
                if update_result.is_failure:
                    return update_result

                update_result = await self._update_yarn_entry_detail_with_dispatch(
                    storage_code=supplier.storage_code,
                    period=period,
                    entry_number=yarn_weaving_dispatch.reference_number1,
                    detail=detail,
                )
                if update_result.is_failure:
                    return update_result

                # //! Liquidacion

                # await self.service_order_supply_service.update_current_stock(
                #     product_code1=yarn_weaving_dispatch_detail_result.product_code1,
                #     period=yarn_weaving_dispatch_detail_result.period,
                #     storage_code=supplier.storage_code,
                #     reference_number=yarn_weaving_dispatch_detail_result.nroreq,
                #     item_number=yarn_weaving_dispatch_detail_result.entry_item_number,
                #     new_stock=detail.net_weight,
                # )
                update_result = await self.yarn_purchase_entry_detail_heavy_service.update_yarn_purchase_entry_detail_heavy_by_yarn_dispatch(
                    entry_number=yarn_weaving_dispatch_detail_result.reference_number,
                    item_number=yarn_weaving_dispatch_detail_result.entry_item_number,
                    group_number=yarn_weaving_dispatch_detail_result.entry_group_number,
                    period=yarn_weaving_dispatch_detail_result.entry_period,
                    cone_count=detail.cone_count,
                    package_count=detail.package_count,
                    dispatch_number=yarn_weaving_dispatch_number,
                )
                if update_result.is_failure:
                    return update_result

                yarn_weaving_dispatch_detail_aux_result.guide_net_weight = (
                    detail.gross_weight
                )
                yarn_weaving_dispatch_detail_aux_result.guide_cone_count = (
                    detail.cone_count
                )
                yarn_weaving_dispatch_detail_aux_result.guide_package_count = (
                    detail.package_count
                )
                yarn_weaving_dispatch_detail_aux_result.mecsa_weight = detail.net_weight

                yarn_weaving_dispatch_detail_result.detail_aux = (
                    yarn_weaving_dispatch_detail_aux_result
                )

                yarn_weaving_dispatch_detail.append(yarn_weaving_dispatch_detail_result)
                yarn_weaving_dispatch_detail_aux.append(
                    yarn_weaving_dispatch_detail_aux_result
                )

            else:
                yarn_weaving_dispatch_detail_result = MovementDetail(
                    company_code=MECSA_COMPANY_CODE,
                    storage_code=YARN_WEAVING_DISPATCH_STORAGE_CODE,
                    movement_type=YARN_WEAVING_DISPATCH_MOVEMENT_TYPE,
                    movement_code=YARN_WEAVING_DISPATCH_MOVEMENT_CODE,
                    document_code=YARN_WEAVING_DISPATCH_DOCUMENT_CODE,
                    document_number=yarn_weaving_dispatch_number,
                    item_number=detail.item_number,
                    period=period,
                    creation_date=yarn_weaving_dispatch.creation_date,
                    creation_time=yarn_weaving_dispatch.creation_time,
                    product_code1=detail._yarn_purchase_entry_heavy.yarn_id,
                    unit_code="KG",
                    factor=1,
                    mecsa_weight=detail.net_weight,
                    precto=0,
                    impcto=0,
                    reference_code="P/I",
                    reference_number=detail.entry_number,
                    # impmn1=,
                    # impmn2=,
                    # stkgen=,
                    # stkalm=,
                    # ctomn1=,
                    # ctomn2=,
                    nroreq=yarn_weaving_dispatch.reference_number2,
                    status_flag="P",
                    entry_group_number=detail.entry_group_number,
                    entry_item_number=detail.entry_item_number,
                    entry_period=detail.entry_period,
                    product_code2=detail.fabric_id,
                )

                yarn_weaving_dispatch_detail_aux_result = MovementDetailAux(
                    company_code=MECSA_COMPANY_CODE,
                    document_code=YARN_WEAVING_DISPATCH_DOCUMENT_CODE,
                    document_number=yarn_weaving_dispatch_number,
                    item_number=detail.item_number,
                    period=period,
                    product_code1=detail._yarn_purchase_entry_heavy.yarn_id,
                    unit_code="KG",
                    factor=1,
                    reference_code="P/I",
                    reference_number=detail.entry_number,
                    creation_date=yarn_weaving_dispatch.creation_date,
                    mecsa_weight=detail.net_weight,
                    guide_net_weight=detail.gross_weight,
                    guide_cone_count=detail.cone_count,
                    guide_package_count=detail.package_count,
                    group_number=detail.entry_group_number,
                )

                # //! Liquidacion
                # await self.create_stock_service_order(
                #     period=period,
                #     yarn_id=detail._yarn_purchase_entry_heavy.yarn_id,
                #     supplier_yarn_id=detail._yarn_purchase_entry_heavy.supplier_yarn_id,
                #     service_order_number=yarn_weaving_dispatch.reference_number2,
                #     storage_code=supplier.storage_code,
                #     quantity=detail.net_weight,
                #     supplier_code=supplier.code,
                #     issue_date=creation_date,
                #     dispatch_number=yarn_weaving_dispatch_number,
                # )
                update_result = (
                    await self.product_inventory_service.update_current_stock(
                        product_code1=detail._yarn_purchase_entry_heavy.yarn_id,
                        period=period,
                        storage_code=YARN_WEAVING_DISPATCH_STORAGE_CODE,
                        new_stock=-detail.net_weight,
                    )
                )
                if update_result.is_failure:
                    return update_result

                update_result = await self.yarn_purchase_entry_detail_heavy_service.update_yarn_purchase_entry_detail_heavy_by_yarn_dispatch(
                    entry_number=detail.entry_number,
                    item_number=detail.entry_item_number,
                    group_number=detail.entry_group_number,
                    period=detail.entry_period,
                    cone_count=detail.cone_count,
                    package_count=detail.package_count,
                    dispatch_number=yarn_weaving_dispatch_number,
                )

                if update_result.is_failure:
                    return update_result

                creation_result = await self._create_yarn_entry_detail_with_dispatch(
                    storage_code=supplier.storage_code,
                    period=period,
                    dispatch_number=yarn_weaving_dispatch_number,
                    entry_item_number_supplier=entry_item_number_supplier,
                    current_time=current_time,
                    supplier=supplier,
                    purchase_service_number=yarn_weaving_dispatch.reference_number2,
                    entry_number=yarn_weaving_dispatch.reference_number1,
                    detail=detail,
                )

                if creation_result.is_failure:
                    return creation_result

                entry_item_number_supplier += 1

                yarn_weaving_dispatch_detail_result.detail_aux = (
                    yarn_weaving_dispatch_detail_aux_result
                )

                yarn_weaving_dispatch_detail.append(yarn_weaving_dispatch_detail_result)
                yarn_weaving_dispatch_detail_aux.append(
                    yarn_weaving_dispatch_detail_aux_result
                )

            upsert_result = await self._upsert_service_order_supply_stock(
                period=period,
                yarn_id=detail._yarn_purchase_entry_heavy.yarn_id,
                fabric_id=detail.fabric_id,
                supplier_yarn_id=detail._yarn_purchase_entry_heavy.supplier_yarn_id,
                service_order_number=yarn_weaving_dispatch.reference_number2,
                storage_code=supplier.storage_code,
                quantity=detail.net_weight,
                supplier_id=supplier.code,
                issue_date=yarn_weaving_dispatch.creation_date,
            )

            if upsert_result.is_failure:
                return upsert_result

            service_order_supply_detail: ServiceOrderSupplyDetail = upsert_result.value

            yarn_weaving_dispatch_detail_result.item_number_supply = (
                service_order_supply_detail.item_number
            )

        yarn_weaving_dispatch.detail = yarn_weaving_dispatch_detail

        creation_result = await self.save_movement(
            movement=yarn_weaving_dispatch,
            movement_detail=yarn_weaving_dispatch_detail,
            movememt_detail_aux=yarn_weaving_dispatch_detail_aux,
        )

        if creation_result.is_failure:
            return creation_result

        return Success(YarnWeavingDispatchSchema.model_validate(yarn_weaving_dispatch))

    async def anulate_yarn_weaving_dispatch(
        self,
        yarn_weaving_dispatch_number: str,
        period: int,
    ) -> Result[None, CustomException]:
        yarn_weaving_dispatch_result = await self._read_yarn_weaving_dispatch(
            yarn_weaving_dispatch_number=yarn_weaving_dispatch_number,
            period=period,
            include_detail=True,
        )

        if yarn_weaving_dispatch_result.is_failure:
            return yarn_weaving_dispatch_result

        yarn_weaving_dispatch: Movement = yarn_weaving_dispatch_result.value

        validation_result = await self._validate_update_yarn_weaving_dispatch(
            yarn_weaving_dispatch=yarn_weaving_dispatch
        )

        if validation_result.is_failure:
            return validation_result

        rollback_result = await self.rollback_yarn_weaving_dispatch(
            yarn_weaving_dispatch=yarn_weaving_dispatch
        )
        if rollback_result.is_failure:
            return rollback_result

        supplier_result = await self.supplier_service.read_supplier(
            supplier_code=yarn_weaving_dispatch.auxiliary_code,
        )

        if supplier_result.is_failure:
            return supplier_result

        supplier = supplier_result.value

        anulate_result = await self._anulate_yarn_entry_with_dispatch(
            entry_number=yarn_weaving_dispatch.reference_number1,
            period=period,
            storage_code=supplier.storage_code,
        )
        if anulate_result.is_failure:
            return anulate_result

        for detail in yarn_weaving_dispatch.detail:
            detail.status_flag = "A"
            detail.detail_aux.status_flag = "A"

        yarn_weaving_dispatch.status_flag = "A"

        creation_result = await self.save_movement(
            movement=yarn_weaving_dispatch,
            movement_detail=yarn_weaving_dispatch.detail,
            movememt_detail_aux=[
                detail.detail_aux for detail in yarn_weaving_dispatch.detail
            ],
        )
        if creation_result.is_failure:
            return creation_result

        return Success(None)

    async def is_updated_permission(
        self,
        yarn_weaving_dispatch_number: str,
        period: int,
    ) -> Result[None, CustomException]:
        yarn_weaving_dispatch_result = await self._read_yarn_weaving_dispatch(
            yarn_weaving_dispatch_number=yarn_weaving_dispatch_number,
            period=period,
        )

        if yarn_weaving_dispatch_result.is_failure:
            return yarn_weaving_dispatch_result

        yarn_weaving_dispatch: Movement = yarn_weaving_dispatch_result.value

        validation_result = await self._validate_update_yarn_weaving_dispatch(
            yarn_weaving_dispatch=yarn_weaving_dispatch
        )

        if validation_result.is_failure:
            return validation_result

        return Success(None)

    async def print_yarn_weaving_dispatch(
        self,
    ) -> Result[None, CustomException]:
        pdf = generate_pdf()

        return Success(pdf)
