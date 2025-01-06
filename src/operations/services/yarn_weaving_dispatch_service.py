from datetime import date, datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.constants import MECSA_COMPANY_CODE
from src.core.exceptions import CustomException
from src.core.repository import BaseRepository
from src.core.result import Result, Success
from src.core.utils import PERU_TIMEZONE, calculate_time
from src.operations.constants import (
    ENTRY_DOCUMENT_CODE,
    ENTRY_MOVEMENT_TYPE,
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
    YARN_WEAVING_DISPATCH_GROUP_ALREADY_DISPATCHED_FAILURE,
    YARN_WEAVING_DISPATCH_GROUP_ANULLED_FAILURE,
    YARN_WEAVING_DISPATCH_NOT_ADDRESS_ASSOCIATED_FAILURE,
    YARN_WEAVING_DISPATCH_NOT_FOUND_FAILURE,
    YARN_WEAVING_DISPATCH_PACKAGE_COUNT_MISMATCH_FAILURE,
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
    ServiceOrderStock,
)
from src.operations.repositories import (
    YarnWeavingDispatchRepository,
)
from src.operations.schemas import (
    ServiceOrderSchema,
    SupplierSchema,
    YarnWeavingDispatchCreateSchema,
    YarnWeavingDispatchDetailCreateSchema,
    YarnWeavingDispatchSchema,
    YarnWeavingDispatchSimpleListSchema,
    YarnWeavingDispatchUpdateSchema,
)

from .fabric_service import FabricService
from .movement_service import MovementService
from .series_service import (
    EntrySeries,
    YarnWeavingDispatchSeries,
)
from .service_order_service import ServiceOrderService
from .service_order_stock_service import ServiceOrderStockService
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
        self.yarn_entry_repository = BaseRepository(model=Movement, db=promec_db)
        self.yarn_entry_detail_repository = BaseRepository(
            model=MovementDetail, db=promec_db
        )
        self.service_order_repository = BaseRepository(model=ServiceOrder, db=promec_db)
        self.service_order_stock_repository = BaseRepository(
            model=ServiceOrderStock, db=promec_db
        )
        self.service_order_stock_service = ServiceOrderStockService(promec_db=promec_db)
        self.movement_detail_repository = BaseRepository(
            model=MovementDetail, db=promec_db
        )
        self.movement_detail_aux_repository = BaseRepository(
            model=MovementDetailAux, db=promec_db
        )
        self.service_order_service = ServiceOrderService(promec_db=promec_db, db=db)
        self.fabric_service = FabricService(promec_db=promec_db, db=db)

    async def read_yarn_weaving_dispatches(
        self,
        limit: int = None,
        offset: int = None,
        period: int = None,
        include_inactive: bool = False,
    ) -> Result[YarnWeavingDispatchSimpleListSchema, CustomException]:
        yarn_weaving_dispatches = await self.repository.find_yarn_weaving_dispatches(
            limit=limit,
            offset=offset,
            period=period,
            include_inactive=include_inactive,
        )

        return Success(
            YarnWeavingDispatchSimpleListSchema(
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
        service_order = await self.service_order_service.read_service_order(
            order_id=data.service_order_id,
            order_type="TJ",
            include_detail=True,
        )

        if service_order.is_failure:
            return service_order

        supplier = await self.supplier_service.read_supplier(
            supplier_code=data.supplier_code,
            include_service=True,
            include_other_addresses=True,
        )

        if supplier.is_failure:
            return supplier

        if supplier.value.storage_code == "":
            return YARN_WEAVING_DISPATCH_SUPPLIER_WITHOUT_STORAGE_FAILURE

        services = [service.service_code for service in supplier.value.services]
        if SERVICE_CODE_SUPPLIER_WEAVING not in services:
            return YARN_WEAVING_DISPATCH_SUPPLIER_NOT_ASSOCIATED_FAILURE

        if data.nrodir not in supplier.value.addresses.keys():
            return YARN_WEAVING_DISPATCH_NOT_ADDRESS_ASSOCIATED_FAILURE

        return Success((supplier.value, service_order.value))

    async def _validate_yarn_weaving_dispatch_detail_data(
        self,
        data: list[YarnWeavingDispatchDetailCreateSchema],
        service_order: ServiceOrderSchema,
        update=False,
        dispatch_number: str = None,
        yarn_weaving_dispatch_detail: list[MovementDetail] = None,
    ) -> Result[None, CustomException]:
        for detail in data:
            yarn_purchase_entry_detail_heavy_result = await self.yarn_purchase_entry_detail_heavy_service.read_yarn_purchase_entry_detail_heavy(
                ingress_number=detail.entry_number,
                item_number=detail.entry_item_number,
                group_number=detail.entry_group_number,
                period=detail.entry_period,
                include_detail_entry=True,
            )

            if yarn_purchase_entry_detail_heavy_result.is_failure:
                return yarn_purchase_entry_detail_heavy_result

            yarn_purchase_entry_detail_heavy = (
                yarn_purchase_entry_detail_heavy_result.value
            )

            detail._yarn_purchase_entry_heavy = yarn_purchase_entry_detail_heavy

            if yarn_purchase_entry_detail_heavy.status_flag == "A":
                return YARN_WEAVING_DISPATCH_GROUP_ANULLED_FAILURE

            if yarn_purchase_entry_detail_heavy.dispatch_status and not update:
                return YARN_WEAVING_DISPATCH_GROUP_ALREADY_DISPATCHED_FAILURE
            else:
                if update:
                    if (yarn_purchase_entry_detail_heavy.exit_number is not None) and (
                        yarn_purchase_entry_detail_heavy.exit_number != dispatch_number
                    ):
                        return YARN_WEAVING_DISPATCH_GROUP_ALREADY_DISPATCHED_FAILURE

            # //! VALIDAR QUE EL HILADO INGRESADO PERTENEZCA A LA RECETA DEL TEJIDO DE LA ORDEN DE SERVICIO

            entry_count = 0
            for detail_service in service_order.detail:
                fabric_result = await self.fabric_service.read_fabric(
                    fabric_id=detail_service.fabric_id,
                    include_recipe=True,
                )

                if fabric_result.is_failure:
                    print("FABRIC NOT FOUND")

                fabric = fabric_result.value

                yarn_ids = [yarn.yarn_id for yarn in fabric.recipe]

                if yarn_purchase_entry_detail_heavy.yarn_id in yarn_ids:
                    entry_count += 1

            if entry_count == 0:
                return YARN_WEAVING_DISPATCH_YARN_NOT_ASSOCIATED_FABRIC_FAILURE

            if update:
                for yarn_weaving_dispatch_detail_value in yarn_weaving_dispatch_detail:
                    if (
                        (
                            yarn_weaving_dispatch_detail_value.reference_number
                            == detail.entry_number
                        )
                        and (
                            yarn_weaving_dispatch_detail_value.entry_item_number
                            == detail.entry_item_number
                        )
                        and (
                            yarn_weaving_dispatch_detail_value.entry_group_number
                            == detail.entry_group_number
                        )
                    ):
                        print(yarn_weaving_dispatch_detail_value.detail_aux)
                        validate_package = (
                            yarn_purchase_entry_detail_heavy.packages_left
                            + yarn_weaving_dispatch_detail_value.detail_aux.guide_package_count
                            - detail.package_count
                        )
                        validate_cones = (
                            yarn_purchase_entry_detail_heavy.cones_left
                            + yarn_weaving_dispatch_detail_value.detail_aux.guide_cone_count
                            - detail.cone_count
                        )

                        break

            else:
                validate_package = (
                    yarn_purchase_entry_detail_heavy.packages_left
                    - detail.package_count
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
        dispatch_number: str,
        current_time: datetime,
        supplier: SupplierSchema,
        purchase_service_number: str,
        detail: list[YarnWeavingDispatchDetailCreateSchema],
    ) -> Result[None, CustomException]:
        entry_number = await self.entry_series.next_number()

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
                    product_code=detail[i]._yarn_purchase_entry_heavy.yarn_id,
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

            await self.product_inventory_service.update_current_stock(
                product_code=detail[i]._yarn_purchase_entry_heavy.yarn_id,
                period=period,
                storage_code=storage_code,
                new_stock=detail[i].net_weight,
            )

        await self.yarn_entry_repository.save(entry_movement)
        await self.yarn_entry_detail_repository.save_all(entry_detail)

        return Success(entry_number)

    async def _anulate_yarn_entry_with_dispatch(
        self,
        entry_number: str,
        period: int,
        storage_code: str,
    ) -> Result[None, CustomException]:
        filter = (
            (Movement.document_number == entry_number)
            & (Movement.company_code == MECSA_COMPANY_CODE)
            & (Movement.storage_code == storage_code)
            & (Movement.movement_type == ENTRY_MOVEMENT_TYPE)
            & (Movement.movement_code == WEAVING_MOVEMENT_CODE)
            & (Movement.document_code == ENTRY_DOCUMENT_CODE)
        )

        options = []

        options.append(joinedload(Movement.detail))
        entry_movement = await self.yarn_entry_repository.find(
            filter=filter, options=options
        )

        if entry_movement is not None:
            entry_movement.status_flag = "A"

            await self.yarn_entry_repository.save(entry_movement)

            for detail in entry_movement.detail:
                detail.status_flag = "A"

            await self.yarn_entry_detail_repository.save_all(entry_movement.detail)

        return Success(None)

    async def _create_yarn_entry_detail_with_dispatch(
        self,
        storage_code: str,
        period: int,
        dispatch_number: str,
        current_time: datetime,
        supplier: SupplierSchema,
        purchase_service_number: str,
        entry_number: str,
        detail: YarnWeavingDispatchUpdateSchema,
    ) -> Result[None, CustomException]:
        creation_date = current_time.date()
        creation_time = current_time.strftime("%H:%M:%S")

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
                    product_code=detail[i]._yarn_purchase_entry_heavy.yarn_id,
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

            await self.product_inventory_service.update_current_stock(
                product_code=detail[i]._yarn_purchase_entry_heavy.yarn_id,
                period=period,
                storage_code=storage_code,
                new_stock=detail[i].net_weight,
            )

        await self.yarn_entry_detail_repository.save_all(entry_detail)

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

    async def create_stock_service_order(
        self,
        period: int,
        yarn_id: str,
        supplier_yarn_id: str,
        service_order_number: str,
        storage_code: str,
        quantity: float,
        supplier_code: str,
        issue_date: date,
        dispatch_number: str,
    ) -> Result[None, CustomException]:
        stock_service_orders = await self.service_order_stock_service._read_max_item_number_by_product_id_and_service_order_id(
            product_id=yarn_id,
            period=period,
            storage_code=storage_code,
            service_order_id=service_order_number,
        )

        if stock_service_orders.is_failure:
            return stock_service_orders

        stock_service_order = ServiceOrderStock(
            company_code=MECSA_COMPANY_CODE,
            period=period,
            product_code=yarn_id,
            item_number=stock_service_orders.value + 1,
            reference_number=service_order_number,
            storage_code=storage_code,
            stkact=quantity,
            status_flag="P",
            supplier_code=supplier_code,
            creation_date=issue_date,
            pormer=0,
            quantity_received=0,
            quantity_dispatched=0,
            provided_quantity=quantity,
            dispatch_id=dispatch_number,
            supplier_yarn_id=supplier_yarn_id,
        )

        await self.service_order_stock_repository.save(stock_service_order)

        return Success(None)

    async def create_yarn_weaving_dispatch(
        self,
        form: YarnWeavingDispatchCreateSchema,
    ) -> Result[None, CustomException]:
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

        current_time = calculate_time(tz=PERU_TIMEZONE)

        creation_date = current_time.date()
        creation_time = current_time.strftime("%H:%M:%S")

        service_order_id = service_order.id

        creation_result = await self._create_yarn_entry_with_dispatch(
            storage_code=supplier.storage_code,
            period=form.period,
            dispatch_number=dispatch_number,
            current_time=current_time,
            supplier=supplier,
            purchase_service_number=service_order_id,
            detail=form.detail,
        )

        if creation_result.is_failure:
            return creation_result

        entry_number = creation_result.value

        yarn_weaving_dispatch = Movement(
            company_code=MECSA_COMPANY_CODE,
            storage_code=YARN_WEAVING_DISPATCH_STORAGE_CODE,
            movement_type=YARN_WEAVING_DISPATCH_MOVEMENT_TYPE,
            movement_code=YARN_WEAVING_DISPATCH_MOVEMENT_CODE,
            document_code=YARN_WEAVING_DISPATCH_DOCUMENT_CODE,
            document_number=dispatch_number,
            period=form.period,
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

        print("------------------------")
        for detail in form.detail:
            yarn_weaving_dispatch_detail_value = MovementDetail(
                company_code=MECSA_COMPANY_CODE,
                storage_code=YARN_WEAVING_DISPATCH_STORAGE_CODE,
                movement_type=YARN_WEAVING_DISPATCH_MOVEMENT_TYPE,
                movement_code=YARN_WEAVING_DISPATCH_MOVEMENT_CODE,
                document_code=YARN_WEAVING_DISPATCH_DOCUMENT_CODE,
                document_number=dispatch_number,
                item_number=detail.item_number,
                period=form.period,
                creation_date=creation_date,
                creation_time=creation_time,
                product_code=detail._yarn_purchase_entry_heavy.yarn_id,
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
            )

            yarn_weaving_dispatch_detail_aux_value = MovementDetailAux(
                company_code=MECSA_COMPANY_CODE,
                document_code=YARN_WEAVING_DISPATCH_DOCUMENT_CODE,
                document_number=dispatch_number,
                item_number=detail.item_number,
                period=form.period,
                product_code=detail._yarn_purchase_entry_heavy.yarn_id,
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
            yarn_purchase_entry = MovementYarnOCHeavy(
                **detail._yarn_purchase_entry_heavy.dict(exclude={"period"})
            )
            yarn_entry_detail = detail._yarn_purchase_entry_heavy.movement_detail
            yarn_purchase_entry.movement_detail = yarn_entry_detail
            yarn_weaving_dispatch_detail_value.movement_ingress = yarn_purchase_entry
            yarn_weaving_dispatch_detail.append(yarn_weaving_dispatch_detail_value)
            yarn_weaving_dispatch_detail_aux.append(
                yarn_weaving_dispatch_detail_aux_value
            )

            await self.create_stock_service_order(
                period=form.period,
                yarn_id=detail._yarn_purchase_entry_heavy.yarn_id,
                supplier_yarn_id=detail._yarn_purchase_entry_heavy.supplier_yarn_id,
                service_order_number=service_order_id,
                storage_code=supplier.storage_code,
                quantity=detail.net_weight,
                supplier_code=supplier.code,
                issue_date=creation_date,
                dispatch_number=dispatch_number,
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

            await self.product_inventory_service.update_current_stock(
                product_code=detail._yarn_purchase_entry_heavy.yarn_id,
                period=form.period,
                storage_code=YARN_WEAVING_DISPATCH_STORAGE_CODE,
                new_stock=detail.net_weight,
            )

        await self.repository.save(yarn_weaving_dispatch)
        await self.yarn_entry_detail_repository.save_all(yarn_weaving_dispatch_detail)
        await self.yarn_entry_detail_repository.save_all(
            yarn_weaving_dispatch_detail_aux
        )

        yarn_weaving_dispatch.detail = yarn_weaving_dispatch_detail

        return Success(YarnWeavingDispatchSchema.model_validate(yarn_weaving_dispatch))

    async def _validate_update_yarn_weaving_dispatch(
        self,
        yarn_weaving_dispatch: Movement,
    ) -> Result[None, CustomException]:
        if yarn_weaving_dispatch.status_flag == "A":
            return YARN_WEAVING_DISPATCH_ALREADY_ANULLED_FAILURE

        if yarn_weaving_dispatch.flgcbd == "S":
            return YARN_WEAVING_DISPATCH_ALREADY_ACCOUNTED_FAILURE

        return Success(None)

    async def _delete_detail(
        self,
        yarn_weaving_dispatch_detail: MovementDetail,
        entry_number: str,
        supplier: SupplierSchema,
    ) -> None:
        await self.product_inventory_service.rollback_currents_stock(
            product_code=yarn_weaving_dispatch_detail.product_code,
            period=yarn_weaving_dispatch_detail.period,
            storage_code=YARN_WEAVING_DISPATCH_STORAGE_CODE,
            quantity=yarn_weaving_dispatch_detail.mecsa_weight,
        )

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

        await self.service_order_stock_service.delete_service_order_stock(
            product_code=yarn_weaving_dispatch_detail.product_code,
            period=yarn_weaving_dispatch_detail.period,
            storage_code=supplier.storage_code,
            reference_number=yarn_weaving_dispatch_detail.nroreq,
            item_number=yarn_weaving_dispatch_detail.entry_item_number,
        )

        if yarn_entry_detail is not None:
            await self.yarn_entry_detail_repository.delete(yarn_entry_detail)

        await self.product_inventory_service.rollback_currents_stock(
            product_code=yarn_weaving_dispatch_detail.product_code,
            period=yarn_weaving_dispatch_detail.period,
            storage_code=supplier.storage_code,
            quantity=yarn_weaving_dispatch_detail.mecsa_weight,
        )

        await self.yarn_purchase_entry_detail_heavy_service.rollback_yarn_purchase_entry_detail_heavy_by_yarn_dispatch(
            package_count=yarn_weaving_dispatch_detail.detail_aux.guide_package_count,
            cone_count=yarn_weaving_dispatch_detail.detail_aux.guide_cone_count,
            item_number=yarn_weaving_dispatch_detail.entry_item_number,
            group_number=yarn_weaving_dispatch_detail.entry_group_number,
            entry_number=yarn_weaving_dispatch_detail.reference_number,
            period=yarn_weaving_dispatch_detail.period,
        )

        await self.movement_detail_aux_repository.delete(
            yarn_weaving_dispatch_detail.detail_aux
        )
        await self.movement_detail_repository.delete(yarn_weaving_dispatch_detail)

    async def _delete_yarn_weaving_dispatch_detail(
        self,
        yarn_weaving_dispatch_detail: list[MovementDetail],
        supplier: SupplierSchema,
        entry_number: str,
        form: YarnWeavingDispatchUpdateSchema,
    ) -> list[MovementDetail]:
        item_numbers = [detail.item_number for detail in form.detail]

        for detail in yarn_weaving_dispatch_detail:
            if detail.item_number not in item_numbers:
                await self._delete_detail(
                    yarn_weaving_dispatch_detail=detail,
                    entry_number=entry_number,
                    supplier=supplier,
                )
                yarn_weaving_dispatch_detail.remove(detail)

        return yarn_weaving_dispatch_detail

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

        current_time = calculate_time(tz=PERU_TIMEZONE)

        creation_date = current_time.date()
        if yarn_weaving_dispatch_result.is_failure:
            return yarn_weaving_dispatch_result

        yarn_weaving_dispatch: Movement = yarn_weaving_dispatch_result.value

        validation_result = await self._validate_update_yarn_weaving_dispatch(
            yarn_weaving_dispatch=yarn_weaving_dispatch
        )

        if validation_result.is_failure:
            return validation_result

        validation_result = await self._validate_yarn_weaving_dispatch_data(data=form)

        if validation_result.is_failure:
            return validation_result

        supplier = validation_result.value[0]
        service_order = validation_result.value[1]

        validation_result = await self._validate_yarn_weaving_dispatch_detail_data(
            data=form.detail,
            update=True,
            dispatch_number=yarn_weaving_dispatch_number,
            service_order=service_order,
            yarn_weaving_dispatch_detail=yarn_weaving_dispatch.detail,
        )

        if validation_result.is_failure:
            return validation_result

        form.detail = validation_result.value

        yarn_weaving_dispatch.supplier_code = form.supplier_code

        yarn_weaving_dispatch.detail = await self._delete_yarn_weaving_dispatch_detail(
            yarn_weaving_dispatch_detail=yarn_weaving_dispatch.detail,
            supplier=supplier,
            entry_number=yarn_weaving_dispatch.reference_number1,
            form=form,
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
                await self.product_inventory_service.rollback_currents_stock(
                    product_code=yarn_weaving_dispatch_detail_result.product_code,
                    period=yarn_weaving_dispatch_detail_result.period,
                    storage_code=YARN_WEAVING_DISPATCH_STORAGE_CODE,
                    quantity=yarn_weaving_dispatch_detail_result.mecsa_weight,
                )

                await self.product_inventory_service.update_current_stock(
                    product_code=yarn_weaving_dispatch_detail_result.product_code,
                    period=yarn_weaving_dispatch_detail_result.period,
                    storage_code=YARN_WEAVING_DISPATCH_STORAGE_CODE,
                    new_stock=detail.net_weight,
                )

                await self.product_inventory_service.rollback_currents_stock(
                    product_code=yarn_weaving_dispatch_detail_result.product_code,
                    period=yarn_weaving_dispatch_detail_result.period,
                    storage_code=supplier.storage_code,
                    quantity=yarn_weaving_dispatch_detail_result.mecsa_weight,
                )

                await self.product_inventory_service.update_current_stock(
                    product_code=yarn_weaving_dispatch_detail_result.product_code,
                    period=yarn_weaving_dispatch_detail_result.period,
                    storage_code=supplier.storage_code,
                    new_stock=detail.net_weight,
                )

                yarn_weaving_dispatch_detail_result.mecsa_weight = detail.net_weight

                await self.service_order_stock_service.rollback_current_stock(
                    product_code=yarn_weaving_dispatch_detail_result.product_code,
                    period=yarn_weaving_dispatch_detail_result.period,
                    storage_code=supplier.storage_code,
                    reference_number=yarn_weaving_dispatch_detail_result.nroreq,
                    item_number=yarn_weaving_dispatch_detail_result.entry_item_number,
                    quantity=yarn_weaving_dispatch_detail_result.mecsa_weight,
                )

                await self.service_order_stock_service.update_current_stock(
                    product_code=yarn_weaving_dispatch_detail_result.product_code,
                    period=yarn_weaving_dispatch_detail_result.period,
                    storage_code=supplier.storage_code,
                    reference_number=yarn_weaving_dispatch_detail_result.nroreq,
                    item_number=yarn_weaving_dispatch_detail_result.entry_item_number,
                    new_stock=detail.net_weight,
                )

                await self.yarn_purchase_entry_detail_heavy_service.rollback_yarn_purchase_entry_detail_heavy_by_yarn_dispatch(
                    package_count=yarn_weaving_dispatch_detail_aux_result.guide_package_count,
                    cone_count=yarn_weaving_dispatch_detail_aux_result.guide_cone_count,
                    item_number=yarn_weaving_dispatch_detail_result.entry_item_number,
                    group_number=yarn_weaving_dispatch_detail_result.entry_group_number,
                    entry_number=yarn_weaving_dispatch_detail_result.reference_number,
                    period=yarn_weaving_dispatch_detail_result.period,
                )

                await self.yarn_purchase_entry_detail_heavy_service.update_yarn_purchase_entry_detail_heavy_by_yarn_dispatch(
                    entry_number=yarn_weaving_dispatch_detail_result.reference_number,
                    item_number=yarn_weaving_dispatch_detail_result.entry_item_number,
                    group_number=yarn_weaving_dispatch_detail_result.entry_group_number,
                    period=yarn_weaving_dispatch_detail_result.period,
                    cone_count=detail.cone_count,
                    package_count=detail.package_count,
                    dispatch_number=yarn_weaving_dispatch_number,
                )

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

                await self.repository.save(yarn_weaving_dispatch)
                await self.yarn_entry_detail_repository.save(
                    yarn_weaving_dispatch_detail_result
                )
                await self.movement_detail_aux_repository.save(
                    yarn_weaving_dispatch_detail_aux_result
                )

            else:
                yarn_weaving_dispatch_detail = MovementDetail(
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
                    product_code=detail._yarn_purchase_entry_heavy.yarn_id,
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
                )

                yarn_weaving_dispatch_detail_aux = MovementDetailAux(
                    company_code=MECSA_COMPANY_CODE,
                    document_code=YARN_WEAVING_DISPATCH_DOCUMENT_CODE,
                    document_number=yarn_weaving_dispatch_number,
                    item_number=detail.item_number,
                    period=period,
                    product_code=detail._yarn_purchase_entry_heavy.yarn_id,
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

                await self.create_stock_service_order(
                    period=period,
                    yarn_id=detail._yarn_purchase_entry_heavy.yarn_id,
                    supplier_yarn_id=detail._yarn_purchase_entry_heavy.supplier_yarn_id,
                    service_order_number=yarn_weaving_dispatch.reference_number2,
                    storage_code=supplier.storage_code,
                    quantity=detail.net_weight,
                    supplier_code=supplier.code,
                    issue_date=creation_date,
                    dispatch_number=yarn_weaving_dispatch_number,
                )

                await self.product_inventory_service.update_current_stock(
                    product_code=detail._yarn_purchase_entry_heavy.yarn_id,
                    period=period,
                    storage_code=YARN_WEAVING_DISPATCH_STORAGE_CODE,
                    new_stock=detail.net_weight,
                )

                await self.yarn_purchase_entry_detail_heavy_service.update_yarn_purchase_entry_detail_heavy_by_yarn_dispatch(
                    entry_number=detail.entry_number,
                    item_number=detail.entry_item_number,
                    group_number=detail.entry_group_number,
                    period=detail.entry_period,
                    cone_count=detail.cone_count,
                    package_count=detail.package_count,
                    dispatch_number=yarn_weaving_dispatch_number,
                )

                await self._create_yarn_entry_detail_with_dispatch(
                    storage_code=supplier.storage_code,
                    period=period,
                    dispatch_number=yarn_weaving_dispatch_number,
                    current_time=current_time,
                    supplier=supplier,
                    purchase_service_number=yarn_weaving_dispatch.reference_number2,
                    entry_number=yarn_weaving_dispatch.reference_number1,
                    detail=form.detail,
                )

                await self.repository.save(yarn_weaving_dispatch)
                await self.yarn_entry_detail_repository.save(
                    yarn_weaving_dispatch_detail
                )
                await self.movement_detail_aux_repository.save(
                    yarn_weaving_dispatch_detail_aux
                )

        return Success(None)

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

        supplier_result = await self.supplier_service.read_supplier(
            supplier_code=yarn_weaving_dispatch.auxiliary_code,
            include_service=True,
        )

        if supplier_result.is_failure:
            return supplier_result

        supplier = supplier_result.value

        # await self.anulate_service_order(
        #     service_order_number=yarn_weaving_dispatch.reference_number2,
        # )

        for detail in yarn_weaving_dispatch.detail:
            await self.product_inventory_service.rollback_currents_stock(
                product_code=detail.product_code,
                period=period,
                storage_code=YARN_WEAVING_DISPATCH_STORAGE_CODE,
                quantity=detail.mecsa_weight,
            )

            await self.product_inventory_service.rollback_currents_stock(
                product_code=detail.product_code,
                period=period,
                storage_code=supplier.storage_code,
                quantity=detail.mecsa_weight,
            )

            await self.service_order_stock_service.anulate_service_order_stock(
                product_code=detail.product_code,
                period=period,
                storage_code=YARN_WEAVING_DISPATCH_STORAGE_CODE,
                reference_number=yarn_weaving_dispatch.reference_number2,
                item_number=detail.item_number,
            )

            await self.yarn_purchase_entry_detail_heavy_service.rollback_yarn_purchase_entry_detail_heavy_by_yarn_dispatch(
                package_count=detail.detail_aux.guide_package_count,
                cone_count=detail.detail_aux.guide_cone_count,
                item_number=detail.entry_item_number,
                group_number=detail.entry_group_number,
                entry_number=detail.reference_number,
                period=detail.period,
            )

            detail.status_flag = "A"
            detail.detail_aux.status_flag = "A"

        yarn_weaving_dispatch.status_flag = "A"

        await self.repository.save(yarn_weaving_dispatch)
        await self.yarn_entry_detail_repository.save_all(yarn_weaving_dispatch.detail)
        await self.movement_detail_aux_repository.save_all(
            [detail.detail_aux for detail in yarn_weaving_dispatch.detail]
        )

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
