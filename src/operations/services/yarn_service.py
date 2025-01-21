from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.constants import MECSA_COMPANY_CODE
from src.core.exceptions import CustomException
from src.core.repositories import SequenceRepository
from src.core.repository import BaseRepository
from src.core.result import Result, Success
from src.core.schemas import ItemIsUpdatableSchema
from src.core.utils import is_active_status, map_active_status
from src.operations.constants import SUPPLY_FAMILY_ID, YARN_SUBFAMILY_ID
from src.operations.failures import (
    DUPLICATE_FIBER_IN_YARN_RECIPE_FAILURE,
    FIBER_DISABLED_IN_YARN_RECIPE_FAILURE,
    FIBER_NOT_FOUND_IN_YARN_RECIPE_FAILURE,
    INVALID_YARN_RECIPE_FAILURE,
    MECSA_COLOR_DISABLED_FAILURE,
    YARN_ALREADY_EXISTS_FAILURE,
    YARN_DISABLED_FAILURE,
    YARN_NOT_FOUND_FAILURE,
    YARN_PARTIAL_UPDATE_FAILURE,
    YARN_UPDATE_FAILURE_DUE_TO_FABRIC_RECIPE_IN_USE,
    YARN_UPDATE_FAILURE_DUE_TO_PURCHASE_ORDER_IN_USE,
)
from src.operations.models import (
    FabricYarn,
    Fiber,
    InventoryItem,
    MovementDetail,
    OrdenCompraDetalle,
    YarnDistinction,
    YarnFiber,
)
from src.operations.repositories import (
    FabricRecipeRepository,
    YarnRecipeRepository,
    YarnRepository,
)
from src.operations.schemas import (
    FiberOptions,
    YarnCreateSchema,
    YarnListSchema,
    YarnOptions,
    YarnRecipeItemSimpleSchema,
    YarnSchema,
    YarnUpdateSchema,
)
from src.operations.sequences import product_id_seq
from src.security.loaders import (
    SpinningMethods,
    YarnCounts,
    YarnDistinctions,
    YarnManufacturingSites,
)
from src.security.models import Parameter
from src.security.services import ParameterService

from .fiber_service import FiberService
from .mecsa_color_service import MecsaColorService
from .series_service import BarcodeSeries


class YarnService:
    def __init__(self, db: AsyncSession, promec_db: AsyncSession):
        self.repository = YarnRepository(db=promec_db)
        self.parameter_service = ParameterService(db=db)
        self.mecsa_color_service = MecsaColorService(promec_db=promec_db)
        self.product_sequence = SequenceRepository(
            sequence=product_id_seq, db=promec_db
        )
        self.spinning_methods = SpinningMethods(db=db)
        self.fiber_service = FiberService(db=db, promec_db=promec_db)
        self.recipe_repository = YarnRecipeRepository(db=db)
        self.barcode_series = BarcodeSeries(promec_db=promec_db)
        self.yarn_counts = YarnCounts(db=db)
        self.manufacturing_sites = YarnManufacturingSites(db=db)
        self.distinctions = YarnDistinctions(db=db)
        self.fabric_recipe_repository = FabricRecipeRepository(db=promec_db)
        self.distinction_repository = BaseRepository[YarnDistinction](
            model=YarnDistinction, db=db
        )
        self.purcharse_order_detail_repository = BaseRepository[OrdenCompraDetalle](
            model=OrdenCompraDetalle, db=promec_db
        )
        self.movement_detail_repository = BaseRepository[MovementDetail](
            model=MovementDetail, db=promec_db
        )
        """
        field1 = yarn_count
        field2 = spinning_method_id
        field3 = color_id
        field4 = manufactured_in_id
        """

    async def _assign_recipe_to_yarns(
        self, yarns: list[InventoryItem], include_fiber_instance: bool = False
    ) -> None:
        if not yarns:
            return None

        yarn_recipe_mapping = {yarn.id: [] for yarn in yarns}
        items = await self.recipe_repository.find_all(
            filter=YarnFiber.yarn_id.in_(yarn_recipe_mapping.keys())
        )

        fiber_mapping: dict[str, Fiber] = dict()
        if include_fiber_instance:
            fiber_ids = list(set(item.fiber_id for item in items))
            fiber_mapping = (
                await self.fiber_service.map_fibers_by_ids(
                    fiber_ids=fiber_ids, options=FiberOptions.all()
                )
            ).value

        for item in items:
            item.fiber = (
                fiber_mapping.get(item.fiber_id, None)
                if include_fiber_instance
                else None
            )
            yarn_recipe_mapping[item.yarn_id].append(item)

        for yarn in yarns:
            yarn.recipe = yarn_recipe_mapping[yarn.id]

    async def _assign_distinctions_to_yarns(
        self, yarns: list[InventoryItem], include_distinction_instances: bool = False
    ) -> list[int]:
        yarn_mapping = {yarn.id: yarn for yarn in yarns if yarn.id.isdigit()}
        for yarn in yarns:
            setattr(yarn, "distinction_items", [])
            setattr(yarn, "distinction_ids", [])
            setattr(yarn, "distinctions", [])

        items = await self.distinction_repository.find_all(
            filter=YarnDistinction.yarn_id.in_(list(yarn_mapping.keys()))
        )
        distinction_ids = list({item.distinction_id for item in items})
        for item in items:
            if yarn := yarn_mapping.get(item.yarn_id):
                yarn.distinction_ids.append(item.distinction_id)
                yarn.distinction_items.append(item)

        if include_distinction_instances:
            mapping = (
                await self.parameter_service.map_parameters_by_ids(
                    parameter_ids=distinction_ids,
                    load_only_value=True,
                )
            ).value
            self._assign_distinction_instances_to_yarns(
                yarns=yarns,
                distinction_mapping=mapping,
            )

        return distinction_ids

    def _assign_distinction_instances_to_yarns(
        self,
        yarns: list[InventoryItem],
        distinction_mapping: dict[int, Parameter],
    ):
        for yarn in yarns:
            yarn.distinctions = [
                distinction_mapping[distinction_id]
                for distinction_id in yarn.distinction_ids
                if distinction_id in distinction_mapping
            ]

    async def _load_related_data_for_yarns(
        self,
        yarns: list[InventoryItem],
        include_yarn_count: bool = False,
        include_spinning_method: bool = False,
        include_manufactured_in: bool = False,
        include_recipe: bool = False,
        include_fiber_instance: bool = False,
        include_distinctions: bool = False,
        include_distinction_instances: bool = False,
        **kwargs,
    ) -> None:
        if include_recipe:
            await self._assign_recipe_to_yarns(
                yarns=yarns, include_fiber_instance=include_fiber_instance
            )

        distinction_ids = []
        if include_distinctions:
            distinction_ids = await self._assign_distinctions_to_yarns(yarns=yarns)

        mapping = {
            "yarn_count": ("field1", include_yarn_count),
            "spinning_method": ("field2", include_spinning_method),
            "manufactured_in": ("field4", include_manufactured_in),
        }

        field_id_mapping = {
            value: int(value)
            for _, (yarn_field, include_flag) in mapping.items()
            if include_flag
            for yarn in yarns
            if (value := getattr(yarn, yarn_field, "")) and value.isdigit()
        }
        ids = (
            list(field_id_mapping.values()) + distinction_ids
            if include_distinction_instances
            else list(field_id_mapping.values())
        )
        if not ids:
            return None

        field_mapping = (
            await self.parameter_service.map_parameters_by_ids(
                parameter_ids=ids,
                load_only_value=True,
            )
        ).value
        for field_name, (yarn_field, include_flag) in mapping.items():
            if not include_flag:
                continue
            for yarn in yarns:
                value = field_mapping.get(
                    field_id_mapping.get(getattr(yarn, yarn_field))
                )
                setattr(yarn, field_name, value)

        if include_distinction_instances:
            self._assign_distinction_instances_to_yarns(
                yarns=yarns,
                distinction_mapping=field_mapping,
            )

    async def _validate_yarn_data(
        self,
        yarn_count_id: int | None = None,
        spinning_method_id: int | None = None,
        manufactured_in_id: int | None = None,
        color_id: str | None = None,
        distinction_ids: list[int] = [],
        **kwargs,
    ) -> Result[None, CustomException]:
        validation = await self.parameter_service.validate_parameters(
            parameter_id_validator_pairs=[
                (yarn_count_id, self.yarn_counts),
                (spinning_method_id, self.spinning_methods),
                (manufactured_in_id, self.manufacturing_sites),
                *[
                    (distinction_id, self.distinctions)
                    for distinction_id in distinction_ids
                ],
            ]
        )
        if validation.is_failure:
            return validation

        if color_id:
            color_result = await self.mecsa_color_service.read_mecsa_color(color_id)
            if color_result.is_failure:
                return color_result
            if not is_active_status(color_result.value.is_active):
                return MECSA_COLOR_DISABLED_FAILURE

        return Success(None)

    async def _validate_yarn_recipe(
        self, yarn_recipe: list[YarnRecipeItemSimpleSchema]
    ) -> Result[None, CustomException]:
        total = sum(map(lambda item: item.proportion, yarn_recipe), 0)
        if total != 100.0:
            return INVALID_YARN_RECIPE_FAILURE

        fiber_ids = {item.fiber_id for item in yarn_recipe}
        if len(yarn_recipe) != len(fiber_ids):
            return DUPLICATE_FIBER_IN_YARN_RECIPE_FAILURE

        fibers = (
            await self.fiber_service.read_fibers_by_ids(fiber_ids=list(fiber_ids))
        ).value

        if len(yarn_recipe) != len(fibers):
            return FIBER_NOT_FOUND_IN_YARN_RECIPE_FAILURE

        if any(not fiber.is_active for fiber in fibers):
            return FIBER_DISABLED_IN_YARN_RECIPE_FAILURE

        return Success(None)

    def _is_yarn_recipe_unique(
        self,
        current_recipe: list[YarnRecipeItemSimpleSchema],
        yarns: list[InventoryItem],
    ) -> bool:
        _current_recipe = {(item.fiber_id, item.proportion) for item in current_recipe}
        recipe_size = len(_current_recipe)

        return not any(
            recipe_size == len(yarn.recipe)
            and _current_recipe
            == {(item.fiber_id, item.proportion) for item in yarn.recipe}
            for yarn in yarns
        )

    async def _is_same_recipe(
        self, current_yarn: InventoryItem, new_recipe: list[YarnRecipeItemSimpleSchema]
    ) -> bool:
        if not hasattr(current_yarn, "recipe"):
            await self._assign_recipe_to_yarns([current_yarn])

        return not self._is_yarn_recipe_unique(
            current_recipe=new_recipe, yarns=[current_yarn]
        )

    async def _is_yarn_unique(
        self,
        yarn_count_id_: str,
        spinning_method_id_: str,
        color_id: str,
        manufactured_in_id_: str,
        distinction_ids: list[int],
        current_yarn: InventoryItem | None = None,
        current_recipe: list[YarnRecipeItemSimpleSchema] | None = None,
        **kwargs,
    ) -> bool:
        filter = (
            (InventoryItem.field1 == yarn_count_id_)
            & (InventoryItem.field2 == spinning_method_id_)
            & (InventoryItem.field3 == color_id)
            & (InventoryItem.field4 == manufactured_in_id_)
        )
        _yarns = await self.repository.find_yarns(filter=filter)
        yarns = (
            _yarns
            if current_yarn is None
            else [yarn for yarn in _yarns if yarn != current_yarn]
        )
        if len(yarns) == 0:  # yarn has unique attributes
            return True

        await self._assign_distinctions_to_yarns(yarns=yarns)
        distinction_ids_ = set(distinction_ids)
        if all(distinction_ids_ != set(yarn.distinction_ids) for yarn in yarns):
            return True

        await self._assign_recipe_to_yarns(yarns=_yarns)
        if current_recipe is None:
            current_recipe = [
                YarnRecipeItemSimpleSchema.model_validate(item)
                for item in current_yarn.recipe
            ]

        return self._is_yarn_recipe_unique(current_recipe=current_recipe, yarns=yarns)

    async def _read_yarn(
        self,
        yarn_id: str,
        options: YarnOptions = YarnOptions(),
    ) -> Result[InventoryItem, CustomException]:
        yarn = await self.repository.find_yarn_by_id(
            yarn_id=yarn_id, include_color=options.include_color
        )

        if yarn is None:
            return YARN_NOT_FOUND_FAILURE

        await self._load_related_data_for_yarns(yarns=[yarn], **options.model_dump())

        return Success(yarn)

    async def read_yarn(
        self,
        yarn_id: str,
        options: YarnOptions = YarnOptions(),
    ) -> Result[YarnSchema, CustomException]:
        yarn_result = await self._read_yarn(
            yarn_id=yarn_id,
            options=options,
        )

        if yarn_result.is_failure:
            return yarn_result

        return Success(YarnSchema.model_validate(yarn_result.value))

    async def read_yarns(
        self,
        options: YarnOptions = YarnOptions(),
        include_inactives: bool = True,
        exclude_legacy: bool = False,
    ) -> Result[YarnListSchema, CustomException]:
        yarns = await self.repository.find_yarns(
            include_inactives=include_inactives,
            order_by=InventoryItem.id.asc(),
            include_color=options.include_color,
            exclude_legacy=exclude_legacy,
        )

        await self._load_related_data_for_yarns(
            yarns=yarns,
            **options.model_dump(),
        )

        return Success(YarnListSchema(yarns=yarns))

    async def create_yarn(
        self, form: YarnCreateSchema
    ) -> Result[None, CustomException]:
        attributes = form.model_dump(exclude={"description", "recipe"})
        validation_result = await self._validate_yarn_data(**attributes)
        if validation_result.is_failure:
            return validation_result

        recipe_validation_result = await self._validate_yarn_recipe(
            yarn_recipe=form.recipe
        )
        if recipe_validation_result.is_failure:
            return recipe_validation_result

        if not (await self._is_yarn_unique(**attributes, current_recipe=form.recipe)):
            return YARN_ALREADY_EXISTS_FAILURE

        yarn_id = str(await self.product_sequence.next_value())
        barcode = (
            await self.barcode_series.next_number()
        )  # Throws failure if series not found
        yarn = InventoryItem(
            id=yarn_id,
            family_id=SUPPLY_FAMILY_ID,
            subfamily_id=YARN_SUBFAMILY_ID,
            base_unit_code="KG",
            inventory_unit_code="KG",
            purchase_unit_code="KG",
            description=form.description,
            purchase_description_=form.description,
            barcode=barcode,
            field1=form.yarn_count_id_,
            field2=form.spinning_method_id_,
            field3=form.color_id,
            field4=form.manufactured_in_id_,
        )
        await self.repository.save(yarn)
        await self.recipe_repository.save_all(
            YarnFiber(yarn_id=yarn_id, **item.model_dump()) for item in form.recipe
        )
        if form.distinction_ids:
            await self.distinction_repository.save_all(
                YarnDistinction(yarn_id=yarn_id, distinction_id=id)
                for id in form.distinction_ids
            )

        return Success(None)

    async def update_yarn(
        self, yarn_id: str, form: YarnUpdateSchema
    ) -> Result[None, CustomException]:
        yarn_result = await self._read_yarn(yarn_id=yarn_id)
        if yarn_result.is_failure:
            return yarn_result

        yarn: InventoryItem = yarn_result.value
        yarn_data = form.model_dump(exclude_unset=True)
        if len(yarn_data) == 0:
            return Success(None)

        result = await self.validate_yarn_updatable(yarn=yarn, yarn_id=yarn.id)
        if result.is_failure:
            return result
        elif not result.value.updatable:
            return result.value.failure

        form_has_yarn_attributes = any(
            field in yarn_data
            for field in (
                "yarn_count_id",
                "spinning_method_id",
                "color_id",
                "manufactured_in_id",
                "distinction_ids",
                "recipe",
            )
        )
        if form_has_yarn_attributes and result.value.is_partial:
            return YARN_PARTIAL_UPDATE_FAILURE()

        validation_result = await self._validate_yarn_data(**yarn_data)
        if validation_result.is_failure:
            return validation_result

        yarn.field1 = (
            form.yarn_count_id_ if "yarn_count_id" in yarn_data else yarn.field1
        )
        yarn.field2 = (
            form.spinning_method_id_
            if "spinning_method_id" in yarn_data
            else yarn.field2
        )
        yarn.field3 = yarn_data.get("color_id", yarn.field3)
        yarn.field4 = (
            form.manufactured_in_id_
            if "manufactured_in_id" in yarn_data
            else yarn.field4
        )
        new_description = yarn_data.get("description", yarn.description)
        if yarn.description != new_description:
            yarn.description = new_description
            yarn.purchase_description_ = new_description

        if form.recipe is not None:
            recipe_validation_result = await self._validate_yarn_recipe(
                yarn_recipe=form.recipe
            )
            if recipe_validation_result.is_failure:
                return recipe_validation_result

        await self._assign_distinctions_to_yarns(yarns=[yarn])
        prev_distinction_ids = yarn.distinction_ids
        yarn.distinction_ids = yarn_data.get("distinction_ids", yarn.distinction_ids)
        if form_has_yarn_attributes and not (
            await self._is_yarn_unique(
                yarn_count_id_=yarn.field1,
                spinning_method_id_=yarn.field2,
                color_id=yarn.field3,
                manufactured_in_id_=yarn.field4,
                distinction_ids=yarn.distinction_ids,
                current_yarn=yarn,
                current_recipe=form.recipe,
            )
        ):
            return YARN_ALREADY_EXISTS_FAILURE

        await self.repository.save(yarn)
        if form.recipe is not None and not (
            await self._is_same_recipe(current_yarn=yarn, new_recipe=form.recipe)
        ):
            await self.recipe_repository.delete_all([item for item in yarn.recipe])
            await self.recipe_repository.save_all(
                YarnFiber(yarn_id=yarn_id, **item.model_dump()) for item in form.recipe
            )
        if set(prev_distinction_ids) != set(yarn.distinction_ids):
            await self.distinction_repository.delete_all(yarn.distinction_items)
            await self.distinction_repository.save_all(
                YarnDistinction(yarn_id=yarn_id, distinction_id=id)
                for id in yarn.distinction_ids
            )

        return Success(None)

    async def update_status(
        self, yarn_id: str, is_active: bool = True
    ) -> Result[None, CustomException]:
        yarn_result = await self._read_yarn(yarn_id=yarn_id)
        if yarn_result.is_failure:
            return yarn_result

        yarn: InventoryItem = yarn_result.value
        yarn.is_active = map_active_status(is_active)
        await self.repository.save(yarn)

        return Success(None)

    async def read_yarns_by_ids(
        self,
        yarn_ids: list[str],
        options: YarnOptions = YarnOptions(),
        include_inactives: bool = True,
        exclude_legacy: bool = False,
    ) -> Result[YarnListSchema, CustomException]:
        if not yarn_ids:
            return Success(YarnListSchema(yarns=[]))

        yarns = await self.repository.find_yarns(
            filter=InventoryItem.id.in_(yarn_ids),
            include_inactives=include_inactives,
            include_color=options.include_color,
            exclude_legacy=exclude_legacy,
        )

        await self._load_related_data_for_yarns(
            yarns=yarns,
            **options.model_dump(),
        )

        return Success(YarnListSchema(yarns=yarns))

    async def map_yarns_by_ids(
        self,
        yarn_ids: list[str],
        options: YarnOptions = YarnOptions(),
    ) -> Result[dict[str, YarnSchema], CustomException]:
        yarns = (
            await self.read_yarns_by_ids(
                yarn_ids=yarn_ids,
                options=options,
            )
        ).value.yarns

        return Success({yarn.id: yarn for yarn in yarns})

    async def read_yarns_by_recipe(
        self,
        fiber_ids: list[str],
        options: YarnOptions = YarnOptions(),
        include_inactives: bool = True,
        exclude_legacy: bool = False,
    ) -> Result[YarnListSchema, CustomException]:
        yarn_ids = await self.recipe_repository.find_yarn_ids_by_recipe(
            fiber_ids=fiber_ids,
        )

        return await self.read_yarns_by_ids(
            yarn_ids=yarn_ids,
            options=options,
            include_inactives=include_inactives,
            exclude_legacy=exclude_legacy,
        )

    async def validate_yarn_updatable(
        self, yarn_id: str, yarn: InventoryItem = None
    ) -> Result[ItemIsUpdatableSchema, CustomException]:
        update_message = (
            "Es posible realizar una actualización completa del hilado especificado."
        )
        is_partial = False
        failure = None
        yarn_result = Success(yarn) if yarn else await self._read_yarn(yarn_id=yarn_id)
        if yarn_result.is_failure:
            return Success(ItemIsUpdatableSchema(failure=yarn_result))

        yarn = yarn_result.value
        if not is_active_status(yarn.is_active):
            return Success(ItemIsUpdatableSchema(failure=YARN_DISABLED_FAILURE))

        recipe_items = await self.fabric_recipe_repository.find_all(
            filter=FabricYarn.yarn_id == yarn.id, limit=1
        )
        if recipe_items:
            is_partial = True
            failure = YARN_UPDATE_FAILURE_DUE_TO_FABRIC_RECIPE_IN_USE

        order_detail_items = await self.purcharse_order_detail_repository.find_all(
            filter=and_(
                OrdenCompraDetalle.company_code == MECSA_COMPANY_CODE,
                OrdenCompraDetalle.product_code == yarn.id,
                OrdenCompraDetalle.status_flag != "A",
            ),
            limit=1,
        )
        if order_detail_items:
            is_partial = True
            failure = YARN_UPDATE_FAILURE_DUE_TO_PURCHASE_ORDER_IN_USE

        # TODO: It's too slow. An index is needed on the MovementDetail table
        # movement_detail_items = await self.movement_detail_repository.find_all(
        #     filter=and_(
        #         MovementDetail.company_code == MECSA_COMPANY_CODE,
        #         MovementDetail.product_code == yarn.id,
        #         MovementDetail.status_flag != "A",
        #     ),
        #     limit=1,
        # )
        # if movement_detail_items:
        #     is_partial = True
        #     failure = YARN_UPDATE_FAILURE_DUE_TO_MOVEMENT_IN_USE

        failure = (
            YARN_PARTIAL_UPDATE_FAILURE(failure.error.detail) if failure else failure
        )
        message = update_message if not is_partial else failure.error.detail
        fields = [] if not is_partial else ["description"]
        return Success(
            ItemIsUpdatableSchema(
                is_partial=is_partial, message=message, failure=failure, fields=fields
            )
        )
