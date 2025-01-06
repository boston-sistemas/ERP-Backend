from sqlalchemy.ext.asyncio import AsyncSession

from src.core.constants import MECSA_COMPANY_CODE
from src.core.exceptions import CustomException
from src.core.repositories import SequenceRepository
from src.core.repository import BaseRepository
from src.core.result import Result, Success
from src.core.utils import PERU_TIMEZONE, calculate_time
from src.operations.constants import (
    YARN_PURCHASE_ENTRY_DOCUMENT_CODE,
    YARN_PURCHASE_ENTRY_MOVEMENT_CODE,
    YARN_PURCHASE_ENTRY_MOVEMENT_TYPE,
    YARN_PURCHASE_ENTRY_STORAGE_CODE,
)
from src.operations.failures import (
    YARN_PURCHASE_ENTRY_ALREADY_ACCOUNTED_FAILURE,
    YARN_PURCHASE_ENTRY_ALREADY_ANULLED_FAILURE,
    YARN_PURCHASE_ENTRY_ALREADY_QUANTITY_RECEIVED_FAILURE,
    YARN_PURCHASE_ENTRY_CONE_COUNT_MISMATCH_FAILURE,
    YARN_PURCHASE_ENTRY_HAS_MOVEMENT_FAILURE,
    YARN_PURCHASE_ENTRY_NOT_FOUND_FAILURE,
    YARN_PURCHASE_ENTRY_PACKAGE_COUNT_MISMATCH_FAILURE,
    YARN_PURCHASE_ENTRY_YARN_ALREADY_QUANTITY_RECEIVED_FAILURE,
    YARN_PURCHASE_ENTRY_YARN_NOT_FOUND_FAILURE,
)
from src.operations.models import (
    CurrencyExchange,
    Movement,
    MovementDetail,
    MovementDetailAux,
    MovementYarnOCHeavy,
)
from src.operations.repositories import (
    YarnPurchaseEntryRepository,
)
from src.operations.schemas import (
    OrdenCompraWithDetailSchema,
    YarnPurchaseEntriesSimpleListSchema,
    YarnPurchaseEntryCreateSchema,
    YarnPurchaseEntryDetailCreateSchema,
    YarnPurchaseEntryDetailUpdateSchema,
    YarnPurchaseEntrySchema,
    YarnPurchaseEntryUpdateSchema,
)
from src.operations.sequences import mecsa_batch_sq

from .movement_service import MovementService
from .orden_compra_service import OrdenCompraService
from .series_service import YarnPurchaseEntrySeries
from .supplier_service import SupplierService
from .yarn_purchase_entry_detail_heavy_service import (
    YarnPurchaseEntryDetailHeavyService,
)
from .yarn_service import YarnService


class YarnPurchaseEntryService(MovementService):
    def __init__(self, promec_db: AsyncSession, db: AsyncSession = None) -> None:
        super().__init__(promec_db=promec_db)
        self.promec_db = promec_db
        self.repository = YarnPurchaseEntryRepository(promec_db=promec_db)
        self.yarn_service = YarnService(promec_db=promec_db, db=db)
        self.purchase_order_service = OrdenCompraService(db=promec_db)
        self.mecsa_batch_sequence = SequenceRepository(
            sequence=mecsa_batch_sq, db=promec_db
        )
        self.yarn_purchase_entry_series = YarnPurchaseEntrySeries(promec_db=promec_db)
        self.currency_exchange_repository = BaseRepository(
            model=CurrencyExchange, db=promec_db
        )
        self.supplier_service = SupplierService(promec_db=promec_db)
        self.yarn_purchase_entry_detail_repository = BaseRepository(
            model=MovementDetail, db=promec_db
        )
        self.yarn_purchase_entry_detail_aux_repository = BaseRepository(
            model=MovementDetailAux, db=promec_db
        )
        self.yarn_purchase_entry_detail_heavy_repository = BaseRepository(
            model=MovementYarnOCHeavy, db=promec_db
        )
        self.yarn_purchase_entry_detail_heavy_service = (
            YarnPurchaseEntryDetailHeavyService(promec_db=promec_db)
        )

    async def _read_yarn_purchase_entry(
        self,
        yarn_purchase_entry_number: str,
        period: int,
        include_details: bool = False,
        include_purchase_order: bool = False,
        include_purchase_order_detail: bool = False,
    ) -> Result[Movement, CustomException]:
        yarn_purchase_entry = await self.repository.find_yarn_purchase_by_entry_number(
            purchase_entry_number=yarn_purchase_entry_number,
            period=period,
            include_details=include_details,
            include_purchase_order=include_purchase_order,
            include_purchase_order_detail=include_purchase_order_detail,
        )

        if yarn_purchase_entry is None:
            return YARN_PURCHASE_ENTRY_NOT_FOUND_FAILURE

        return Success(yarn_purchase_entry)

    async def read_yarn_purchase_entry(
        self,
        yarn_purchase_entry_number: str,
        period: int,
        include_details: bool = False,
    ) -> Result[YarnPurchaseEntrySchema, CustomException]:
        yarn_purchase_entry_result = await self._read_yarn_purchase_entry(
            yarn_purchase_entry_number=yarn_purchase_entry_number,
            period=period,
            include_details=include_details,
        )

        if yarn_purchase_entry_result.is_failure:
            return yarn_purchase_entry_result

        return Success(
            YarnPurchaseEntrySchema.model_validate(yarn_purchase_entry_result.value)
        )

    async def read_yarn_purchase_entries(
        self,
        period: int,
        limit: int = None,
        offset: int = None,
        include_inactive: bool = False,
    ) -> Result[YarnPurchaseEntriesSimpleListSchema, CustomException]:
        yarn_purchase_entries = await self.repository.find_yarn_purchase_entries(
            limit=limit,
            offset=offset,
            period=period,
            include_inactive=include_inactive,
        )

        return Success(
            YarnPurchaseEntriesSimpleListSchema(
                yarn_purchase_entries=yarn_purchase_entries
            )
        )

    async def _validate_yarn_purchase_entry_data(
        self,
        data: YarnPurchaseEntryCreateSchema,
    ) -> Result[None, CustomException]:
        yarn_order = await self.purchase_order_service.read_purchase_yarn_order(
            purchase_order_number=data.purchase_order_number,
            period=data.period,
            include_detalle=True,
        )

        if yarn_order.is_failure:
            return yarn_order

        if yarn_order.value.status_flag == "C":
            return YARN_PURCHASE_ENTRY_ALREADY_QUANTITY_RECEIVED_FAILURE

        return yarn_order

    async def _validate_yarn_purchase_entry_detalle_data(
        self,
        data: list[YarnPurchaseEntryDetailCreateSchema],
        purchase_yarn_order: OrdenCompraWithDetailSchema,
    ) -> Result[None, CustomException]:
        detalle_yarn_ids = {
            detail.yarn.id: detail.status_flag for detail in purchase_yarn_order.detail
        }

        for detail in data:
            if detail.yarn_id not in detalle_yarn_ids.keys():
                return YARN_PURCHASE_ENTRY_YARN_NOT_FOUND_FAILURE

            if detalle_yarn_ids[detail.yarn_id] == "C":
                return YARN_PURCHASE_ENTRY_YARN_ALREADY_QUANTITY_RECEIVED_FAILURE

            if detail.detail_heavy:
                cone_count_total = sum(
                    [cone.cone_count for cone in detail.detail_heavy]
                )
                if detail.guide_cone_count < cone_count_total:
                    return YARN_PURCHASE_ENTRY_CONE_COUNT_MISMATCH_FAILURE

                package_count_total = sum(
                    [cone.package_count for cone in detail.detail_heavy]
                )
                if detail.guide_package_count < package_count_total:
                    return YARN_PURCHASE_ENTRY_PACKAGE_COUNT_MISMATCH_FAILURE

        return Success(None)

    async def create_yarn_purchase_entry(
        self,
        form: YarnPurchaseEntryCreateSchema,
    ) -> Result[None, CustomException]:
        validation_result = await self._validate_yarn_purchase_entry_data(data=form)

        if validation_result.is_failure:
            return validation_result

        purchase_yarn_order = validation_result.value

        validation_result = await self._validate_yarn_purchase_entry_detalle_data(
            data=form.detail, purchase_yarn_order=validation_result.value
        )

        if validation_result.is_failure:
            return validation_result

        mecsa_batch_sq = str(await self.mecsa_batch_sequence.next_value())

        entry_number = await self.yarn_purchase_entry_series.next_number()

        currency_code_value = purchase_yarn_order.currency_code
        current_time = calculate_time(tz=PERU_TIMEZONE)

        currency_exchange = await self.currency_exchange_repository.find_all(
            filter=(CurrencyExchange.exchange_date <= current_time.date()),
            limit=1,
            order_by=[CurrencyExchange.exchange_date.desc()],
        )

        supplier = await self.supplier_service.read_supplier(
            purchase_yarn_order.supplier_code
        )

        if supplier.is_failure:
            return supplier

        supplier = supplier.value

        period = form.period
        creation_date = current_time.date()
        creation_time = current_time.strftime("%H:%M:%S")

        exchange_rate_value = currency_exchange[0].sell_rate

        yarn_purchase_entry = Movement(
            company_code=MECSA_COMPANY_CODE,
            storage_code=YARN_PURCHASE_ENTRY_STORAGE_CODE,
            movement_type=YARN_PURCHASE_ENTRY_MOVEMENT_TYPE,
            movement_code=YARN_PURCHASE_ENTRY_MOVEMENT_CODE,
            document_code=YARN_PURCHASE_ENTRY_DOCUMENT_CODE,
            document_number=entry_number,
            period=period,
            creation_date=creation_date,
            creation_time=creation_time,
            currency_code=currency_code_value,
            exchange_rate=exchange_rate_value,
            document_note=form.document_note,
            clfaux="_PRO",
            auxiliary_code=purchase_yarn_order.supplier_code,
            status_flag="P",
            user_id="DESA01",
            auxiliary_name=supplier.name,
            reference_document="O/C",
            reference_number2=form.purchase_order_number,
            nrogf=form.supplier_po_correlative,
            sergf=form.supplier_po_series,
            fecgf=form.fecgf,
            origmov="A",
            serial_number="006",
            printed_flag="N",
            flgact="N",
            flgtras=False,
            flgreclamo="N",
            flgsit="A",
            servadi="N",
            tarfservadi=0,
            origin_station="SERVIDORDESA",
            undpesobrutototal="KGM",
            transaction_mode="02",
            intentosenvele=0,
            supplier_batch=form.supplier_batch,
            mecsa_batch=mecsa_batch_sq,
        )
        # print(yarn_purchase_entry)

        # for detail in form.detail:
        #     print(detail.item_number, detail.guide_cone_count)

        yarn_purchase_entry_detail = []
        yarn_purchase_entry_detail_aux = []
        yarn_purchase_entry_detail_heavy = []

        precto = {
            detail.yarn_id: detail.precto for detail in purchase_yarn_order.detail
        }

        # print(precto)
        #
        for detail in form.detail:
            if detail.mecsa_weight != 0:
                precto_value = precto[detail.yarn_id] * (
                    detail.guide_net_weight / detail.mecsa_weight
                )
            else:
                precto_value = 0

            impcto_value = precto[detail.yarn_id] * detail.guide_net_weight

            impmn2_value = detail.guide_net_weight * precto[detail.yarn_id]
            impmn1_value = impmn2_value * exchange_rate_value

            product_inventory = await self._read_or_create_product_inventory(
                product_code=detail.yarn_id,
                period=period,
                storage_code=YARN_PURCHASE_ENTRY_STORAGE_CODE,
                enable_create=True,
            )

            if product_inventory.is_failure:
                return product_inventory

            product_inventory = product_inventory.value

            stkact_value = product_inventory.current_stock + detail.mecsa_weight

            products_inventory = (
                await self.product_inventory_service._read_products_inventory(
                    product_code=detail.yarn_id,
                    period=period,
                )
            ).value

            stkgen_value = sum(product.current_stock for product in products_inventory)

            yarn_purchase_entry_detail_value = MovementDetail(
                company_code=MECSA_COMPANY_CODE,
                storage_code=YARN_PURCHASE_ENTRY_STORAGE_CODE,
                movement_type=YARN_PURCHASE_ENTRY_MOVEMENT_TYPE,
                movement_code=YARN_PURCHASE_ENTRY_MOVEMENT_CODE,
                document_code=YARN_PURCHASE_ENTRY_DOCUMENT_CODE,
                document_number=entry_number,
                item_number=detail.item_number,
                period=period,
                creation_date=creation_date,
                creation_time=creation_time,
                product_code=detail.yarn_id,
                unit_code="KG",
                factor=1,
                mecsa_weight=detail.mecsa_weight,
                guide_gross_weight=detail.guide_gross_weight,
                precto=precto_value,
                impcto=impcto_value,
                currency_code=currency_code_value,
                exchange_rate=exchange_rate_value,
                impmn1=impmn1_value,
                impmn2=impmn2_value,
                stkgen=stkgen_value,
                stkalm=stkact_value,
                # ctomn1=lo di todo,
                # ctomn2=pero no supe calcularte,
                status_flag="P",
                is_weighted=detail.is_weighted,
                supplier_batch=form.supplier_batch,
            )

            yarn_purchase_entry_detail_aux_value = MovementDetailAux(
                company_code=MECSA_COMPANY_CODE,
                document_code=YARN_PURCHASE_ENTRY_DOCUMENT_CODE,
                document_number=entry_number,
                item_number=detail.item_number,
                period=period,
                product_code=detail.yarn_id,
                unit_code="KG",
                factor=1,
                precto=precto_value,
                impcto=impcto_value,
                creation_date=creation_date,
                guide_net_weight=detail.guide_net_weight,
                mecsa_weight=detail.mecsa_weight,
                guide_cone_count=detail.guide_cone_count,
                guide_package_count=detail.guide_package_count,
                reference_code="006",
                mecsa_batch=mecsa_batch_sq,
                supplier_batch=form.supplier_batch[:14],
            )

            for heavy in detail.detail_heavy:
                yarn_purchase_entry_detail_heavy.append(
                    MovementYarnOCHeavy(
                        company_code=MECSA_COMPANY_CODE,
                        yarn_id=detail.yarn_id,
                        group_number=heavy.group_number,
                        ingress_number=entry_number,
                        item_number=detail.item_number,
                        status_flag="P",
                        entry_user_id="DESA01",
                        cone_count=heavy.cone_count,
                        package_count=heavy.package_count,
                        destination_storage="006",
                        net_weight=heavy.net_weight,
                        gross_weight=heavy.gross_weight,
                        dispatch_status=False,
                        packages_left=heavy.package_count,
                        cones_left=heavy.cone_count,
                        supplier_yarn_id=supplier.code,
                        supplier_batch=form.supplier_batch,
                    )
                )

            yarn_purchase_entry_detail_value.detail_heavy = (
                yarn_purchase_entry_detail_heavy
            )
            yarn_purchase_entry_detail_value.detail_aux = (
                yarn_purchase_entry_detail_aux_value
            )

            yarn_purchase_entry_detail.append(yarn_purchase_entry_detail_value)
            yarn_purchase_entry_detail_aux.append(yarn_purchase_entry_detail_aux_value)
            await self.product_inventory_service.update_current_stock(
                product_code=detail.yarn_id,
                period=period,
                storage_code=YARN_PURCHASE_ENTRY_STORAGE_CODE,
                new_stock=detail.mecsa_weight,
            )
            await self.purchase_order_service.update_quantity_supplied_by_product_code(
                purchase_order_number=form.purchase_order_number,
                product_code=detail.yarn_id,
                period=period,
                quantity_supplied=detail.mecsa_weight,
            )

        yarn_purchase_entry.detail = yarn_purchase_entry_detail

        await self.repository.save(yarn_purchase_entry)
        await self.yarn_purchase_entry_detail_repository.save_all(
            yarn_purchase_entry_detail
        )
        await self.yarn_purchase_entry_detail_aux_repository.save_all(
            yarn_purchase_entry_detail_aux
        )
        await self.yarn_purchase_entry_detail_heavy_repository.save_all(
            yarn_purchase_entry_detail_heavy
        )

        return Success(YarnPurchaseEntrySchema.model_validate(yarn_purchase_entry))

    async def _delete_detail(
        self,
        yarn_purchase_entry_detail: MovementDetail,
    ) -> None:
        await self.product_inventory_service.rollback_currents_stock(
            product_code=yarn_purchase_entry_detail.product_code,
            period=yarn_purchase_entry_detail.period,
            storage_code=YARN_PURCHASE_ENTRY_STORAGE_CODE,
            quantity=yarn_purchase_entry_detail.mecsa_weight,
        )

        await self.purchase_order_service.rollback_quantity_supplied_by_product_code(
            purchase_order_number=yarn_purchase_entry_detail.document_number,
            period=yarn_purchase_entry_detail.period,
            product_code=yarn_purchase_entry_detail.product_code,
            quantity_supplied=yarn_purchase_entry_detail.mecsa_weight,
        )

        await self.yarn_purchase_entry_detail_heavy_repository.delete_all(
            yarn_purchase_entry_detail.detail_heavy
        )
        await self.yarn_purchase_entry_detail_aux_repository.delete(
            yarn_purchase_entry_detail.detail_aux
        )
        await self.yarn_purchase_entry_detail_repository.delete(
            yarn_purchase_entry_detail
        )

    async def _delete_detail_heavy(
        self,
        yarn_purchase_entry_detail_heavy: MovementYarnOCHeavy,
    ) -> None:
        await self.yarn_purchase_entry_detail_heavy_repository.delete(
            yarn_purchase_entry_detail_heavy
        )

    async def _delete_yarn_purchase_entry_detail(
        self,
        yarn_purchase_entry_detail: list[MovementDetail],
        form: YarnPurchaseEntryUpdateSchema,
    ) -> list[MovementDetail]:
        item_numbers = [detail.item_number for detail in form.detail]
        for detail in yarn_purchase_entry_detail:
            if detail.item_number not in item_numbers:
                await self._delete_detail(yarn_purchase_entry_detail=detail)
                yarn_purchase_entry_detail.remove(detail)

        return yarn_purchase_entry_detail

    async def _delete_yarn_purchase_entry_detail_heavy(
        self,
        yarn_purchase_entry_detail_heavy: list[MovementYarnOCHeavy],
        form: YarnPurchaseEntryDetailUpdateSchema,
    ) -> list[MovementYarnOCHeavy]:
        group_numbers = [str(heavy.group_number) for heavy in form.detail_heavy]
        print(group_numbers)
        yarn_purchase_entry_detail_heavy_result = []
        for heavy in yarn_purchase_entry_detail_heavy:
            if heavy.group_number not in group_numbers:
                await self._delete_detail_heavy(yarn_purchase_entry_detail_heavy=heavy)
            else:
                yarn_purchase_entry_detail_heavy_result.append(heavy)

        return yarn_purchase_entry_detail_heavy_result

    async def _find_yarn_purchase_entry_detail(
        self,
        yarn_purchase_entry_detail: list[MovementDetail],
        item_number: int,
    ) -> MovementDetail | None:
        for detail in yarn_purchase_entry_detail:
            if detail.item_number == item_number:
                return detail
        return None

    async def _find_yarn_purchase_entry_detail_aux(
        self,
        yarn_purchase_entry_detail_aux: list[MovementDetail],
        item_number: int,
    ) -> MovementDetailAux | None:
        for detail in yarn_purchase_entry_detail_aux:
            if detail.detail_aux.item_number == item_number:
                return detail.detail_aux
        return None

    async def _find_yarn_purchase_entry_detail_heavy(
        self,
        yarn_purchase_entry_detail_heavy: list[MovementYarnOCHeavy],
        group_number: int,
    ) -> MovementYarnOCHeavy | None:
        for heavy in yarn_purchase_entry_detail_heavy:
            if heavy.group_number == str(group_number):
                return heavy
        return None

    async def _validate_update_yarn_purchase_entry(
        self,
        yarn_purchase_entry: Movement,
    ) -> Result[None, CustomException]:
        if yarn_purchase_entry.status_flag == "A":
            return YARN_PURCHASE_ENTRY_ALREADY_ANULLED_FAILURE

        if yarn_purchase_entry.flgcbd == "S":
            return YARN_PURCHASE_ENTRY_ALREADY_ACCOUNTED_FAILURE

        for detail in yarn_purchase_entry.detail:
            for heavy in detail.detail_heavy:
                print(heavy.exit_number)
                if heavy.exit_number != "":
                    return YARN_PURCHASE_ENTRY_HAS_MOVEMENT_FAILURE

        return Success(None)

    async def update_yarn_purchase_entry(
        self,
        yarn_purchase_entry_number: str,
        period: int,
        form: YarnPurchaseEntryUpdateSchema,
    ) -> Result[None, CustomException]:
        yarn_purchase_entry_result = await self._read_yarn_purchase_entry(
            yarn_purchase_entry_number=yarn_purchase_entry_number,
            period=period,
            include_details=True,
            include_purchase_order=True,
            include_purchase_order_detail=True,
        )

        if yarn_purchase_entry_result.is_failure:
            return yarn_purchase_entry_result

        yarn_purchase_entry: Movement = yarn_purchase_entry_result.value

        validation_result = await self._validate_update_yarn_purchase_entry(
            yarn_purchase_entry=yarn_purchase_entry
        )

        if validation_result.is_failure:
            return validation_result

        purchase_yarn_order = yarn_purchase_entry.purchase_order

        validation_result = await self._validate_yarn_purchase_entry_detalle_data(
            data=form.detail,
            purchase_yarn_order=purchase_yarn_order,
        )

        if validation_result.is_failure:
            return validation_result

        yarn_purchase_entry.supplier_po_correlative = form.supplier_po_correlative
        yarn_purchase_entry.supplier_po_series = form.supplier_po_series
        yarn_purchase_entry.fecgf = form.fecgf
        yarn_purchase_entry.document_note = form.document_note
        yarn_purchase_entry.supplier_batch = form.supplier_batch

        yarn_purchase_entry.detail = await self._delete_yarn_purchase_entry_detail(
            yarn_purchase_entry_detail=yarn_purchase_entry.detail,
            form=form,
        )

        precto = {
            detail.product_code: detail.precto for detail in purchase_yarn_order.detail
        }

        for detail in form.detail:
            yarn_purchase_entry_detail_result = (
                await self._find_yarn_purchase_entry_detail(
                    yarn_purchase_entry_detail=yarn_purchase_entry.detail,
                    item_number=detail.item_number,
                )
            )

            yarn_purchase_entry_detail_aux_result = (
                await self._find_yarn_purchase_entry_detail_aux(
                    yarn_purchase_entry_detail_aux=yarn_purchase_entry.detail,
                    item_number=detail.item_number,
                )
            )

            if yarn_purchase_entry_detail_result is not None:
                yarn_purchase_entry.detail.detail_heavy = await self._delete_yarn_purchase_entry_detail_heavy(
                    yarn_purchase_entry_detail_heavy=yarn_purchase_entry_detail_result.detail_heavy,
                    form=detail,
                )
                for heavy in detail.detail_heavy:
                    yarn_purchase_entry_detail_heavy_result = await self._find_yarn_purchase_entry_detail_heavy(
                        yarn_purchase_entry_detail_heavy=yarn_purchase_entry_detail_result.detail_heavy,
                        group_number=heavy.group_number,
                    )

                    if yarn_purchase_entry_detail_heavy_result is not None:
                        yarn_purchase_entry_detail_heavy_result.cone_count = (
                            heavy.cone_count
                        )
                        yarn_purchase_entry_detail_heavy_result.package_count = (
                            heavy.package_count
                        )
                        yarn_purchase_entry_detail_heavy_result.net_weight = (
                            heavy.net_weight
                        )
                        yarn_purchase_entry_detail_heavy_result.gross_weight = (
                            heavy.gross_weight
                        )
                    else:
                        yarn_purchase_entry_detail_heavy_result = MovementYarnOCHeavy(
                            company_code=MECSA_COMPANY_CODE,
                            yarn_id=detail.yarn_id,
                            group_number=str(heavy.group_number),
                            ingress_number=yarn_purchase_entry_number,
                            item_number=detail.item_number,
                            status_flag="P",
                            entry_user_id="DESA01",
                            cone_count=heavy.cone_count,
                            package_count=heavy.package_count,
                            destination_storage="006",
                            net_weight=heavy.net_weight,
                            gross_weight=heavy.gross_weight,
                            dispatch_status=False,
                            packages_left=heavy.package_count,
                            cones_left=heavy.cone_count,
                            supplier_yarn_id=purchase_yarn_order.supplier_code,
                        )
                        await self.yarn_purchase_entry_detail_heavy_repository.save(
                            yarn_purchase_entry_detail_heavy_result
                        )

                if (
                    detail.mecsa_weight
                    != yarn_purchase_entry_detail_result.mecsa_weight
                    or detail.guide_net_weight
                    != yarn_purchase_entry_detail_aux_result.guide_net_weight
                ):
                    await self.product_inventory_service.rollback_currents_stock(
                        product_code=yarn_purchase_entry_detail_result.product_code,
                        period=period,
                        storage_code=YARN_PURCHASE_ENTRY_STORAGE_CODE,
                        quantity=yarn_purchase_entry_detail_result.mecsa_weight,
                    )

                    await self.purchase_order_service.rollback_quantity_supplied_by_product_code(
                        purchase_order_number=purchase_yarn_order.purchase_order_number,
                        period=period,
                        product_code=yarn_purchase_entry_detail_result.product_code,
                        quantity_supplied=yarn_purchase_entry_detail_result.mecsa_weight,
                    )

                    yarn_purchase_entry_detail_result.mecsa_weight = detail.mecsa_weight
                    yarn_purchase_entry_detail_result.guide_gross_weight = (
                        detail.guide_gross_weight
                    )
                    if detail.mecsa_weight != 0:
                        yarn_purchase_entry_detail_result.precto = precto[
                            detail.yarn_id
                        ] * (detail.guide_net_weight / detail.mecsa_weight)
                    else:
                        yarn_purchase_entry_detail_result.precto = 0
                    yarn_purchase_entry_detail_result.impcto = (
                        precto[detail.yarn_id] * detail.guide_net_weight
                    )
                    yarn_purchase_entry_detail_result.impmn2 = (
                        detail.guide_net_weight * precto[detail.yarn_id]
                    )
                    yarn_purchase_entry_detail_result.impmn1 = (
                        yarn_purchase_entry_detail_result.impmn2
                        * yarn_purchase_entry.exchange_rate
                    )
                    yarn_purchase_entry_detail_result.stkalm = (
                        yarn_purchase_entry_detail_result.stkalm + detail.mecsa_weight
                    )
                    yarn_purchase_entry_detail_result.is_weighted = detail.is_weighted

                    product_inventory = await self._read_or_create_product_inventory(
                        product_code=detail.yarn_id,
                        period=period,
                        storage_code=YARN_PURCHASE_ENTRY_STORAGE_CODE,
                        enable_create=True,
                    )

                    if product_inventory.is_failure:
                        return product_inventory

                    product_inventory = product_inventory.value

                    products_inventory = (
                        await self.product_inventory_service._read_products_inventory(
                            product_code=detail.yarn_id,
                            period=period,
                        )
                    ).value

                    yarn_purchase_entry_detail_result.stkgen = sum(
                        product.current_stock for product in products_inventory
                    )

                    yarn_purchase_entry_detail_aux_result.guide_net_weight = (
                        detail.guide_net_weight
                    )
                    yarn_purchase_entry_detail_aux_result.mecsa_weight = (
                        detail.mecsa_weight
                    )
                    yarn_purchase_entry_detail_aux_result.guide_cone_count = (
                        detail.guide_cone_count
                    )
                    yarn_purchase_entry_detail_aux_result.guide_package_count = (
                        detail.guide_package_count
                    )
                    yarn_purchase_entry_detail_aux_result.supplier_batch = (
                        form.supplier_batch
                    )

                    await self.product_inventory_service.update_current_stock(
                        product_code=detail.yarn_id,
                        period=period,
                        storage_code=YARN_PURCHASE_ENTRY_STORAGE_CODE,
                        new_stock=yarn_purchase_entry_detail_result.stkalm,
                    )

                    await self.purchase_order_service.update_quantity_supplied_by_product_code(
                        purchase_order_number=purchase_yarn_order.purchase_order_number,
                        product_code=detail.yarn_id,
                        period=period,
                        quantity_supplied=detail.mecsa_weight,
                    )
            else:
                if detail.mecsa_weight != 0:
                    precto_value = precto[detail.yarn_id] * (
                        detail.guide_net_weight / detail.mecsa_weight
                    )
                else:
                    precto_value = 0

                impcto_value = precto[detail.yarn_id] * detail.guide_net_weight

                impmn2_value = detail.guide_net_weight * precto[detail.yarn_id]

                impmn1_value = impmn2_value * yarn_purchase_entry.exchange_rate

                product_inventory = await self._read_or_create_product_inventory(
                    product_code=detail.yarn_id,
                    period=period,
                    storage_code=YARN_PURCHASE_ENTRY_STORAGE_CODE,
                    enable_create=True,
                )

                if product_inventory.is_failure:
                    return product_inventory

                product_inventory = product_inventory.value

                stkact_value = product_inventory.current_stock + detail.mecsa_weight

                products_inventory = (
                    await self.product_inventory_service._read_products_inventory(
                        product_code=detail.yarn_id,
                        period=period,
                    )
                ).value

                stkgen_value = sum(
                    product.current_stock for product in products_inventory
                )

                yarn_purchase_entry_detail_result = MovementDetail(
                    company_code=MECSA_COMPANY_CODE,
                    storage_code=YARN_PURCHASE_ENTRY_STORAGE_CODE,
                    movement_type=YARN_PURCHASE_ENTRY_MOVEMENT_TYPE,
                    movement_code=YARN_PURCHASE_ENTRY_MOVEMENT_CODE,
                    document_code=YARN_PURCHASE_ENTRY_DOCUMENT_CODE,
                    document_number=yarn_purchase_entry_number,
                    item_number=detail.item_number,
                    period=period,
                    creation_date=yarn_purchase_entry.creation_date,
                    creation_time=yarn_purchase_entry.creation_time,
                    product_code=detail.yarn_id,
                    unit_code="KG",
                    factor=1,
                    mecsa_weight=detail.mecsa_weight,
                    guide_gross_weight=detail.guide_gross_weight,
                    precto=precto_value,
                    impcto=impcto_value,
                    currency_code=yarn_purchase_entry.currency_code,
                    exchange_rate=yarn_purchase_entry.exchange_rate,
                    impmn1=impmn1_value,
                    impmn2=impmn2_value,
                    stkgen=stkgen_value,
                    stkalm=stkact_value,
                    status_flag="P",
                    is_weighted=detail.is_weighted,
                )

                yarn_purchase_entry_detail_aux_result = MovementDetailAux(
                    company_code=MECSA_COMPANY_CODE,
                    document_code=YARN_PURCHASE_ENTRY_DOCUMENT_CODE,
                    document_number=yarn_purchase_entry_number,
                    item_number=detail.item_number,
                    period=period,
                    product_code=detail.yarn_id,
                    unit_code="KG",
                    factor=1,
                    precto=precto_value,
                    impcto=impcto_value,
                    creation_date=yarn_purchase_entry.creation_date,
                    guide_net_weight=detail.guide_net_weight,
                    mecsa_weight=detail.mecsa_weight,
                    guide_cone_count=detail.guide_cone_count,
                    guide_package_count=detail.guide_package_count,
                    reference_code="006",
                    mecsa_batch=yarn_purchase_entry.mecsa_batch,
                    supplier_batch=form.supplier_batch[:14],
                )

                yarn_purchase_entry.detail.append(yarn_purchase_entry_detail_result)
                yarn_purchase_entry_detail_result.detail_aux = (
                    yarn_purchase_entry_detail_aux_result
                )

            await self.yarn_purchase_entry_detail_repository.save(
                yarn_purchase_entry_detail_result
            )
            await self.yarn_purchase_entry_detail_aux_repository.save(
                yarn_purchase_entry_detail_aux_result
            )

        await self.repository.save(yarn_purchase_entry)

        return Success(None)

    async def anulate_yarn_purchase_entry(
        self,
        yarn_purchase_entry_number: str,
        period: int,
    ) -> Result[None, CustomException]:
        yarn_purchase_entry_result = await self._read_yarn_purchase_entry(
            yarn_purchase_entry_number=yarn_purchase_entry_number,
            period=period,
            include_details=True,
        )

        if yarn_purchase_entry_result.is_failure:
            return yarn_purchase_entry_result

        yarn_purchase_entry: Movement = yarn_purchase_entry_result.value

        validation_result = await self._validate_update_yarn_purchase_entry(
            yarn_purchase_entry=yarn_purchase_entry
        )

        if validation_result.is_failure:
            return validation_result

        for detail in yarn_purchase_entry.detail:
            await self.product_inventory_service.rollback_currents_stock(
                product_code=detail.product_code,
                period=period,
                storage_code=YARN_PURCHASE_ENTRY_STORAGE_CODE,
                quantity=detail.mecsa_weight,
            )

            await (
                self.purchase_order_service.rollback_quantity_supplied_by_product_code(
                    purchase_order_number=yarn_purchase_entry.reference_number2,
                    period=period,
                    product_code=detail.product_code,
                    quantity_supplied=detail.mecsa_weight,
                )
            )

            detail.status_flag = "A"

            for heavy in detail.detail_heavy:
                heavy.status_flag = "A"
                heavy.ingress_number = heavy.ingress_number
                await self.yarn_purchase_entry_detail_heavy_repository.save(heavy)

        yarn_purchase_entry.status_flag = "A"

        await self.repository.save(yarn_purchase_entry)
        await self.repository.save_all(yarn_purchase_entry.detail)
        return Success(None)

    async def is_updated_permission(
        self,
        yarn_purchase_entry_number: str,
        period: int,
    ) -> Result[None, CustomException]:
        yarn_purchase_entry_result = await self._read_yarn_purchase_entry(
            yarn_purchase_entry_number=yarn_purchase_entry_number,
            period=period,
            include_details=True,
        )

        if yarn_purchase_entry_result.is_failure:
            return yarn_purchase_entry_result

        yarn_purchase_entry: Movement = yarn_purchase_entry_result.value

        validation_result = await self._validate_update_yarn_purchase_entry(
            yarn_purchase_entry=yarn_purchase_entry
        )

        if validation_result.is_failure:
            return validation_result

        return Success(None)

    async def read_yarn_purchase_entry_item_group_availability(
        self,
        period: int,
    ) -> Result[None, CustomException]:
        yarn_purchase_entries_item_group_availability = await self.yarn_purchase_entry_detail_heavy_service.find_yarn_purchase_entries_item_group_availability(
            period=period,
        )

        if yarn_purchase_entries_item_group_availability.is_failure:
            return yarn_purchase_entries_item_group_availability

        return Success(yarn_purchase_entries_item_group_availability.value)
