from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.constants import MECSA_COMPANY_CODE
from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.core.utils import PERU_TIMEZONE, calculate_time
from src.operations.constants import (
    DISPATCH_MOVEMENT_TYPE,
    DYEING_SERVICE_DISPATCH_DOCUMENT_CODE,
    DYEING_SERVICE_DISPATCH_MOVEMENT_CODE,
    ENTRY_DOCUMENT_CODE,
    ENTRY_MOVEMENT_TYPE,
    SERVICE_CODE_SUPPLIER_DYEING,
    WEAVING_STORAGE_CODE,
)
from src.operations.failures import (
    DYEING_SERVICE_DISPATCH_ALREADY_ACCOUNTED_FAILURE,
    DYEING_SERVICE_DISPATCH_ANULLED_FAILURE,
    DYEING_SERVICE_DISPATCH_CARD_OPERATION_ALREADY_ASSOCIATED_FAILURE,
    DYEING_SERVICE_DISPATCH_CARD_OPERATION_ANULLED_FAILURE,
    DYEING_SERVICE_DISPATCH_CARD_OPERATION_NOT_ASSOCIATED_SUPPLIER_FAILURE,
    DYEING_SERVICE_DISPATCH_NOT_ASSOCIATED_SUPPLIER_FAILURE,
    DYEING_SERVICE_DISPATCH_NOT_ASSOCIATED_SUPPLIER_STORAGE_FAILURE,
    DYEING_SERVICE_DISPATCH_NOT_FOUND_FAILURE,
    DYEING_SERVICE_DISPATCH_SUPPLIER_NOT_ASSOCIATED_ADDRESS_FAILURE,
    DYEING_SERVICE_DISPATCH_SUPPLIER_NOT_ASSOCIATED_COLOR_ID_FAILURE,
)
from src.operations.models import (
    CardOperation,
    FabricWarehouse,
    Movement,
    MovementDetail,
)
from src.operations.repositories import (
    DyeingServiceDispatchRepository,
)
from src.operations.schemas import (
    DyeingServiceDispatchCreateSchema,
    DyeingServiceDispatchDetailCreateSchema,
    DyeingServiceDispatchesListSchema,
    DyeingServiceDispatchSchema,
    DyeingServiceDispatchUpdateSchema,
    SupplierSchema,
)
from src.operations.utils.movements.dyeing_service_dispatch.pdf import generate_pdf

from .card_operation_service import CardOperationService
from .fabric_service import FabricService
from .movement_service import MovementService
from .product_inventory_service import ProductInventoryService
from .series_service import (
    DyeingServiceDispatchSeries,
    EntrySeries,
)
from .supplier_service import SupplierService


class DyeingServiceDispatchService(MovementService):
    def __init__(self, promec_db: AsyncSession, db: AsyncSession) -> None:
        super().__init__(promec_db=promec_db)
        self.repository = DyeingServiceDispatchRepository(promec_db=promec_db)
        self.supplier_service = SupplierService(
            promec_db=promec_db,
        )
        self.card_operation_service = CardOperationService(
            promec_db=promec_db,
        )
        self.dyeing_service_dispatch_series = DyeingServiceDispatchSeries(
            promec_db=promec_db,
        )
        self.entry_series = EntrySeries(
            promec_db=promec_db,
        )
        self.fabric_service = FabricService(
            promec_db=promec_db,
            db=db,
        )
        self.product_inventory_service = ProductInventoryService(
            promec_db=promec_db,
        )

    async def read_dyeing_service_dispatches(
        self,
        period: int,
        limit: int = None,
        offset: int = None,
        include_annulled: bool = False,
    ) -> Result[DyeingServiceDispatchesListSchema, CustomException]:
        dyeing_service_dispatches = (
            await self.repository.find_dyeing_service_dispatches(
                period=period,
                limit=limit,
                offset=offset,
                include_annulled=include_annulled,
            )
        )

        return Success(
            DyeingServiceDispatchesListSchema(
                dyeing_service_dispatches=dyeing_service_dispatches
            )
        )

    async def _read_dyeing_service_dispatch(
        self,
        dyeing_service_dispatch_number: str,
        period: int,
        include_detail: bool = False,
        include_detail_card: bool = False,
    ) -> Result[Movement, CustomException]:
        dyeing_service_dispatch = (
            await self.repository.find_dyeing_service_dispatch_by_dispatch_number(
                dispatch_number=dyeing_service_dispatch_number,
                period=period,
                include_detail=include_detail,
                include_detail_card=include_detail_card,
            )
        )

        if dyeing_service_dispatch is None:
            return DYEING_SERVICE_DISPATCH_NOT_FOUND_FAILURE

        return Success(dyeing_service_dispatch)

    async def read_dyeing_service_dispatch(
        self,
        dyeing_service_dispatch_number: str,
        period: int,
        include_detail: bool = False,
        include_detail_card: bool = False,
    ) -> Result[DyeingServiceDispatchSchema, CustomException]:
        dyeing_service_dispatch = await self._read_dyeing_service_dispatch(
            dyeing_service_dispatch_number=dyeing_service_dispatch_number,
            period=period,
            include_detail=include_detail,
            include_detail_card=include_detail_card,
        )

        if dyeing_service_dispatch.is_failure:
            return dyeing_service_dispatch

        return Success(
            DyeingServiceDispatchSchema.model_validate(dyeing_service_dispatch.value)
        )

    async def _validate_dyeing_service_dispatch_data(
        self,
        data: DyeingServiceDispatchCreateSchema,
    ) -> Result[None, CustomException]:
        validation_result = await self.supplier_service.read_supplier(
            supplier_code=data.supplier_id,
            include_service=True,
            include_colors=True,
        )

        if validation_result.is_failure:
            return validation_result

        supplier = validation_result.value

        if supplier.storage_code == "":
            return DYEING_SERVICE_DISPATCH_NOT_ASSOCIATED_SUPPLIER_STORAGE_FAILURE

        services = [service.service_code for service in supplier.services]

        if SERVICE_CODE_SUPPLIER_DYEING not in services:
            return DYEING_SERVICE_DISPATCH_NOT_ASSOCIATED_SUPPLIER_FAILURE

        if data.nrodir not in supplier.addresses.keys():
            return DYEING_SERVICE_DISPATCH_SUPPLIER_NOT_ASSOCIATED_ADDRESS_FAILURE

        color_ids = [color.id for color in supplier.colors]

        if data.tint_supplier_color_id not in color_ids:
            return DYEING_SERVICE_DISPATCH_SUPPLIER_NOT_ASSOCIATED_COLOR_ID_FAILURE

        return Success(supplier)

    async def _validate_dyeing_service_dispatch_detail_data(
        self,
        period: int,
        supplier: SupplierSchema,
        data: list[DyeingServiceDispatchDetailCreateSchema],
    ) -> Result[None, CustomException]:
        for detail in data:
            validation_result = await self.card_operation_service._read_card_operation(
                id=detail.card_id,
            )

            if validation_result.is_failure:
                return validation_result

            card_operation = validation_result.value
            if card_operation.exit_number:
                return DYEING_SERVICE_DISPATCH_CARD_OPERATION_ALREADY_ASSOCIATED_FAILURE

            if card_operation.status_flag == "A":
                return DYEING_SERVICE_DISPATCH_CARD_OPERATION_ANULLED_FAILURE

            if card_operation.tint_supplier_id:
                if card_operation.tint_supplier_id != supplier.code:
                    return DYEING_SERVICE_DISPATCH_CARD_OPERATION_NOT_ASSOCIATED_SUPPLIER_FAILURE

            detail._card_operation = card_operation

        return Success(data)

    async def _create_dyeing_service_entry(
        self,
        supplier: SupplierSchema,
        period: int,
        current_time: datetime,
        dyeing_service_dispatch_number: str,
        fabric_id_detail: dict,
    ) -> Result[None, CustomException]:
        entry_number = await self.entry_series.next_number()

        creation_date = current_time.date()
        creation_time = current_time.strftime("%H:%M:%S")

        dyeing_service_entry = Movement(
            company_code=MECSA_COMPANY_CODE,
            storage_code=supplier.storage_code,
            movement_type=ENTRY_MOVEMENT_TYPE,
            document_code=ENTRY_DOCUMENT_CODE,
            movement_code=DYEING_SERVICE_DISPATCH_MOVEMENT_CODE,
            document_number=entry_number,
            period=period,
            creation_date=creation_date,
            creation_time=creation_time,
            clfaux="_PRO",
            auxiliary_code=supplier.code,
            reference_code=DYEING_SERVICE_DISPATCH_DOCUMENT_CODE,
            reference_number1=dyeing_service_dispatch_number,
            status_flag="P",
            user_id="DESA01",
            auxiliary_name=supplier.name,
            reference_document=DYEING_SERVICE_DISPATCH_DOCUMENT_CODE,
            reference_number2=dyeing_service_dispatch_number,
            origmov="A",
            serial_number="001",
            printed_flag="N",
            flgact="N",
            nrodir1="000",
            flgtras=False,
            flgreclamo="N",
            flgsit="A",
            servadi="N",
            tarfservadi=False,
            flgcbd="N",
            nrodir2="000",
            origin_station="SERVIDORDESA",
            flgele="P",
            undpesobrutototal="KGM",
            transaction_mode="02",
            intentosenvele=0,
        )

        dyeing_service_entry_detail = []

        item_number = 1
        for fabric in fabric_id_detail:
            dyeing_service_entry_detail_value = MovementDetail(
                company_code=MECSA_COMPANY_CODE,
                storage_code=supplier.storage_code,
                movement_type=ENTRY_MOVEMENT_TYPE,
                document_code=ENTRY_DOCUMENT_CODE,
                movement_code=DYEING_SERVICE_DISPATCH_MOVEMENT_CODE,
                document_number=entry_number,
                period=period,
                creation_date=creation_date,
                creation_time=creation_time,
                item_number=item_number,
                product_code=fabric,
                unit_code="KG",
                factor=1,
                mecsa_weight=fabric_id_detail[fabric]["net_weight"],
                reference_code=DYEING_SERVICE_DISPATCH_DOCUMENT_CODE,
                reference_number=dyeing_service_dispatch_number,
                # stkgen=,
                # stkalm=,
                status_flag="P",
            )

            dyeing_service_entry_detail.append(dyeing_service_entry_detail_value)
            item_number += 1

            await self.product_inventory_service.update_current_stock(
                product_code=fabric,
                period=period,
                storage_code=supplier.storage_code,
                new_stock=fabric_id_detail[fabric]["net_weight"],
            )

        await self.save_movement(
            movement=dyeing_service_entry,
            movement_detail=dyeing_service_entry_detail,
        )

        return Success(entry_number)

    def _assign_fabric_id_detail(
        self, data: list[DyeingServiceDispatchDetailCreateSchema]
    ) -> Result[dict, CustomException]:
        fabric_id_detail = {}

        for detail in data:
            card_operation = detail._card_operation

            if card_operation.product_id not in fabric_id_detail:
                fabric_id_detail[card_operation.product_id] = {
                    "net_weight": card_operation.net_weight,
                    "roll_count": 1,
                    "cards": [card_operation],
                }
            else:
                fabric_id_detail[card_operation.product_id]["net_weight"] += (
                    card_operation.net_weight
                )
                fabric_id_detail[card_operation.product_id]["roll_count"] += 1
                fabric_id_detail[card_operation.product_id]["cards"].append(
                    card_operation
                )

        return Success(fabric_id_detail)

    async def create_dyeing_service_dispatch(
        self,
        form: DyeingServiceDispatchCreateSchema,
    ) -> Result[DyeingServiceDispatchSchema, CustomException]:
        validation_result = await self._validate_dyeing_service_dispatch_data(
            data=form,
        )
        if validation_result.is_failure:
            return validation_result

        supplier = validation_result.value

        validation_result = await self._validate_dyeing_service_dispatch_detail_data(
            period=form.period,
            data=form.detail,
            supplier=supplier,
        )
        if validation_result.is_failure:
            return validation_result

        form.detail = validation_result.value

        dispatch_number = await self.dyeing_service_dispatch_series.next_number()

        current_time = calculate_time(tz=PERU_TIMEZONE)

        fabric_id_detail_result = self._assign_fabric_id_detail(data=form.detail)
        if fabric_id_detail_result.is_failure:
            return fabric_id_detail_result

        fabric_id_detail = fabric_id_detail_result.value

        creation_result = await self._create_dyeing_service_entry(
            supplier=supplier,
            period=form.period,
            current_time=current_time,
            dyeing_service_dispatch_number=dispatch_number,
            fabric_id_detail=fabric_id_detail,
        )
        if creation_result.is_failure:
            return creation_result

        entry_number = creation_result.value

        creation_date = current_time.date()
        creation_time = current_time.strftime("%H:%M:%S")

        sequence_number = await self.supplier_service.next_service_sequence(
            supplier_code=supplier.code,
            service_code=SERVICE_CODE_SUPPLIER_DYEING,
        )
        if sequence_number.is_failure:
            return sequence_number

        order_service_number = str(sequence_number.value).zfill(7)

        dyeing_service_dispatch = Movement(
            company_code=MECSA_COMPANY_CODE,
            storage_code=WEAVING_STORAGE_CODE,
            movement_type=DISPATCH_MOVEMENT_TYPE,
            document_code=DYEING_SERVICE_DISPATCH_DOCUMENT_CODE,
            movement_code=DYEING_SERVICE_DISPATCH_MOVEMENT_CODE,
            document_number=dispatch_number,
            period=form.period,
            creation_date=creation_date,
            creation_time=creation_time,
            document_note=form.document_note,
            clfaux="_PRO",
            auxiliary_code=form.supplier_id,
            reference_code=ENTRY_DOCUMENT_CODE,
            reference_number1=entry_number,
            status_flag="P",
            user_id="DESA01",
            auxiliary_name=supplier.name,
            reference_document="O/S",
            reference_number2=order_service_number,
            origmov="A",
            serial_number="104",
            printed_flag="N",
            flgact="N",
            nrodir1="000",
            transaction_motive="17",
            flgtras=False,
            empqnro2=form.tint_supplier_color_id,
            flgreclamo="N",
            flgsit="A",
            servadi="N",
            tarfservadi=False,
            flgcbd="N",
            nrodir2=form.nrodir,
            origin_station="SERVIDORDESA",
            flgele="P",
            prefele="T",
            undpesobrutototal="KGM",
            transaction_mode="01",
            intentosenvele=0,
        )

        dyeing_service_dispatch_detail = []
        dyeing_service_dispatch_detail_card = []
        cards = []
        item_number = 1
        for detail in fabric_id_detail:
            fabric_id = detail
            net_weight = fabric_id_detail[detail]["net_weight"]
            roll_count = fabric_id_detail[detail]["roll_count"]
            detail_cards = fabric_id_detail[detail]["cards"]
            fabric_result = await self.fabric_service.read_fabric(
                fabric_id=fabric_id,
                include_color=True,
            )
            if fabric_result.is_failure:
                return fabric_result

            fabric = fabric_result.value
            codcol = "CRUD"
            if fabric.color:
                codcol = fabric.color.id

            meters_count = round(
                (net_weight * 1000 / (fabric.density * fabric.width * 2 / 100)), 2
            )
            dyeing_service_dispatch_detail_value = FabricWarehouse(
                company_code=MECSA_COMPANY_CODE,
                fabric_id=fabric_id,
                width=fabric.width,
                codcol=codcol,
                guide_net_weight=net_weight,
                mecsa_weight=net_weight,
                document_number=dispatch_number,
                status_flag="P",
                product_id=fabric_id,
                document_code=DYEING_SERVICE_DISPATCH_DOCUMENT_CODE,
                roll_count=roll_count,
                meters_count=meters_count,
                density=fabric.density,
                real_width=fabric.width,
            )

            for detail_card in detail_cards:
                dyeing_service_dispatch_detail_card_value = MovementDetail(
                    company_code=MECSA_COMPANY_CODE,
                    storage_code=WEAVING_STORAGE_CODE,
                    movement_type=DISPATCH_MOVEMENT_TYPE,
                    document_code=DYEING_SERVICE_DISPATCH_DOCUMENT_CODE,
                    movement_code=DYEING_SERVICE_DISPATCH_MOVEMENT_CODE,
                    document_number=dispatch_number,
                    period=form.period,
                    creation_date=creation_date,
                    creation_time=creation_time,
                    item_number=item_number,
                    product_code=fabric_id,
                    unit_code="KG",
                    factor=1,
                    mecsa_weight=detail_card.net_weight,
                    reference_code="O/S",
                    reference_number=order_service_number,
                    # stkgen=,
                    # stkalm=,
                    # ctomn1=,
                    # ctomn2=,
                    nrotarj=detail_card.id,
                    status_flag="P",
                )

                dyeing_service_dispatch_detail_card.append(
                    dyeing_service_dispatch_detail_card_value
                )
                item_number += 1

                await self.product_inventory_service.update_current_stock(
                    product_code=fabric_id,
                    period=form.period,
                    storage_code=WEAVING_STORAGE_CODE,
                    new_stock=-detail_card.net_weight,
                )

            for card in detail_cards:
                card.exit_number = (
                    DYEING_SERVICE_DISPATCH_DOCUMENT_CODE + dispatch_number
                )
                card.status_flag = "C"

            dyeing_service_dispatch_detail_value.detail_card = detail_cards
            cards.extend(detail_cards)
            dyeing_service_dispatch_detail.append(dyeing_service_dispatch_detail_value)

        dyeing_service_dispatch.detail_dyeing = dyeing_service_dispatch_detail

        creation_result = await self.save_movement(
            movement=dyeing_service_dispatch,
            movement_detail=dyeing_service_dispatch_detail_card,
            movement_detail_fabric=dyeing_service_dispatch_detail,
            movement_detail_card=cards,
        )

        return Success(
            DyeingServiceDispatchSchema.model_validate(dyeing_service_dispatch)
        )

    async def _delete_card_operation_and_update_list(
        self,
        target_card: CardOperation,
        existing_movements: list[MovementDetail],
    ) -> Result[list[MovementDetail], CustomException]:
        # await self.card_operation_repository.save(target_card)

        remaining_movements = []
        for movement in existing_movements:
            if movement.nrotarj == target_card.id:
                await self.movement_detail_repository.delete(movement)
            else:
                remaining_movements.append(movement)

        return Success(remaining_movements)

    # async def _delete_dyeing_service_entry(
    #     self,
    #
    # )

    async def _delete_dyeing_service_dispatch_details(
        self,
        fabric_warehouses: list[FabricWarehouse],
        movement_details: list[MovementDetail],
        update_form: DyeingServiceDispatchUpdateSchema,
    ) -> Result[tuple[list[FabricWarehouse], list[MovementDetail]], CustomException]:
        form_card_ids = {form_detail.card_id for form_detail in update_form.detail}
        updated_movements = movement_details.copy()

        for warehouse in fabric_warehouses:
            remaining_cards = []
            for card in warehouse.detail_card:
                if card.id not in form_card_ids:
                    delete_result = await self._delete_card_operation_and_update_list(
                        target_card=card,
                        existing_movements=updated_movements,
                    )
                    if delete_result.is_failure:
                        return delete_result

                    updated_movements = delete_result.value
                else:
                    remaining_cards.append(card)

            warehouse.detail_card = remaining_cards

        filtered_warehouses = []
        for warehouse in fabric_warehouses:
            if warehouse.product_id in {
                detail.product_code for detail in updated_movements
            }:
                filtered_warehouses.append(warehouse)
            else:
                await self.fabric_warehouse_repository.delete(warehouse)

        return Success((fabric_warehouses, updated_movements))

    async def rollback_dyeing_service_dispatch(
        self,
        period: int,
        dyeing_service_dispatch: Movement,
    ) -> Result[None, CustomException]:
        supplier_result = await self.supplier_service.read_supplier(
            supplier_code=dyeing_service_dispatch.auxiliary_code,
        )
        if supplier_result.is_failure:
            return supplier_result

        supplier = supplier_result.value

        for detail in dyeing_service_dispatch.detail_dyeing:
            await self.product_inventory_service.rollback_currents_stock(
                product_code=detail.product_id,
                period=period,
                storage_code=supplier.storage_code,
                quantity=detail.guide_net_weight,
            )

            await self.product_inventory_service.rollback_currents_stock(
                product_code=detail.product_id,
                period=period,
                storage_code=WEAVING_STORAGE_CODE,
                quantity=-detail.guide_net_weight,
            )

            for detail_card in detail.detail_card:
                detail_card.exit_number = None
                detail_card.status_flag = "P"

        return Success(None)

    async def _reads_dyeing_service_dispatch_detail(
        self,
        dyeing_service_dispatch_number: str,
        period: int,
    ) -> Result[list[MovementDetail], CustomException]:
        dyeing_service_dispatch_detail = await self.repository.find_dyeing_service_dispatch_details_by_dispatch_number(
            dispatch_number=dyeing_service_dispatch_number,
            period=period,
        )

        return Success(dyeing_service_dispatch_detail)

    async def _validate_update_dyeing_service_dispatch(
        self,
        dyeing_service_dispatch: Movement,
    ) -> Result[None, CustomException]:
        if dyeing_service_dispatch.status_flag == "A":
            return DYEING_SERVICE_DISPATCH_ANULLED_FAILURE

        if dyeing_service_dispatch.flgcbd == "S":
            return DYEING_SERVICE_DISPATCH_ALREADY_ACCOUNTED_FAILURE

        return Success(None)

    async def _find_dyeing_service_dispatch_detail_card(
        self,
        movement_detail: list[MovementDetail],
        card_id: str,
    ) -> Result[MovementDetail, CustomException]:
        for detail in movement_detail:
            if detail.nrotarj == card_id:
                return Success(detail)

        return Success(None)

    async def _find_dyeing_service_dispatch_detail(
        self,
        warehouses: list[FabricWarehouse],
        fabric_id: str,
    ) -> Result[FabricWarehouse, CustomException]:
        for warehouse in warehouses:
            if warehouse.product_id == fabric_id:
                return Success(warehouse)
        return Success(None)

    async def _delete_dyeing_service_entry(
        self,
        entry_number: str,
        supplier: SupplierSchema,
        period: int,
    ) -> Result[None, CustomException]:
        filter = (
            (Movement.storage_code == supplier.storage_code)
            & (Movement.movement_type == ENTRY_MOVEMENT_TYPE)
            & (Movement.movement_code == DYEING_SERVICE_DISPATCH_MOVEMENT_CODE)
            & (Movement.document_code == ENTRY_DOCUMENT_CODE)
            & (Movement.period == period)
        )
        options = [joinedload(Movement.detail)]

        entry_movement = await self.repository.find_movement_by_document_number(
            document_number=entry_number,
            filter=filter,
            options=options,
        )

        if entry_movement:
            await self.movement_detail_repository.delete_all(entry_movement.detail)
            await self.repository.delete(entry_movement)

        return Success(None)

    async def update_dyeing_service_dispatch(
        self,
        dyeing_service_dispatch_number: str,
        period: int,
        form: DyeingServiceDispatchUpdateSchema,
    ) -> Result[DyeingServiceDispatchSchema, CustomException]:
        dyeing_service_dispatch_result = await self._read_dyeing_service_dispatch(
            dyeing_service_dispatch_number=dyeing_service_dispatch_number,
            period=period,
            include_detail=True,
            include_detail_card=True,
        )
        if dyeing_service_dispatch_result.is_failure:
            return dyeing_service_dispatch_result

        dyeing_service_dispatch: Movement = dyeing_service_dispatch_result.value

        dyeing_service_dispatch_detail_result = (
            await self._reads_dyeing_service_dispatch_detail(
                dyeing_service_dispatch_number=dyeing_service_dispatch_number,
                period=period,
            )
        )
        if dyeing_service_dispatch_detail_result.is_failure:
            return dyeing_service_dispatch_detail_result

        dyeing_service_dispatch_detail_card = (
            dyeing_service_dispatch_detail_result.value
        )

        validation_result = await self._validate_update_dyeing_service_dispatch(
            dyeing_service_dispatch=dyeing_service_dispatch,
        )
        if validation_result.is_failure:
            return validation_result

        rollback_result = await self.rollback_dyeing_service_dispatch(
            period=period,
            dyeing_service_dispatch=dyeing_service_dispatch,
        )
        if rollback_result.is_failure:
            return rollback_result

        validation_result = await self._validate_dyeing_service_dispatch_data(
            data=form,
        )
        if validation_result.is_failure:
            return validation_result

        supplier = validation_result.value

        validation_result = await self._validate_dyeing_service_dispatch_detail_data(
            period=period,
            data=form.detail,
            supplier=supplier,
        )
        if validation_result.is_failure:
            return validation_result

        form.detail = validation_result.value

        # //! TODO: Movimientos alternos
        delete_result = await self._delete_dyeing_service_dispatch_details(
            fabric_warehouses=dyeing_service_dispatch.detail_dyeing,
            movement_details=dyeing_service_dispatch_detail_card,
            update_form=form,
        )
        if delete_result.is_failure:
            return delete_result

        dyeing_service_dispatch.detail_dyeing = delete_result.value[0]
        dyeing_service_dispatch_detail_card_before = delete_result.value[1]

        delete_result = await self._delete_dyeing_service_entry(
            entry_number=dyeing_service_dispatch.reference_number1,
            supplier=supplier,
            period=period,
        )
        if delete_result.is_failure:
            return delete_result

        fabric_id_detail_result = self._assign_fabric_id_detail(data=form.detail)
        if fabric_id_detail_result.is_failure:
            return fabric_id_detail_result
        fabric_id_detail = fabric_id_detail_result.value

        current_time = calculate_time(tz=PERU_TIMEZONE)
        creation_date = current_time.date()
        creation_time = current_time.strftime("%H:%M:%S")

        creation_result = await self._create_dyeing_service_entry(
            supplier=supplier,
            period=period,
            current_time=current_time,
            dyeing_service_dispatch_number=dyeing_service_dispatch_number,
            fabric_id_detail=fabric_id_detail,
        )
        if creation_result.is_failure:
            return creation_result

        entry_number = creation_result.value

        item_number = 1
        if dyeing_service_dispatch_detail_card_before:
            item_number = (
                max(
                    [
                        detail.item_number
                        for detail in dyeing_service_dispatch_detail_card_before
                    ]
                )
                + 1
            )

        dyeing_service_dispatch_detail = []
        dyeing_service_dispatch_detail_card = []
        cards = []

        dyeing_service_dispatch.reference_number1 = entry_number

        for detail in fabric_id_detail:
            dyeing_service_dispatch_detail_result = (
                await self._find_dyeing_service_dispatch_detail(
                    warehouses=dyeing_service_dispatch.detail_dyeing,
                    fabric_id=detail,
                )
            )
            if dyeing_service_dispatch_detail_result.is_failure:
                return dyeing_service_dispatch_detail_result
            dyeing_service_dispatch_detail_value = (
                dyeing_service_dispatch_detail_result.value
            )

            fabric_id = detail
            net_weight = fabric_id_detail[detail]["net_weight"]
            roll_count = fabric_id_detail[detail]["roll_count"]
            detail_cards = fabric_id_detail[detail]["cards"]
            fabric_result = await self.fabric_service.read_fabric(
                fabric_id=fabric_id,
                include_color=True,
            )
            if fabric_result.is_failure:
                return fabric_result

            fabric = fabric_result.value
            codcol = "CRUD"
            if fabric.color:
                codcol = fabric.color.id

            meters_count = round(
                (net_weight * 1000 / (fabric.density * fabric.width * 2 / 100)), 2
            )

            if dyeing_service_dispatch_detail_value:
                dyeing_service_dispatch_detail_value.guide_net_weight = net_weight
                dyeing_service_dispatch_detail_value.mecsa_weight = net_weight
                dyeing_service_dispatch_detail_value.roll_count = roll_count
                dyeing_service_dispatch_detail_value.meters_count = meters_count

                for detail_card in detail_cards:
                    dyeing_service_dispatch_detail_card_result = (
                        await self._find_dyeing_service_dispatch_detail_card(
                            movement_detail=dyeing_service_dispatch_detail_card_before,
                            card_id=detail_card.id,
                        )
                    )
                    if dyeing_service_dispatch_detail_card_result.is_failure:
                        return dyeing_service_dispatch_detail_card_result
                    dyeing_service_dispatch_detail_card_value = (
                        dyeing_service_dispatch_detail_card_result.value
                    )

                    if dyeing_service_dispatch_detail_card_value:
                        continue
                    else:
                        dyeing_service_dispatch_detail_card_value = MovementDetail(
                            company_code=MECSA_COMPANY_CODE,
                            storage_code=WEAVING_STORAGE_CODE,
                            movement_type=DISPATCH_MOVEMENT_TYPE,
                            document_code=DYEING_SERVICE_DISPATCH_DOCUMENT_CODE,
                            movement_code=DYEING_SERVICE_DISPATCH_MOVEMENT_CODE,
                            document_number=dyeing_service_dispatch_number,
                            period=period,
                            creation_date=creation_date,
                            creation_time=creation_time,
                            item_number=item_number,
                            product_code=fabric_id,
                            unit_code="KG",
                            factor=1,
                            mecsa_weight=detail_card.net_weight,
                            reference_code="O/S",
                            reference_number=dyeing_service_dispatch.reference_number2,
                            # stkgen=,
                            # stkalm=,
                            # ctomn1=,
                            # ctomn2=,
                            nrotarj=detail_card.id,
                            status_flag="P",
                        )

                        dyeing_service_dispatch_detail_card.append(
                            dyeing_service_dispatch_detail_card_value
                        )
                        item_number += 1

                        await self.product_inventory_service.update_current_stock(
                            product_code=fabric_id,
                            period=period,
                            storage_code=WEAVING_STORAGE_CODE,
                            new_stock=-detail_card.net_weight,
                        )

                for card in detail_cards:
                    card.exit_number = (
                        DYEING_SERVICE_DISPATCH_DOCUMENT_CODE
                        + dyeing_service_dispatch_number
                    )
                    card.status_flag = "C"

                dyeing_service_dispatch_detail_value.detail_card = detail_cards
                cards.extend(detail_cards)
                dyeing_service_dispatch_detail.append(
                    dyeing_service_dispatch_detail_value
                )
            else:
                dyeing_service_dispatch_detail_value = FabricWarehouse(
                    company_code=MECSA_COMPANY_CODE,
                    fabric_id=fabric_id,
                    width=fabric.width,
                    codcol=codcol,
                    guide_net_weight=net_weight,
                    mecsa_weight=net_weight,
                    document_number=dyeing_service_dispatch_number,
                    status_flag="P",
                    product_id=fabric_id,
                    document_code=DYEING_SERVICE_DISPATCH_DOCUMENT_CODE,
                    roll_count=roll_count,
                    meters_count=meters_count,
                    density=fabric.density,
                    real_width=fabric.width,
                )

                for detail_card in detail_cards:
                    dyeing_service_dispatch_detail_card_value = MovementDetail(
                        company_code=MECSA_COMPANY_CODE,
                        storage_code=WEAVING_STORAGE_CODE,
                        movement_type=DISPATCH_MOVEMENT_TYPE,
                        document_code=DYEING_SERVICE_DISPATCH_DOCUMENT_CODE,
                        movement_code=DYEING_SERVICE_DISPATCH_MOVEMENT_CODE,
                        document_number=dyeing_service_dispatch_number,
                        period=period,
                        creation_date=creation_date,
                        creation_time=creation_time,
                        item_number=item_number,
                        product_code=fabric_id,
                        unit_code="KG",
                        factor=1,
                        mecsa_weight=detail_card.net_weight,
                        reference_code="O/S",
                        reference_number=dyeing_service_dispatch.reference_number2,
                        # stkgen=,
                        # stkalm=,
                        # ctomn1=,
                        # ctomn2=,
                        nrotarj=detail_card.id,
                        status_flag="P",
                    )

                    dyeing_service_dispatch_detail_card.append(
                        dyeing_service_dispatch_detail_card_value
                    )
                    item_number += 1

                    await self.product_inventory_service.update_current_stock(
                        product_code=fabric_id,
                        period=period,
                        storage_code=WEAVING_STORAGE_CODE,
                        new_stock=-detail_card.net_weight,
                    )

                for card in detail_cards:
                    card.exit_number = (
                        DYEING_SERVICE_DISPATCH_DOCUMENT_CODE
                        + dyeing_service_dispatch_number
                    )
                    card.status_flag = "C"

                dyeing_service_dispatch_detail_value.detail_card = detail_cards
                cards.extend(detail_cards)
                dyeing_service_dispatch_detail.append(
                    dyeing_service_dispatch_detail_value
                )

        dyeing_service_dispatch.detail_dyeing = dyeing_service_dispatch_detail

        creation_result = await self.save_movement(
            movement=dyeing_service_dispatch,
            movement_detail=dyeing_service_dispatch_detail_card,
            movement_detail_fabric=dyeing_service_dispatch_detail,
            movement_detail_card=cards,
        )
        if creation_result.is_failure:
            return creation_result

        return Success(
            DyeingServiceDispatchSchema.model_validate(dyeing_service_dispatch)
        )

    async def anulate_dyeing_service_dispatch(
        self,
        dyeing_service_dispatch_number: str,
        period: int,
    ) -> Result[DyeingServiceDispatchSchema, CustomException]:
        dyeing_service_dispatch_result = await self._read_dyeing_service_dispatch(
            dyeing_service_dispatch_number=dyeing_service_dispatch_number,
            period=period,
            include_detail=True,
            include_detail_card=True,
        )
        if dyeing_service_dispatch_result.is_failure:
            return dyeing_service_dispatch_result

        dyeing_service_dispatch: Movement = dyeing_service_dispatch_result.value

        validation_result = await self._validate_update_dyeing_service_dispatch(
            dyeing_service_dispatch=dyeing_service_dispatch,
        )
        if validation_result.is_failure:
            return validation_result

        dyeing_service_dispatch_detail_result = (
            await self._reads_dyeing_service_dispatch_detail(
                dyeing_service_dispatch_number=dyeing_service_dispatch_number,
                period=period,
            )
        )
        if dyeing_service_dispatch_detail_result.is_failure:
            return dyeing_service_dispatch_detail_result

        dyeing_service_dispatch_detail_card = (
            dyeing_service_dispatch_detail_result.value
        )

        rollback_result = await self.rollback_dyeing_service_dispatch(
            period=period,
            dyeing_service_dispatch=dyeing_service_dispatch,
        )
        if rollback_result.is_failure:
            return rollback_result

        dyeing_service_dispatch.status_flag = "A"

        for detail in dyeing_service_dispatch.detail_dyeing:
            detail.status_flag = "A"

        update_result = await self.save_movement(
            movement=dyeing_service_dispatch,
            movement_detail=dyeing_service_dispatch_detail_card,
            movement_detail_fabric=dyeing_service_dispatch.detail_dyeing,
            movement_detail_card=[
                detail_card
                for detail in dyeing_service_dispatch.detail_dyeing
                for detail_card in detail.detail_card
            ],
        )
        if update_result.is_failure:
            return update_result

        return Success(None)

    async def is_updated_permission(
        self,
        dyeing_service_dispatch_number: str,
        period: int,
    ) -> Result[None, CustomException]:
        dyeing_service_dispatch_result = await self._read_dyeing_service_dispatch(
            dyeing_service_dispatch_number=dyeing_service_dispatch_number,
            period=period,
            include_detail=True,
            include_detail_card=True,
        )
        if dyeing_service_dispatch_result.is_failure:
            return dyeing_service_dispatch_result

        dyeing_service_dispatch: Movement = dyeing_service_dispatch_result.value

        validation_result = await self._validate_update_dyeing_service_dispatch(
            dyeing_service_dispatch=dyeing_service_dispatch,
        )
        if validation_result.is_failure:
            return validation_result

        return Success(None)

    async def print_dyeing_service_dispatch(
        self,
    ) -> Result[None, CustomException]:
        pass

        pdf = generate_pdf()

        return Success(pdf)
