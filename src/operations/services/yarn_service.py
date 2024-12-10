from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.repositories import SequenceRepository
from src.core.result import Result, Success
from src.core.utils import is_active_status, map_active_status
from src.operations.constants import SUPPLY_FAMILY_ID, YARN_SUBFAMILY_ID
from src.operations.failures import (
    DUPLICATE_FIBER_IN_YARN_RECIPE_FAILURE,
    FIBER_DISABLED_IN_YARN_RECIPE_FAILURE,
    FIBER_NOT_FOUND_IN_YARN_RECIPE_FAILURE,
    INVALID_YARN_RECIPE_FAILURE,
    MECSA_COLOR_DISABLED_FAILURE,
    SPINNING_METHOD_DISABLED_YARN_VALIDATION_FAILURE,
    SPINNING_METHOD_NOT_FOUND_YARN_VALIDATION_FAILURE,
    YARN_ALREADY_EXISTS_FAILURE,
    YARN_COUNT_NULL_VALIDATION_FAILURE,
    YARN_NOT_FOUND_FAILURE,
    YARN_NUMBERING_NULL_VALIDATION_FAILURE,
    YARN_RECIPE_NULL_VALIDATION_FAILURE,
)
from src.operations.models import Fiber, InventoryItem, YarnFiber
from src.operations.repositories import (
    YarnRecipeRepository,
    YarnRepository,
)
from src.operations.schemas import (
    YarnCreateSchema,
    YarnListSchema,
    YarnRecipeItemSimpleSchema,
    YarnSchema,
    YarnUpdateSchema,
)
from src.operations.sequences import product_id_seq
from src.security.loaders import SpinningMethods
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
        """
        field1 = yarn_count
        field2 = numbering_system
        field3 = spinning_method_id
        field4 = color_id
        """

    async def _assign_spinning_method_to_yarns(
        self, yarns: list[InventoryItem]
    ) -> None:
        spinnig_method_id_mapping = {
            yarn.field3: int(yarn.field3)
            for yarn in yarns
            if yarn.field3 and yarn.field3.isdigit()
        }
        if not spinnig_method_id_mapping:
            return None

        spinning_method_mapping = (
            await self.parameter_service.map_parameters_by_ids(
                parameter_ids=list(spinnig_method_id_mapping.values()),
                load_only_value=True,
            )
        ).value
        for yarn in yarns:
            yarn.spinning_method = spinning_method_mapping.get(
                spinnig_method_id_mapping.get(yarn.field3, None), None
            )

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
                    fiber_ids=fiber_ids,
                    include_category=include_fiber_instance,
                    include_color=include_fiber_instance,
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

    async def _validate_yarn_data(
        self,
        spinning_method_id: int | None = None,
        color_id: str | None = None,
        **kwargs,
    ) -> Result[None, CustomException]:
        if spinning_method_id is not None:
            result = await self.spinning_methods.validate(id=spinning_method_id)
            if result.is_failure:
                return SPINNING_METHOD_NOT_FOUND_YARN_VALIDATION_FAILURE
            if not result.value.is_active:
                return SPINNING_METHOD_DISABLED_YARN_VALIDATION_FAILURE

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
            await self.fiber_service.find_fibers_by_ids(fiber_ids=list(fiber_ids))
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
        self, current_yarn: Fiber, new_recipe: list[YarnRecipeItemSimpleSchema]
    ) -> bool:
        if not hasattr(current_yarn, "recipe"):
            await self._assign_recipe_to_yarns([current_yarn])

        return not self._is_yarn_recipe_unique(
            current_recipe=new_recipe, yarns=[current_yarn]
        )

    async def _is_yarn_unique(
        self,
        yarn_count: str,
        numbering_system: str,
        spinning_method_id_: str,
        color_id: str,
        current_yarn: InventoryItem | None = None,
        current_recipe: list[YarnRecipeItemSimpleSchema] | None = None,
        **kwargs,
    ) -> bool:
        filter = (
            (InventoryItem.field1 == yarn_count)
            & (InventoryItem.field2 == numbering_system)
            & (InventoryItem.field3 == spinning_method_id_)
            & (InventoryItem.field4 == color_id)
        )
        _yarns = await self.repository.find_yarns(filter=filter)
        yarns = (
            _yarns
            if current_yarn is None
            else [yarn for yarn in _yarns if yarn != current_yarn]
        )
        if len(yarns) == 0:  # yarn has unique attributes
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
        include_color: bool = False,
        include_spinning_method: bool = False,
        include_recipe: bool = False,
    ) -> Result[InventoryItem, CustomException]:
        yarn = await self.repository.find_yarn_by_id(
            yarn_id=yarn_id, include_color=include_color
        )

        if yarn is None:
            return YARN_NOT_FOUND_FAILURE

        if include_spinning_method:
            await self._assign_spinning_method_to_yarns([yarn])

        if include_recipe:
            await self._assign_recipe_to_yarns([yarn], include_fiber_instance=True)

        return Success(yarn)

    async def read_yarn(
        self,
        yarn_id: str,
        include_color: bool = False,
        include_spinning_method: bool = False,
        include_recipe: bool = False,
    ) -> Result[YarnSchema, CustomException]:
        yarn_result = await self._read_yarn(
            yarn_id=yarn_id,
            include_color=include_color,
            include_spinning_method=include_spinning_method,
            include_recipe=include_recipe,
        )

        if yarn_result.is_failure:
            return yarn_result

        return Success(YarnSchema.model_validate(yarn_result.value))

    async def read_yarns(
        self,
        include_color: bool = False,
        include_spinning_method: bool = False,
        include_recipe: bool = False,
        exclude_legacy: bool = False,
    ) -> Result[YarnListSchema, CustomException]:
        yarns = await self.repository.find_yarns(
            include_color=include_color, exclude_legacy=exclude_legacy
        )

        if include_spinning_method:
            await self._assign_spinning_method_to_yarns(yarns)

        if include_recipe:
            await self._assign_recipe_to_yarns(yarns=yarns, include_fiber_instance=True)

        return Success(YarnListSchema(yarns=yarns))

    async def create_yarn(
        self, form: YarnCreateSchema
    ) -> Result[None, CustomException]:
        validation_result = await self._validate_yarn_data(
            spinning_method_id=form.spinning_method_id, color_id=form.color_id
        )
        if validation_result.is_failure:
            return validation_result

        recipe_validation_result = await self._validate_yarn_recipe(
            yarn_recipe=form.recipe
        )
        if recipe_validation_result.is_failure:
            return recipe_validation_result

        if not (
            await self._is_yarn_unique(**form.model_dump(), current_recipe=form.recipe)
        ):
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
            purchase_description=form.description,
            barcode=barcode,
            field1=form.yarn_count,
            field2=form.numbering_system,
            field3=form.spinning_method_id_,
            field4=form.color_id,
        )
        await self.repository.save(yarn)
        await self.recipe_repository.save_all(
            YarnFiber(yarn_id=yarn_id, **item.model_dump()) for item in form.recipe
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

        if yarn_data.get("yarn_count", "") is None:
            return YARN_COUNT_NULL_VALIDATION_FAILURE
        if yarn_data.get("numbering_system", "") is None:
            return YARN_NUMBERING_NULL_VALIDATION_FAILURE
        if yarn_data.get("recipe", "") is None:
            return YARN_RECIPE_NULL_VALIDATION_FAILURE

        validation_result = await self._validate_yarn_data(**yarn_data)
        if validation_result.is_failure:
            return validation_result

        yarn.field1 = yarn_data.get("yarn_count", yarn.field1)
        yarn.field2 = yarn_data.get("numbering_system", yarn.field2)
        yarn.field3 = (
            form.spinning_method_id_
            if "spinning_method_id" in yarn_data
            else yarn.field3
        )
        yarn.field4 = yarn_data.get("color_id", yarn.field4)
        yarn.description = yarn_data.get("description", yarn.description)
        yarn.purchase_description = yarn.description

        if form.recipe is not None:
            recipe_validation_result = await self._validate_yarn_recipe(
                yarn_recipe=form.recipe
            )
            if recipe_validation_result.is_failure:
                return recipe_validation_result

        if any(
            field in yarn_data
            for field in (
                "yarn_count",
                "numbering_system",
                "spinning_method_id",
                "color_id",
                "recipe",
            )
        ) and not (
            await self._is_yarn_unique(
                yarn_count=yarn.field1,
                numbering_system=yarn.field2,
                spinning_method_id_=yarn.field3,
                color_id=yarn.field4,
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
