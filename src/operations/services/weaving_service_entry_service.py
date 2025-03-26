from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.constants import MECSA_COMPANY_CODE
from src.core.exceptions import CustomException
from src.core.repositories import SequenceRepository
from src.core.repository import (
    BaseRepository,
)
from src.core.result import Result, Success
from src.core.utils import PERU_TIMEZONE, calculate_time
from src.operations.constants import (
    ANNULLED_SERVICE_ORDER_ID,
    CANCELLED_SERVICE_ORDER_ID,
    CLOSED_SERVICE_ORDER_ID,
    DISPATCH_DOCUMENT_CODE,
    DISPATCH_MOVEMENT_TYPE,
    ENTRY_DOCUMENT_CODE,
    ENTRY_MOVEMENT_TYPE,
    IN_PROCESS_SERVICE_ORDER_ID,
    LIQUIDATED_SERVICE_ORDER_ID,
    PENDING_BALANCES_FOR_CANCELLED_SERVICE_ORDER_ID,
    PENDING_BALANCES_SERVICE_ORDER_ID,
    SCHEDULED_SERVICE_ORDER_ID,
    SERVICE_CODE_SUPPLIER_DYEING,
    SERVICE_CODE_SUPPLIER_WEAVING,
    STOPPED_SERVICE_ORDER_ID,
    WEAVING_SERVICE_ENTRY_MOVEMENT_CODE,
    WEAVING_STORAGE_CODE,
    YARN_WEAVING_DISPATCH_MOVEMENT_CODE,
)
from src.operations.failures import (
    WEAVING_SERVICE_ENTRY_ALREADY_ACCOUNTED_FAILURE,
    WEAVING_SERVICE_ENTRY_ALREADY_QUANTITY_RECEIVED_FAILURE,
    WEAVING_SERVICE_ENTRY_CARD_OPERATION_ALREADY_DISPATCHED_FAILURE,
    WEAVING_SERVICE_ENTRY_FABRIC_ALREADY_ANULLED_FAILURE,
    WEAVING_SERVICE_ENTRY_FABRIC_ALREADY_QUANTITY_RECEIVED_FAILURE,
    WEAVING_SERVICE_ENTRY_FABRIC_NOT_FOUND_FAILURE,
    WEAVING_SERVICE_ENTRY_NOT_FOUND_FAILURE,
    WEAVING_SERVICE_ENTRY_SERVICE_ORDER_ANULLED_FAILURE,
    WEAVING_SERVICE_ENTRY_SERVICE_ORDER_NOT_SUPPLIED_FABRIC_YARNS_FAILURE,
    WEAVING_SERVICE_ENTRY_SERVICE_ORDER_NOT_SUPPLIED_YARNS_FAILURE,
    WEAVING_SERVICE_ENTRY_SUPPLIER_COLOR_NOT_FOUND_FAILURE,
    WEAVING_SERVICE_ENTRY_SUPPLIER_NOT_ASSOCIATED_FAILURE,
    WEAVING_SERVICE_ENTRY_SUPPLIER_NOT_ASSOCIATED_TO_DYEING_FAILURE,
    WEAVING_SERVICE_ENTRY_SUPPLIER_WITHOUT_STORAGE_FAILURE,
    WeavingServiceEntryFailures,
)
from src.operations.models import (
    CardOperation,
    FabricWarehouse,
    Movement,
    MovementDetail,
    ServiceRate,
)
from src.operations.repositories import WeavingServiceEntryRepository
from src.operations.schemas import (
    FabricSchema,
    ServiceOrderSchema,
    SupplierSchema,
    WeavingServiceEntriesListSchema,
    WeavingServiceEntriesSimpleListSchema,
    WeavingServiceEntryCreateSchema,
    WeavingServiceEntryDetailCreateSchema,
    WeavingServiceEntryFilterParams,
    WeavingServiceEntryPrintListSchema,
    WeavingServiceEntrySchema,
    WeavingServiceEntryUpdateSchema,
)
from src.operations.sequences import card_id_seq
from src.operations.utils.card_operation.pdf import generate_pdf_cards

from ..suppliers.supplier_service import SupplierService
from .card_operation_service import CardOperationService
from .fabric_service import FabricService
from .mecsa_color_service import MecsaColorService
from .movement_service import MovementService
from .series_service import (
    DispatchSeries,
    WeavingServiceEntrySeries,
)
from .service_order_service import ServiceOrderService
from .service_order_supply_service import ServiceOrderSupplyDetailService


class WeavingServiceEntryService(MovementService):
    def __init__(self, promec_db: AsyncSession, db: AsyncSession = None) -> None:
        super().__init__(promec_db=promec_db)
        self.repository = WeavingServiceEntryRepository(promec_db=promec_db)
        self.weaving_service_entry_series = WeavingServiceEntrySeries(
            promec_db=promec_db
        )
        self.supplier_service = SupplierService(promec_db=promec_db)
        self.fabric_service = FabricService(db=db, promec_db=promec_db)
        self.service_order_service = ServiceOrderService(db=db, promec_db=promec_db)
        self.service_card_operation_service = BaseRepository(
            model=ServiceRate, db=promec_db
        )
        self.mecsa_color_service = MecsaColorService(promec_db=promec_db)
        self.card_operation_sequence = SequenceRepository(
            sequence=card_id_seq, db=promec_db
        )
        self.dispatch_series = DispatchSeries(promec_db=promec_db)
        self.service_order_supply_service = ServiceOrderSupplyDetailService(
            promec_db=promec_db
        )
        self.yarn_weaving_dispatch_repository = BaseRepository(
            model=MovementDetail, db=promec_db
        )
        self.movement_detail_repository = BaseRepository(
            model=MovementDetail, db=promec_db
        )
        self.fabric_warehouse_repository = BaseRepository(
            model=FabricWarehouse, db=promec_db
        )
        self.card_operation_repository = BaseRepository(
            model=CardOperation, db=promec_db
        )
        self.card_operation_service = CardOperationService(promec_db=promec_db)

    async def read_weaving_service_entries(
        self,
        filter_params: WeavingServiceEntryFilterParams,
    ) -> Result[WeavingServiceEntriesSimpleListSchema, CustomException]:
        weaving_service_entries = await self.repository.find_weaving_service_entries(
            **filter_params.model_dump(exclude={"page"})
        )

        return Success(
            WeavingServiceEntriesListSchema(
                weaving_service_entries=weaving_service_entries
            )
        )

    async def _read_weaving_service_entry(
        self,
        weaving_service_entry_number: str,
        period: int,
        include_detail: bool = False,
        include_detail_card: bool = False,
    ) -> Result[Movement, CustomException]:
        weaving_service_entry = (
            await self.repository.find_weaving_service_entry_by_entry_number(
                entry_number=weaving_service_entry_number,
                period=period,
                include_detail=include_detail,
                include_detail_card=include_detail_card,
            )
        )

        if weaving_service_entry is None:
            return WEAVING_SERVICE_ENTRY_NOT_FOUND_FAILURE

        return Success(weaving_service_entry)

    async def read_weaving_service_entry(
        self,
        weaving_service_entry_number: str,
        period: int,
        include_detail: bool = False,
        include_detail_card: bool = False,
    ) -> Result[WeavingServiceEntrySchema, CustomException]:
        weaving_service_entry_result = await self._read_weaving_service_entry(
            weaving_service_entry_number=weaving_service_entry_number,
            period=period,
            include_detail=include_detail,
            include_detail_card=include_detail_card,
        )

        if weaving_service_entry_result.is_failure:
            return weaving_service_entry_result

        return Success(
            WeavingServiceEntrySchema.model_validate(weaving_service_entry_result.value)
        )

    async def _validate_weaving_service_entry_data(
        self,
        data: WeavingServiceEntryCreateSchema,
    ) -> Result[None, CustomException]:
        supplier = await self.supplier_service.read_supplier(
            supplier_code=data.supplier_id,
            include_service=True,
        )

        if supplier.is_failure:
            return supplier

        if supplier.value.storage_code == "":
            return WEAVING_SERVICE_ENTRY_SUPPLIER_WITHOUT_STORAGE_FAILURE

        services = [service.service_code for service in supplier.value.services]
        if SERVICE_CODE_SUPPLIER_WEAVING not in services:
            return WEAVING_SERVICE_ENTRY_SUPPLIER_NOT_ASSOCIATED_FAILURE

        return Success(supplier.value)

    async def _validate_rate_fabric(
        self,
        current_date: datetime,
        supplier_id: str,
        fabric: FabricSchema,
    ) -> Result[None, CustomException]:
        codcol = "CRUD"
        fabric_id = fabric.id

        if fabric.color:
            codcol = fabric.color.id
            fabric_id = fabric_id[0:3] + str(round(fabric.density))

        filter = (
            (ServiceRate.company_code == MECSA_COMPANY_CODE)
            & (ServiceRate.period == current_date.date().year)
            & (ServiceRate.month_number == current_date.date().month)
            & (ServiceRate.serial_code == "003")
            & (ServiceRate.supplier_id == supplier_id)
            & (ServiceRate.fabric_id == fabric_id)
            & (ServiceRate.width == fabric.width)
            & (ServiceRate.codcol == codcol)
        )

        rate = await self.service_card_operation_service.find(
            filter=filter,
        )

        if rate is None:
            print("Fabric rate missing")
            # return WEAVING_SERVICE_ENTRY_FABRIC_RATE_MISSING_FAILURE

        return Success(None)

    async def _validate_weaving_service_entry_detail_data(
        self,
        supplier: SupplierSchema,
        period: int,
        current_date: datetime,
        data: list[WeavingServiceEntryDetailCreateSchema],
    ) -> Result[None, CustomException]:
        for detail in data:
            # Validación de existencia de la orden de servicio
            service_orders = []
            service_order_result = await self.service_order_service.read_service_order(
                order_id=detail.service_order_id,
                order_type="TJ",
                include_detail=True,
            )

            if service_order_result.is_failure:
                return service_order_result

            service_orders.append(service_order_result.value)
            # En caso sean multiples ordenes de servicio

            fabric_ids = {
                fabric.fabric_id
                for service_order in service_orders
                for fabric in service_order.detail
            }
            # Codes antiguos no esta el detalle de la O/S
            if detail.fabric_id not in fabric_ids:
                return WEAVING_SERVICE_ENTRY_FABRIC_NOT_FOUND_FAILURE

            fabric_result = await self.fabric_service.read_fabric(
                fabric_id=detail.fabric_id,
                include_recipe=True,
                include_color=True,
                # include_yarn_instance_to_recipe=True,
            )
            if fabric_result.is_failure:
                return fabric_result
            fabric: FabricSchema = fabric_result.value

            for service_order in service_orders:
                service_orders_supply_stock_result = await self.service_order_supply_service._read_service_orders_supply_stock(
                    storage_code=supplier.storage_code,
                    period=period,
                    service_order_id=service_order.id,
                )

                if service_orders_supply_stock_result.is_failure:
                    return service_orders_supply_stock_result

                service_orders_supply_stock: list[ServiceOrderSupplyDetailService] = (
                    service_orders_supply_stock_result.value
                )

                if not service_orders_supply_stock:
                    return (
                        WEAVING_SERVICE_ENTRY_SERVICE_ORDER_NOT_SUPPLIED_YARNS_FAILURE
                    )

                yarns_ids = {
                    supply_stock.product_code1
                    for supply_stock in service_orders_supply_stock
                }

                if (service_order.status_param_id == CANCELLED_SERVICE_ORDER_ID) or (
                    service_order.status_param_id
                    == PENDING_BALANCES_FOR_CANCELLED_SERVICE_ORDER_ID
                ):
                    return WeavingServiceEntryFailures.WEAVING_SERVICE_ENTRY_SERVICE_ORDER_CANCELLED_FAILURE

                if (service_order.status_param_id == LIQUIDATED_SERVICE_ORDER_ID) or (
                    service_order.status_param_id == PENDING_BALANCES_SERVICE_ORDER_ID
                ):
                    return WEAVING_SERVICE_ENTRY_ALREADY_QUANTITY_RECEIVED_FAILURE

                if service_order.status_param_id == ANNULLED_SERVICE_ORDER_ID:
                    return WEAVING_SERVICE_ENTRY_SERVICE_ORDER_ANULLED_FAILURE

                # Se recolecta los proveedores que componen el hilado del stock del insumo de O/S
                # //!Consultar para facilicitar
                fabric_recipe_yarns_ids = {}
                for service_order_supply_stock in service_orders_supply_stock:
                    fabric_recipe_yarns_ids.setdefault(
                        service_order_supply_stock.product_code1, set()
                    ).add(service_order_supply_stock.supplier_yarn_id)

                # print(fabric_recipe_yarns_ids)

                # Se recolecta el estado del tejido en la orden de servicio
                fabric_ids = {
                    fabric.fabric_id: fabric.status_param_id
                    for fabric in service_order.detail
                }

                # Se recolecta los proveedores que componen el hilado del stock del insumo de O/S del tejido
                yarn_supplier_ids: list[str] = list(
                    set.union(
                        *[
                            fabric_recipe_yarns_ids[yarn.yarn_id]
                            for yarn in fabric.recipe
                            if yarn.yarn_id in fabric_recipe_yarns_ids
                        ]
                    )
                )

                fabric.supplier_yarn_ids = yarn_supplier_ids
                detail._fabric = fabric
                detail._service_orders_supply_stock = service_orders_supply_stock

                count_recipe_supplied = 0

                for yarn in fabric.recipe:
                    if yarn.yarn_id in yarns_ids:
                        count_recipe_supplied += 1

                if count_recipe_supplied != len(fabric.recipe):
                    return WEAVING_SERVICE_ENTRY_SERVICE_ORDER_NOT_SUPPLIED_FABRIC_YARNS_FAILURE

                if fabric_ids[detail.fabric_id] == LIQUIDATED_SERVICE_ORDER_ID:
                    return (
                        WEAVING_SERVICE_ENTRY_FABRIC_ALREADY_QUANTITY_RECEIVED_FAILURE
                    )

                if fabric_ids[detail.fabric_id] == CANCELLED_SERVICE_ORDER_ID:
                    return WeavingServiceEntryFailures.WEAVING_SERVICE_ENTRY_SERVICE_ORDER_CANCELLED_FAILURE

                validation_result = await self._validate_rate_fabric(
                    current_date=current_date,
                    supplier_id=service_order.supplier_id,
                    fabric=fabric,
                )

                if validation_result.is_failure:
                    return validation_result

        return Success((data, service_order))

    # async def _validate_weaving_service_entry_detail_card(
    #     self,
    #     data: list[WeavingServiceEntryDetailCreateSchema],
    # ) -> Result[None, CustomException]:
    #
    #     return Success(None)

    async def _generate_cards_operations(
        self,
        supplier_weaving_tej: str,
        service_order: ServiceOrderSchema,
        detail: WeavingServiceEntryDetailCreateSchema,
        entry_number: str,
        current_time: datetime,
        period: int,
    ) -> Result[None, CustomException]:
        cards_operations = []
        creation_date = current_time.date()

        net_weight = round(detail.guide_net_weight / detail.roll_count, 2)
        gross_weight = net_weight
        sdoneto = net_weight
        for i in range(detail.roll_count):
            card_id = "C" + str(await self.card_operation_sequence.next_value())
            color = "CRUD"
            if detail._fabric.color:
                color = detail._fabric.color.id

            yarn_supplier_ids = ""

            for supplier_id in detail._fabric.supplier_yarn_ids:
                yarn_supplier_ids += supplier_id + ","

            yarn_supplier_ids = yarn_supplier_ids[:-1]

            card_operation = CardOperation(
                id=card_id,
                fabric_id=detail.fabric_id,
                width=detail._fabric.width,
                codcol=color,
                net_weight=net_weight,
                gross_weight=gross_weight,
                document_number="P/I" + entry_number,
                creation_date=creation_date,
                supplier_weaving_tej=supplier_weaving_tej,
                status_flag="P",
                storage_code=WEAVING_STORAGE_CODE,
                entry_user_id="DESA01",
                product_id=detail.fabric_id,
                tint_supplier_id="",
                fabric_type="C",
                tint_color_id="",
                desttej="T",
                flgsit="P",
                sdoneto=sdoneto,
                yarn_supplier_id=yarn_supplier_ids,
                service_order_id=service_order.id,
                card_type="C",
                company_code=MECSA_COMPANY_CODE,
                period=period,
            )

            cards_operations.append(card_operation)

        return Success(cards_operations)

    async def _create_yarn_weaving_dispatch(
        self,
        dispatch_number: str,
        supplier: SupplierSchema,
        period: int,
        current_time: datetime,
        weaving_service_entry_number: str,
        weaving_service_entry_detail: list[WeavingServiceEntryDetailCreateSchema],
    ) -> Result[None, CustomException]:
        creation_date = current_time.date()
        creation_time = current_time.strftime("%H:%M:%S")

        yarn_weaving_dispatch = Movement(
            company_code=MECSA_COMPANY_CODE,
            storage_code=supplier.storage_code,
            movement_type=DISPATCH_MOVEMENT_TYPE,
            movement_code=YARN_WEAVING_DISPATCH_MOVEMENT_CODE,
            document_code=DISPATCH_DOCUMENT_CODE,
            document_number=dispatch_number,
            period=period,
            creation_date=creation_date,
            creation_time=creation_time,
            clfaux="_PRO",
            auxiliary_code=supplier.code,
            reference_code="P/I",
            reference_number1=weaving_service_entry_number,
            status_flag="P",
            user_id="DESA01",
            auxiliary_name=supplier.name,
            origmov="A",
            serial_number="001",
            printed_flag="N",
            flgact="N",
            nrodir1="000",
            flgtras=False,
            flgreclamo="N",
            flgsit="A",
            servadi="N",
            tarfservadi=0,
            flgcbd="N",
            nrodir2="000",
            origin_station="SERVIDORDESA",
            flgele="P",
            undpesobrutototal="KGM",
            transaction_mode="02",
            intentosenvele=0,
        )

        yarn_weaving_dispatch_detail = []

        for detail in weaving_service_entry_detail:
            guide_net_weight = detail.guide_net_weight
            for i in range(len(detail._fabric.recipe)):
                yarn = detail._fabric.recipe[i]
                quantity = round(guide_net_weight * (yarn.proportion / 100.0), 2)
                yarn_weaving_dispatch_detail_value = MovementDetail(
                    company_code=MECSA_COMPANY_CODE,
                    storage_code=supplier.storage_code,
                    movement_type=DISPATCH_MOVEMENT_TYPE,
                    movement_code=YARN_WEAVING_DISPATCH_MOVEMENT_CODE,
                    document_code=DISPATCH_DOCUMENT_CODE,
                    document_number=dispatch_number,
                    period=period,
                    creation_date=creation_date,
                    creation_time=creation_time,
                    item_number=i + 1,
                    product_code1=yarn.yarn_id,
                    unit_code="KG",
                    factor=1,
                    mecsa_weight=quantity,
                    reference_code="O/S",
                    reference_number=detail.service_order_id,
                    # stkgen=,
                    # stkalm=,
                    nroreq=detail.service_order_id,
                    status_flag="P",
                    entry_item_number=detail.item_number,
                )

                await self.product_inventory_service.update_current_stock(
                    product_code1=yarn.yarn_id,
                    period=period,
                    storage_code=supplier.storage_code,
                    new_stock=-quantity,
                )

                yarn_weaving_dispatch_detail.append(yarn_weaving_dispatch_detail_value)

        await self.save_movement(
            movement=yarn_weaving_dispatch,
            movement_detail=yarn_weaving_dispatch_detail,
        )

        return Success(dispatch_number)

    # async def _find_supplier_yarn_id_

    async def create_weaving_service_entry(
        self,
        form: WeavingServiceEntryCreateSchema,
    ) -> Result[WeavingServiceEntrySchema, CustomException]:
        validation_result = await self._validate_weaving_service_entry_data(data=form)
        if validation_result.is_failure:
            return validation_result

        supplier: SupplierSchema = validation_result.value

        current_time = calculate_time(tz=PERU_TIMEZONE)

        validation_result = await self._validate_weaving_service_entry_detail_data(
            data=form.detail,
            supplier=supplier,
            period=form.period,
            current_date=current_time,
        )
        if validation_result.is_failure:
            return validation_result

        form.detail = validation_result.value[0]
        service_order = validation_result.value[1]

        # validation_result = await self._validate_weaving_service_entry_detail_card(
        #     data=form.detail
        # )
        # if validation_result.is_failure:
        #     return validation_result

        entry_number = await self.weaving_service_entry_series.next_number()

        # currency_code
        # currency_exchange

        creation_date = current_time.date()
        creation_time = current_time.strftime("%H:%M:%S")

        dispatch_number: str = await self.dispatch_series.next_number()

        weaving_service_entry = Movement(
            company_code=MECSA_COMPANY_CODE,
            storage_code=WEAVING_STORAGE_CODE,
            movement_type=ENTRY_MOVEMENT_TYPE,
            movement_code=WEAVING_SERVICE_ENTRY_MOVEMENT_CODE,
            document_code=ENTRY_DOCUMENT_CODE,
            document_number=entry_number,
            period=form.period,
            creation_date=creation_date,
            creation_time=creation_time,
            # currency_code=currency_code_value,
            # exchange_rate=exchange_rate_value,
            document_note=form.document_note,
            clfaux="_PRO",
            auxiliary_code=form.supplier_id,
            reference_code="P/S",
            reference_number1=dispatch_number,
            status_flag="P",
            user_id="DESA01",
            auxiliary_name=supplier.name,
            nrogf=form.supplier_po_correlative,
            sergf=form.supplier_po_series,
            fecgf=form.fecgf,
            origmov="A",
            serial_number="001",
            printed_flag="N",
            flgact="N",
            nrodir1="000",
            flgtras=True,
            flgreclamo="N",
            flgsit="A",
            servadi="N",
            tarfservadi=0,
            flgcbd="N",
            nrodir2="000",
            origin_station="SERVIDORDESA",
            flgele="P",
            undpesobrutototal="KGM",
            transaction_mode="02",
            intentosenvele=0,
        )

        weaving_service_entry_detail = []
        weaving_service_entry_detail_fabric = []
        weaving_service_entry_detail_card = []

        for detail in form.detail:
            card_operations_value = []
            if detail.generate_cards:
                card_operations_value = await self._generate_cards_operations(
                    supplier_weaving_tej=supplier.code,
                    service_order=service_order,
                    detail=detail,
                    entry_number=entry_number,
                    current_time=current_time,
                    period=form.period,
                )

                if card_operations_value.is_failure:
                    return card_operations_value

                card_operations_value = card_operations_value.value
                weaving_service_entry_detail_card.extend(card_operations_value)

            mecsa_weight = sum([card.net_weight for card in card_operations_value])

            product_inventory = await self._read_or_create_product_inventory(
                product_code1=detail.fabric_id,
                period=form.period,
                storage_code=WEAVING_STORAGE_CODE,
                enable_create=True,
            )

            if product_inventory.is_failure:
                return product_inventory

            weaving_service_entry_detail_value = MovementDetail(
                company_code=MECSA_COMPANY_CODE,
                storage_code=WEAVING_STORAGE_CODE,
                movement_type=ENTRY_MOVEMENT_TYPE,
                movement_code=WEAVING_SERVICE_ENTRY_MOVEMENT_CODE,
                document_code=ENTRY_DOCUMENT_CODE,
                document_number=entry_number,
                period=form.period,
                creation_date=creation_date,
                creation_time=creation_time,
                item_number=detail.item_number,
                product_code1=detail.fabric_id,
                unit_code="KG",
                factor=1,
                mecsa_weight=mecsa_weight,
                # currency_code=currency_code_value,
                # exchange_rate=exchange_rate_value,
                reference_number=detail.service_order_id,
                # stkgen=,
                # stkalm=,
                nroreq=detail.service_order_id,
                status_flag="P",
            )

            color = "CRUD"
            fabric_id = detail.fabric_id
            if detail._fabric.color:
                color = detail._fabric.color.id
                fabric_id = fabric_id[0:3] + str(round(detail._fabric.density))

            meters_count = (
                detail.guide_net_weight
                * 1000
                / (detail._fabric.density * detail._fabric.width * 2 / 100)
            )
            weaving_service_entry_detail_fabric_value = FabricWarehouse(
                company_code=MECSA_COMPANY_CODE,
                fabric_id=fabric_id,
                width=detail._fabric.width,
                codcol=color,
                guide_net_weight=detail.guide_net_weight,
                mecsa_weight=mecsa_weight,
                document_number=entry_number,
                status_flag="P",
                product_id=detail.fabric_id,
                document_code=ENTRY_DOCUMENT_CODE,
                roll_count=detail.roll_count,
                meters_count=meters_count,
                density=detail._fabric.density,
                real_width=detail._fabric.width,
                yarn_supplier_id=",".join(detail._fabric.supplier_yarn_ids),
                service_order_id=service_order.id,
                tint_supplier_id="",
                fabric_type="C",
                tint_color_id="",
                _tint_supplier_color_id="",
                tint_supplier_color_id="",
            )

            update_result = await self.product_inventory_service.update_current_stock(
                product_code1=detail.fabric_id,
                period=form.period,
                storage_code=WEAVING_STORAGE_CODE,
                new_stock=mecsa_weight,
            )
            if update_result.is_failure:
                return update_result

            update_result = (
                await self.service_order_service.update_quantity_supplied_by_fabric_id(
                    fabric_id=detail.fabric_id,
                    order_id=detail.service_order_id,
                    quantity_supplied=mecsa_weight,
                )
            )
            if update_result.is_failure:
                return update_result

            update_result = await (
                self.service_order_supply_service.update_current_stock_by_fabric_recipe(
                    fabric=detail._fabric,
                    quantity=mecsa_weight,
                    service_orders_stock=detail._service_orders_supply_stock,
                )
            )
            if update_result.is_failure:
                return update_result

            weaving_service_entry_detail_value.detail_fabric = (
                weaving_service_entry_detail_fabric_value
            )
            weaving_service_entry_detail_value.detail_card = card_operations_value
            weaving_service_entry_detail.append(weaving_service_entry_detail_value)
            weaving_service_entry_detail_fabric.append(
                weaving_service_entry_detail_fabric_value
            )

        weaving_service_entry.detail = weaving_service_entry_detail

        creation_result = await self.save_movement(
            movement=weaving_service_entry,
            movement_detail=weaving_service_entry_detail,
            movement_detail_fabric=weaving_service_entry_detail_fabric,
            movement_detail_card=weaving_service_entry_detail_card,
        )

        if creation_result.is_failure:
            return creation_result

        creation_result = await self._create_yarn_weaving_dispatch(
            dispatch_number=dispatch_number,
            supplier=supplier,
            period=form.period,
            current_time=current_time,
            weaving_service_entry_number=entry_number,
            weaving_service_entry_detail=form.detail,
        )

        if creation_result.is_failure:
            return creation_result

        return Success(WeavingServiceEntrySchema.model_validate(weaving_service_entry))

    async def _validate_update_weaving_service_entry(
        self,
        weaving_service_entry: Movement,
    ) -> Result[None, CustomException]:
        if weaving_service_entry.status_flag == "A":
            return WEAVING_SERVICE_ENTRY_FABRIC_ALREADY_ANULLED_FAILURE

        if weaving_service_entry.flgcbd == "S":
            return WEAVING_SERVICE_ENTRY_ALREADY_ACCOUNTED_FAILURE

        for detail in weaving_service_entry.detail:
            for card in detail.detail_card:
                if card.exit_number:
                    return (
                        WEAVING_SERVICE_ENTRY_CARD_OPERATION_ALREADY_DISPATCHED_FAILURE
                    )

        return Success(None)

    async def _rollback_yarn_weaving_dispatch(
        self,
        supplier: SupplierSchema,
        period: int,
        weaving_service_entry_detail: list[MovementDetail],
    ) -> Result[None, CustomException]:
        for detail in weaving_service_entry_detail:
            guide_net_weight = detail.mecsa_weight
            for i in range(len(detail.fabric.recipe)):
                yarn = detail.fabric.recipe[i]
                quantity = round(guide_net_weight * (yarn.proportion / 100.0), 2)

                await self.product_inventory_service.rollback_currents_stock(
                    product_code1=yarn.yarn_id,
                    period=period,
                    storage_code=supplier.storage_code,
                    quantity=-quantity,
                )

        return Success(None)

    async def rollback_weaving_service_entry(
        self,
        period: int,
        weaving_service_entry: Movement,
    ) -> Result[None, CustomException]:
        supplier_result = await self.supplier_service.read_supplier(
            supplier_code=weaving_service_entry.auxiliary_code,
        )
        if supplier_result.is_failure:
            return supplier_result

        supplier: SupplierSchema = supplier_result.value

        for detail in weaving_service_entry.detail:
            rollback_result = (
                await self.product_inventory_service.rollback_currents_stock(
                    product_code1=detail.product_code1,
                    period=period,
                    storage_code=WEAVING_STORAGE_CODE,
                    quantity=detail.mecsa_weight,
                )
            )
            if rollback_result.is_failure:
                return rollback_result

            rollback_result = await self.service_order_service.rollback_quantity_supplied_by_fabric_id(
                fabric_id=detail.product_code1,
                order_id=detail.reference_number,
                quantity_supplied=detail.mecsa_weight,
            )
            if rollback_result.is_failure:
                return rollback_result

            service_orders_stock = await self.service_order_supply_service._read_service_orders_supply_stock(
                storage_code=supplier.storage_code,
                period=period,
                service_order_id=detail.reference_number,
            )
            if service_orders_stock.is_failure:
                return service_orders_stock

            service_orders_stock = service_orders_stock.value

            fabric_result = await self.fabric_service.read_fabric(
                fabric_id=detail.product_code1,
                include_recipe=True,
                include_color=True,
            )
            if fabric_result.is_failure:
                return fabric_result

            fabric = fabric_result.value

            service_orders_stock_result = await self.service_order_supply_service.rollback_current_stock_by_fabric_recipe(
                fabric=fabric,
                quantity=detail.mecsa_weight,
                service_orders_stock=service_orders_stock,
            )
            if service_orders_stock_result.is_failure:
                return service_orders_stock_result

            service_orders_stock = service_orders_stock_result.value

            detail.fabric = fabric

        rollback_result = await self._rollback_yarn_weaving_dispatch(
            supplier=supplier,
            period=period,
            weaving_service_entry_detail=weaving_service_entry.detail,
        )
        if rollback_result.is_failure:
            return rollback_result

        return Success(service_orders_stock)

    async def _delete_detail(
        self,
        weaving_service_entry_detail: MovementDetail,
        supplier: SupplierSchema,
        dispatch_number: str,
    ) -> None:
        filter = (
            (MovementDetail.document_number == dispatch_number)
            & (
                MovementDetail.entry_item_number
                == weaving_service_entry_detail.item_number
            )
            & (MovementDetail.company_code == MECSA_COMPANY_CODE)
            & (MovementDetail.storage_code == supplier.storage_code)
            & (MovementDetail.movement_type == DISPATCH_MOVEMENT_TYPE)
            & (MovementDetail.movement_code == YARN_WEAVING_DISPATCH_MOVEMENT_CODE)
            & (MovementDetail.document_code == DISPATCH_DOCUMENT_CODE)
            & (MovementDetail.period == weaving_service_entry_detail.period)
        )

        yarn_weaving_dispatch_detail = (
            await self.yarn_weaving_dispatch_repository.find_all(
                filter=filter,
            )
        )

        if yarn_weaving_dispatch_detail:
            await self.yarn_weaving_dispatch_repository.delete_all(
                yarn_weaving_dispatch_detail
            )
        await self.card_operation_repository.delete_all(
            weaving_service_entry_detail.detail_card
        )
        await self.fabric_warehouse_repository.delete(
            weaving_service_entry_detail.detail_fabric
        )
        await self.movement_detail_repository.delete(weaving_service_entry_detail)

    async def _delete_weaving_service_entry_detail(
        self,
        weaving_service_entry_detail: list[MovementDetail],
        dispatch_number: str,
        supplier: SupplierSchema,
        form: WeavingServiceEntryUpdateSchema,
    ) -> Result[list[MovementDetail], CustomException]:
        item_numbers = {detail.item_number for detail in form.detail}
        details_to_keep = []

        for detail in weaving_service_entry_detail:
            if detail.item_number not in item_numbers:
                await self._delete_detail(
                    weaving_service_entry_detail=detail,
                    supplier=supplier,
                    dispatch_number=dispatch_number,
                )
            else:
                details_to_keep.append(detail)

        return Success(details_to_keep)

    async def _delete_card(
        self,
        weaving_service_entry_detail_card: CardOperation,
    ) -> Result[None, CustomException]:
        await self.card_operation_repository.delete(weaving_service_entry_detail_card)
        return Success(None)

    async def _delete_weaving_service_entry_detail_card(
        self,
        weaving_service_entry_detail_card: list[CardOperation],
        form: WeavingServiceEntryUpdateSchema,
    ) -> Result[list[CardOperation], CustomException]:
        card_ids = {card.id for detail in form.detail for card in detail.detail_card}
        print(card_ids)
        cards_to_keep = []

        for card in weaving_service_entry_detail_card:
            if card.id not in card_ids:
                delete_result = await self._delete_card(
                    weaving_service_entry_detail_card=card
                )
                if delete_result.is_failure:
                    return delete_result
            else:
                cards_to_keep.append(card)

        return Success(cards_to_keep)

    async def _find_weaving_service_entry_detail(
        self,
        weaving_service_entry_detail: list[MovementDetail],
        item_number: int,
    ) -> Result[MovementDetail, CustomException]:
        for detail in weaving_service_entry_detail:
            if detail.item_number == item_number:
                return Success(detail)

        return Success(None)

    async def _find_weaving_service_entry_detail_card(
        self,
        weaving_service_entry_detail_card: list[CardOperation],
        card_id: str,
        fabric_id: str,
    ) -> Result[CardOperation, CustomException]:
        for card in weaving_service_entry_detail_card:
            if card.id == card_id and card.fabric_id == fabric_id:
                return Success(card)

        return WeavingServiceEntryFailures.WEAVING_SERVICE_ENTRY_CARD_NOT_FOUND_FAILURE

    async def update_weaving_service_entry(
        self,
        form: WeavingServiceEntryUpdateSchema,
        period: int,
        weaving_service_entry_number: str,
    ) -> Result[WeavingServiceEntrySchema, CustomException]:
        weaving_service_entry_result = await self._read_weaving_service_entry(
            weaving_service_entry_number=weaving_service_entry_number,
            period=period,
            include_detail=True,
            include_detail_card=True,
        )
        if weaving_service_entry_result.is_failure:
            return weaving_service_entry_result

        current_time = calculate_time(tz=PERU_TIMEZONE)
        creation_date = current_time.date()

        weaving_service_entry: Movement = weaving_service_entry_result.value
        rolling_back_result = await self.rollback_weaving_service_entry(
            period=period,
            weaving_service_entry=weaving_service_entry,
        )
        if rolling_back_result.is_failure:
            return rolling_back_result

        validation_result = await self._validate_update_weaving_service_entry(
            weaving_service_entry=weaving_service_entry
        )
        if validation_result.is_failure:
            return validation_result

        # validation_result = await self._validate_weaving_service_entry_data(data=form)
        # if validation_result.is_failure:
        #     return validation_result
        #
        # supplier = validation_result.value

        search_result = await self.supplier_service.read_supplier(
            supplier_code=weaving_service_entry.auxiliary_code,
        )
        if search_result.is_failure:
            return search_result

        supplier: SupplierSchema = search_result.value

        validation_result = await self._validate_weaving_service_entry_detail_data(
            data=form.detail,
            supplier=supplier,
            period=period,
            current_date=current_time,
        )
        if validation_result.is_failure:
            return validation_result

        form.detail = validation_result.value[0]
        service_order = validation_result.value[1]

        delete_result = await self._delete_weaving_service_entry_detail(
            weaving_service_entry_detail=weaving_service_entry.detail,
            dispatch_number=weaving_service_entry.reference_number1,
            supplier=supplier,
            form=form,
        )
        if delete_result.is_failure:
            return delete_result

        weaving_service_entry.detail = delete_result.value

        for detail in weaving_service_entry.detail:
            delete_result = await self._delete_weaving_service_entry_detail_card(
                weaving_service_entry_detail_card=detail.detail_card,
                form=form,
            )

            if delete_result.is_failure:
                return delete_result

            detail.detail_card = delete_result.value

        for detail in form.detail:
            weaving_service_entry_detail_result = (
                await self._find_weaving_service_entry_detail(
                    weaving_service_entry_detail=weaving_service_entry.detail,
                    item_number=detail.item_number,
                )
            )
            if weaving_service_entry_detail_result.is_failure:
                return weaving_service_entry_detail_result

            weaving_service_entry_detail = weaving_service_entry_detail_result.value

            guide_net_weight = detail.guide_net_weight

            if weaving_service_entry_detail:
                card_operations_value = []

                if (detail.detail_card and detail.generate_cards) or (
                    weaving_service_entry_detail.detail_card and detail.generate_cards
                ):
                    return WeavingServiceEntryFailures.WEAVING_SERVICE_ENTRY_REGENERATE_CARDS_FAILURE

                if detail.detail_card:
                    for card in detail.detail_card:
                        card_result = await self._find_weaving_service_entry_detail_card(
                            weaving_service_entry_detail_card=weaving_service_entry_detail.detail_card,
                            card_id=card.id,
                            fabric_id=detail.fabric_id,
                        )
                        if card_result.is_failure:
                            return card_result

                        card_value = card_result.value
                        card_value.net_weight = card.net_weight

                        card_operations_value.append(card_value)

                    weaving_service_entry_detail.detail_card = card_operations_value

                elif detail.generate_cards:
                    card_operations_value = await self._generate_cards_operations(
                        supplier_weaving_tej=supplier.code,
                        service_order=service_order,
                        detail=detail,
                        entry_number=weaving_service_entry_number,
                        current_time=current_time,
                        period=period,
                    )

                    if card_operations_value.is_failure:
                        return card_operations_value

                    card_operations_value = card_operations_value.value
                    weaving_service_entry_detail.detail_card = card_operations_value

                mecsa_weight = sum(
                    [
                        card.net_weight
                        for card in weaving_service_entry_detail.detail_card
                    ]
                )
                weaving_service_entry_detail.product_code1 = detail.fabric_id
                weaving_service_entry_detail.mecsa_weight = mecsa_weight
                weaving_service_entry_detail.reference_number = detail.service_order_id
                weaving_service_entry_detail.nroreq = detail.service_order_id

                color = "CRUD"
                fabric_id = detail.fabric_id
                if detail._fabric.color:
                    color = detail._fabric.color.id

                meters_count = (
                    guide_net_weight
                    * 1000
                    / (detail._fabric.density * detail._fabric.width * 2 / 100)
                )

                weaving_service_entry_detail.detail_fabric.fabric_id = fabric_id
                weaving_service_entry_detail.detail_fabric.width = detail._fabric.width
                weaving_service_entry_detail.detail_fabric.codcol = color
                weaving_service_entry_detail.detail_fabric.guide_net_weight = (
                    guide_net_weight
                )
                weaving_service_entry_detail.detail_fabric.mecsa_weight = mecsa_weight
                weaving_service_entry_detail.detail_fabric.product_id = detail.fabric_id
                weaving_service_entry_detail.detail_fabric.roll_count = (
                    detail.roll_count
                )
                weaving_service_entry_detail.detail_fabric.meters_count = meters_count
                weaving_service_entry_detail.detail_fabric.density = (
                    detail._fabric.density
                )
                weaving_service_entry_detail.detail_fabric.real_width = (
                    detail._fabric.width
                )
                weaving_service_entry_detail.detail_fabric.yarn_supplier_id = ",".join(
                    detail._fabric.supplier_yarn_ids
                )
                weaving_service_entry_detail.detail_fabric.service_order_id = (
                    service_order.id
                )

                await self.product_inventory_service.update_current_stock(
                    product_code1=detail.fabric_id,
                    period=period,
                    storage_code=WEAVING_STORAGE_CODE,
                    new_stock=mecsa_weight,
                )

                await self.service_order_service.update_quantity_supplied_by_fabric_id(
                    fabric_id=detail.fabric_id,
                    order_id=detail.service_order_id,
                    quantity_supplied=mecsa_weight,
                )

                await self.service_order_supply_service.update_current_stock_by_fabric_recipe(
                    fabric=detail._fabric,
                    quantity=mecsa_weight,
                    service_orders_stock=detail._service_orders_supply_stock,
                )
            else:
                card_operations_value = []
                if detail.generate_cards:
                    card_operations_value = await self._generate_cards_operations(
                        supplier_weaving_tej=supplier.code,
                        service_order=service_order,
                        detail=detail,
                        entry_number=weaving_service_entry_number,
                        current_time=current_time,
                        period=period,
                    )

                    if card_operations_value.is_failure:
                        return card_operations_value

                    card_operations_value = card_operations_value.value

                mecsa_weight = sum([card.net_weight for card in card_operations_value])

                product_inventory = await self._read_or_create_product_inventory(
                    product_code1=detail.fabric_id,
                    period=period,
                    storage_code=WEAVING_STORAGE_CODE,
                    enable_create=True,
                )

                if product_inventory.is_failure:
                    return product_inventory

                weaving_service_entry_detail_value = MovementDetail(
                    company_code=MECSA_COMPANY_CODE,
                    storage_code=WEAVING_STORAGE_CODE,
                    movement_type=ENTRY_MOVEMENT_TYPE,
                    movement_code=WEAVING_SERVICE_ENTRY_MOVEMENT_CODE,
                    document_code=ENTRY_DOCUMENT_CODE,
                    document_number=weaving_service_entry_number,
                    period=period,
                    creation_date=creation_date,
                    creation_time=current_time.strftime("%H:%M:%S"),
                    item_number=detail.item_number,
                    product_code1=detail.fabric_id,
                    unit_code="KG",
                    factor=1,
                    mecsa_weight=mecsa_weight,
                    # currency_code=currency_code_value,
                    # exchange_rate=exchange_rate_value,
                    reference_number=detail.service_order_id,
                    # stkgen=,
                    # stkalm=,
                    nroreq=detail.service_order_id,
                    status_flag="P",
                )

                color = "CRUD"
                fabric_id = detail.fabric_id
                if detail._fabric.color:
                    color = detail._fabric.color.id

                meters_count = (
                    detail.guide_net_weight
                    * 1000
                    / (detail._fabric.density * detail._fabric.width * 2 / 100)
                )

                weaving_service_entry_detail_fabric_value = FabricWarehouse(
                    company_code=MECSA_COMPANY_CODE,
                    fabric_id=fabric_id,
                    width=detail._fabric.width,
                    codcol=color,
                    guide_net_weight=detail.guide_net_weight,
                    mecsa_weight=mecsa_weight,
                    document_number=weaving_service_entry_number,
                    status_flag="P",
                    product_id=detail.fabric_id,
                    document_code=ENTRY_DOCUMENT_CODE,
                    roll_count=detail.roll_count,
                    meters_count=meters_count,
                    density=detail._fabric.density,
                    real_width=detail._fabric.width,
                    yarn_supplier_id=",".join(detail._fabric.supplier_yarn_ids),
                    service_order_id=service_order.id,
                    tint_supplier_id="",
                    fabric_type="C",
                    tint_color_id="",
                    _tint_supplier_color_id="",
                    tint_supplier_color_id="",
                )

                await self.product_inventory_service.update_current_stock(
                    product_code1=detail.fabric_id,
                    period=period,
                    storage_code=WEAVING_STORAGE_CODE,
                    new_stock=mecsa_weight,
                )

                await self.service_order_service.update_quantity_supplied_by_fabric_id(
                    fabric_id=detail.fabric_id,
                    order_id=detail.service_order_id,
                    quantity_supplied=mecsa_weight,
                )

                await self.service_order_supply_service.update_current_stock_by_fabric_recipe(
                    fabric=detail._fabric,
                    quantity=mecsa_weight,
                    service_orders_stock=detail._service_orders_supply_stock,
                )

                weaving_service_entry_detail_value.detail_fabric = (
                    weaving_service_entry_detail_fabric_value
                )
                weaving_service_entry_detail_value.detail_card = card_operations_value
                weaving_service_entry.detail.append(weaving_service_entry_detail_value)

        creation_result = await self.save_movement(
            movement=weaving_service_entry,
            movement_detail=weaving_service_entry.detail,
            movement_detail_fabric=[
                detail.detail_fabric for detail in weaving_service_entry.detail
            ],
            movement_detail_card=[
                card
                for detail in weaving_service_entry.detail
                for card in detail.detail_card
            ],
        )

        if creation_result.is_failure:
            return creation_result

        return Success(WeavingServiceEntrySchema.model_validate(weaving_service_entry))

    async def anulate_weaving_service_entry(
        self,
        period: int,
        weaving_service_entry_number: str,
    ) -> Result[None, CustomException]:
        weaving_service_entry_result = await self._read_weaving_service_entry(
            weaving_service_entry_number=weaving_service_entry_number,
            period=period,
            include_detail=True,
            include_detail_card=True,
        )

        if weaving_service_entry_result.is_failure:
            return weaving_service_entry_result

        weaving_service_entry: Movement = weaving_service_entry_result.value

        validation_result = await self._validate_update_weaving_service_entry(
            weaving_service_entry=weaving_service_entry
        )
        if validation_result.is_failure:
            return validation_result

        supplier = await self.supplier_service.read_supplier(
            supplier_code=weaving_service_entry.auxiliary_code,
        )
        if supplier.is_failure:
            return supplier

        rolling_back_result = await self.rollback_weaving_service_entry(
            period=period,
            weaving_service_entry=weaving_service_entry,
        )
        if rolling_back_result.is_failure:
            return rolling_back_result

        for detail in weaving_service_entry.detail:
            detail.status_flag = "A"
            detail.detail_fabric.status_flag = "A"

            for card in detail.detail_card:
                card.status_flag = "A"

        weaving_service_entry.status_flag = "A"

        await self.save_movement(
            movement=weaving_service_entry,
            movement_detail=weaving_service_entry.detail,
            movement_detail_fabric=[
                detail.detail_fabric for detail in weaving_service_entry.detail
            ],
            movement_detail_card=[
                card
                for detail in weaving_service_entry.detail
                for card in detail.detail_card
            ],
        )

        return Success(None)

    async def is_updated_permission(
        self,
        period: int,
        weaving_service_entry_number: str,
    ) -> Result[None, CustomException]:
        weaving_service_entry_result = await self._read_weaving_service_entry(
            weaving_service_entry_number=weaving_service_entry_number,
            period=period,
            include_detail=True,
            include_detail_card=True,
        )

        if weaving_service_entry_result.is_failure:
            return weaving_service_entry_result

        weaving_service_entry: Movement = weaving_service_entry_result.value

        validation_result = await self._validate_update_weaving_service_entry(
            weaving_service_entry=weaving_service_entry
        )

        if validation_result.is_failure:
            return validation_result

        return Success(None)

    async def print_weaving_service_entry(
        self,
        form: WeavingServiceEntryPrintListSchema,
    ):
        card_ids = [card.card_id for card in form.card_ids]

        card_operations_value = (
            await self.card_operation_service.reads_card_operation_by_id(
                ids=card_ids,
            )
        )

        if card_operations_value.is_failure:
            return card_operations_value
        card_operations = card_operations_value.value

        pdf = generate_pdf_cards(cards=card_operations)

        return Success(pdf)
