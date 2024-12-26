from sqlalchemy.ext.asyncio import AsyncSession

from src.core.constants import MECSA_COMPANY_CODE
from src.core.exceptions import CustomException
from src.core.repositories import SequenceRepository
from src.core.repository import BaseRepository
from src.core.result import Result, Success
from src.core.utils import PERU_TIMEZONE, calculate_time
from src.operations.constants import (
    YARN_WEAVING_DISPATCH_STORAGE_CODE,
    YARN_WEAVING_DISPATCH_MOVEMENT_CODE,
    YARN_WEAVING_DISPATCH_MOVEMENT_TYPE,
    YARN_WEAVING_DISPATCH_DOCUMENT_CODE,
    SERVICE_CODE_SUPPLIER_WEAVING,
    ENTRY_MOVEMENT_TYPE,
    ENTRY_DOCUMENT_CODE,
    WEAVING_MOVEMENT_CODE,
)

from datetime import datetime

from src.operations.models import (
    Movement,
    MovementDetail,
    MovementDetailAux,
)
from src.operations.repositories import (
    YarnWeavingDispatchRepository,
)
from src.operations.schemas import (
    YarnWeavingDispatchSimpleListSchema,
    YarnWeavingDispatchSchema,
    YarnWeavingDispatchCreateSchema,
    YarnWeavingDispatchDetailCreateSchema,
    SupplierSchema
)

from .movement_service import MovementService

from .series_service import (
    YarnWeavingDispatchSeries,
    EntrySeries,
)

from src.core.repository import BaseRepository
from .supplier_service import SupplierService

from .yarn_purchase_entry_detail_heavy_service import YarnPurchaseEntryDetailHeavyService

from src.operations.failures import (
    YARN_WEAVING_DISPATCH_NOT_FOUND_FAILURE,
    YARN_WEAVING_DISPATCH_SUPPLIER_WITHOUT_STORAGE_FAILURE,
    YARN_WEAVING_DISPATCH_SUPPLIER_NOT_ASSOCIATED_FAILURE,
    YARN_WEAVING_DISPATCH_PACKAGE_COUNT_MISMATCH_FAILURE,
    YARN_WEAVING_DISPATCH_CONE_COUNT_MISMATCH_FAILURE,
    YARN_WEAVING_DISPATCH_GROUP_ALREADY_DISPATCHED_FAILURE,
    YARN_WEAVING_DISPATCH_GROUP_ANULLED_FAILURE,
)

class YarnWeavingDispatchService(MovementService):
    def __init__(self, promec_db: AsyncSession) -> None:
        super().__init__(promec_db)
        self.repository = YarnWeavingDispatchRepository(promec_db)
        self.yarn_purchase_entry_detail_heavy_service = YarnPurchaseEntryDetailHeavyService(
            promec_db=promec_db
        )
        self.supplier_service = SupplierService(promec_db=promec_db)
        self.yarn_weaving_dispatch_series = YarnWeavingDispatchSeries(promec_db=promec_db)
        self.entry_series = EntrySeries(promec_db=promec_db)
        self.yarn_entry_repository = BaseRepository(
            model=Movement, db=promec_db
        )
        self.yarn_entry_detail_repository = BaseRepository(
            model=MovementDetail, db=promec_db
        )

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
        yarn_weaving_dispatch = await self.repository.find_yarn_weaving_dispatch_by_dispatch_number(
            dispatch_number=yarn_weaving_dispatch_number,
            period=period,
            include_detail=include_detail,
            include_detail_entry=include_detail_entry,
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
    ) -> Result[None, CustomException]:
        supplier = await self.supplier_service.read_supplier(
            supplier_code=data.supplier_code,
            include_service=True,
        )

        if supplier.is_failure:
            return supplier

        if supplier.value.storage_code == "":
            return YARN_WEAVING_DISPATCH_SUPPLIER_WITHOUT_STORAGE_FAILURE

        services = [service.service_code for service in supplier.value.services]
        if SERVICE_CODE_SUPPLIER_WEAVING not in services:
            return YARN_WEAVING_DISPATCH_SUPPLIER_NOT_ASSOCIATED_FAILURE
        return supplier

    async def _validate_yarn_weaving_dispatch_detail_data(
        self,
        data: list[YarnWeavingDispatchDetailCreateSchema],
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

            yarn_purchase_entry_detail_heavy = yarn_purchase_entry_detail_heavy_result.value

            detail._yarn_purchase_entry_heavy = yarn_purchase_entry_detail_heavy

            if yarn_purchase_entry_detail_heavy.status_flag == "A":
                return YARN_WEAVING_DISPATCH_GROUP_ANULLED_FAILURE

            if yarn_purchase_entry_detail_heavy.dispatch_status:
                return YARN_WEAVING_DISPATCH_GROUP_ALREADY_DISPATCHED_FAILURE

            validate_package = yarn_purchase_entry_detail_heavy.packages_left - detail.package_count
            validate_cones = yarn_purchase_entry_detail_heavy.cones_left - detail.cone_count

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
            serial_number='001',
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
                )
            )

        # await self.yarn_entry_repository.save(entry_movement)
        # await self.yarn_entry_detail_repository.save_all(entry_detail)

        return Success(entry_number)

    async def create_yarn_weaving_dispatch(
        self,
        form: YarnWeavingDispatchCreateSchema,
    ) -> Result[None, CustomException]:
        validation_result = await self._validate_yarn_weaving_dispatch_data(data=form)

        if validation_result.is_failure:
            return validation_result

        supplier = validation_result.value

        validation_result = await self._validate_yarn_weaving_dispatch_detail_data(
            data=form.detail
        )

        if validation_result.is_failure:
            return validation_result

        form.detail = validation_result.value

        dispatch_number = await self.yarn_weaving_dispatch_series.next_number()

        current_time = calculate_time(tz=PERU_TIMEZONE)

        creation_date = current_time.date()
        creation_time = current_time.strftime("%H:%M:%S")

        sequence_numbers = {
            service.service_code: service.sequence_number for service in supplier.services
        }

        purchase_service_number = supplier.initials + str(
            sequence_numbers[SERVICE_CODE_SUPPLIER_WEAVING]
        )

        print(purchase_service_number)

        creation_result = await self._create_yarn_entry_with_dispatch(
            storage_code=supplier.storage_code,
            period=form.period,
            dispatch_number=dispatch_number,
            current_time=current_time,
            supplier=supplier,
            purchase_service_number=purchase_service_number,
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
            # reference_document="P/I",
            reference_number1=entry_number,
            status_flag="P",
            user_id="DESA01",
            auxiliary_name=supplier.name,
            reference_document="O/S",
            reference_number2=purchase_service_number,
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

        for detail in form.detail:
            yarn_weaving_dispatch_detail.append(
                MovementDetail(
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
                    nroreq=purchase_service_number,
                    status_flag="P",
                )
            )

            yarn_weaving_dispatch_detail_aux.append(
                MovementDetailAux(
                    company_code=MECSA_COMPANY_CODE,
                    document_code=YARN_WEAVING_DISPATCH_DOCUMENT_CODE,
                    document_number=dispatch_number,
                    item_number=detail.item_number,
                    period=form.period,
                    product_code=detail._yarn_purchase_entry_heavy.yarn_id,
                    unit_code="KG",
                    factor=1,
                    mecsa_weight=detail.net_weight,
                    reference_code="P/I",

                )
            )

        return Success(None)
