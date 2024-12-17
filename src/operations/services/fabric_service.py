from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.repositories import SequenceRepository
from src.core.repository import BaseRepository
from src.core.result import Result, Success
from src.core.utils import is_active_status, map_active_status
from src.operations.constants import FABRIC_FAMILY_ID
from src.operations.failures import (
    DUPLICATE_YARN_IN_FABRIC_RECIPE_FAILURE,
    FABRIC_ALREADY_EXISTS_FAILURE,
    FABRIC_NOT_FOUND_FAILURE,
    FABRIC_TYPE_DISABLED_FABRIC_VALIDATION_FAILURE,
    FABRIC_TYPE_NOT_FOUND_FABRIC_VALIDATION_FAILURE,
    INVALID_FABRIC_RECIPE_FAILURE,
    MECSA_COLOR_DISABLED_FAILURE,
    YARN_DISABLED_IN_FABRIC_RECIPE_FAILURE,
    YARN_NOT_FOUND_IN_FABRIC_RECIPE_FAILURE,
)
from src.operations.models import FabricYarn, InventoryItem
from src.operations.repositories import FabricRepository
from src.operations.schemas import (
    FabricCreateSchema,
    FabricListSchema,
    FabricRecipeItemSimpleSchema,
    FabricSchema,
)
from src.operations.sequences import product_id_seq
from src.security.loaders import FabricTypes
from src.security.services import ParameterService

from .mecsa_color_service import MecsaColorService
from .series_service import BarcodeSeries
from .yarn_service import YarnService


class FabricService:
    def __init__(self, db: AsyncSession, promec_db: AsyncSession):
        self.repository = FabricRepository(db=promec_db)
        self.recipe_repository = BaseRepository[FabricYarn](
            model=FabricYarn, db=promec_db
        )
        self.mecsa_color_service = MecsaColorService(promec_db=promec_db)
        self.product_sequence = SequenceRepository(
            sequence=product_id_seq, db=promec_db
        )
        self.yarn_service = YarnService(db=db, promec_db=promec_db)
        self.parameter_service = ParameterService(db=db)
        self.barcode_series = BarcodeSeries(promec_db=promec_db)
        self.fabric_types = FabricTypes(db=db)
        """
        field1 = density
        field2 = width
        field3 = color_id
        field4 = type_fabric_id
        field5 = structure_pattern
        """

    async def _assign_fabric_type_to_fabrics(
        self, fabrics: list[InventoryItem]
    ) -> None:
        type_fabric_id_mapping = {
            fabric.field4: int(fabric.field4)
            for fabric in fabrics
            if fabric.field4 and fabric.field4.isdigit()
        }
        if not type_fabric_id_mapping:
            return None

        type_fabric_mapping = (
            await self.parameter_service.map_parameters_by_ids(
                parameter_ids=list(type_fabric_id_mapping.values()),
                load_only_value=True,
            )
        ).value
        for fabric in fabrics:
            fabric.fabric_type = type_fabric_mapping.get(
                type_fabric_id_mapping.get(fabric.field4, None), None
            )

    async def _include_yarn_instance_to_recipes(
        self, fabrics: list[InventoryItem]
    ) -> None:
        if not fabrics:
            return None

        yarn_ids = {item.yarn_id for fabric in fabrics for item in fabric.fabric_recipe}
        if not yarn_ids:
            return None

        yarn_mapping = (
            await self.yarn_service.map_yarns_by_ids(
                yarn_ids=list(yarn_ids), include_color=True, include_recipe=True
            )
        ).value
        for fabric in fabrics:
            for item in fabric.fabric_recipe:
                item.yarn = yarn_mapping.get(item.yarn_id, None)

    async def _validate_fabric_data(
        self, fabric_type_id: int | None = None, color_id: str | None = None
    ) -> Result[None, CustomException]:
        if fabric_type_id is not None:
            result = await self.fabric_types.validate(id=fabric_type_id)
            if result.is_failure:
                return FABRIC_TYPE_NOT_FOUND_FABRIC_VALIDATION_FAILURE
            if not result.value.is_active:
                return FABRIC_TYPE_DISABLED_FABRIC_VALIDATION_FAILURE

        if color_id:
            color_result = await self.mecsa_color_service.read_mecsa_color(color_id)
            if color_result.is_failure:
                return color_result
            if not is_active_status(color_result.value.is_active):
                return MECSA_COLOR_DISABLED_FAILURE

        return Success(None)

    async def _validate_fabric_recipe(
        self, fabric_recipe: list[FabricRecipeItemSimpleSchema]
    ) -> Result[None, CustomException]:
        total = sum(map(lambda item: item.proportion, fabric_recipe), 0)
        if total != 100.0:
            return INVALID_FABRIC_RECIPE_FAILURE

        yarn_ids = {item.yarn_id for item in fabric_recipe}
        if len(fabric_recipe) != len(yarn_ids):
            return DUPLICATE_YARN_IN_FABRIC_RECIPE_FAILURE

        yarns = (
            await self.yarn_service.find_yarns_by_ids(yarn_ids=list(yarn_ids))
        ).value.yarns

        if len(fabric_recipe) != len(yarns):
            return YARN_NOT_FOUND_IN_FABRIC_RECIPE_FAILURE

        if any(not yarn.is_active for yarn in yarns):
            return YARN_DISABLED_IN_FABRIC_RECIPE_FAILURE

        return Success(None)

    def _is_fabric_recipe_unique(
        self,
        current_recipe: list[FabricRecipeItemSimpleSchema],
        fabrics: list[InventoryItem],
    ) -> bool:
        _current_recipe = {
            (item.yarn_id, item.proportion, item.num_plies) for item in current_recipe
        }
        recipe_size = len(_current_recipe)

        return not any(
            recipe_size == len(fabric.fabric_recipe)
            and _current_recipe
            == {
                (item.yarn_id, item.proportion, item.num_plies)
                for item in fabric.fabric_recipe
            }
            for fabric in fabrics
        )

    async def _is_fabric_unique(
        self,
        width_: str,
        fabric_type_id_: str,
        color_id: str,
        current_fabric: InventoryItem | None = None,
        current_recipe: list[FabricRecipeItemSimpleSchema] | None = None,
        **kwargs,
    ) -> bool:
        filter = (
            (InventoryItem.field2 == width_)
            & (InventoryItem.field4 == fabric_type_id_)
            & (InventoryItem.field3 == color_id)
        )
        _fabrics = await self.repository.find_fabrics(
            filter=filter, include_simple_recipe=True
        )
        from loguru import logger

        logger.debug(str(_fabrics))
        fabrics = (
            _fabrics
            if current_fabric is None
            else [fabric for fabric in _fabrics if fabric != current_fabric]
        )
        if len(fabrics) == 0:  # fabric has unique attributes
            return True

        if current_recipe is None:
            current_recipe = [
                FabricRecipeItemSimpleSchema.model_validate(item)
                for item in current_fabric.recipe
            ]

        return self._is_fabric_recipe_unique(
            current_recipe=current_recipe, fabrics=fabrics
        )

    async def _read_fabric(
        self,
        fabric_id: str,
        include_fabric_type: bool = False,
        include_color: bool = False,
        include_recipe: bool = False,
    ) -> Result[InventoryItem, CustomException]:
        fabric = await self.repository.find_fabric_by_id(
            fabric_id=fabric_id,
            include_color=include_color,
            include_simple_recipe=include_recipe,
        )

        if fabric is None:
            return FABRIC_NOT_FOUND_FAILURE

        if include_fabric_type:
            await self._assign_fabric_type_to_fabrics([fabric])

        if include_recipe:
            await self._include_yarn_instance_to_recipes([fabric])

        return Success(fabric)

    async def read_fabric(
        self,
        fabric_id: str,
        include_fabric_type: bool = False,
        include_color: bool = False,
        include_recipe: bool = False,
    ) -> Result[FabricSchema, CustomException]:
        fabric_result = await self._read_fabric(
            fabric_id=fabric_id,
            include_color=include_color,
            include_fabric_type=include_fabric_type,
            include_recipe=include_recipe,
        )

        if fabric_result.is_failure:
            return fabric_result

        return Success(FabricSchema.model_validate(fabric_result.value))

    async def read_fabrics(
        self,
        include_fabric_type: bool = False,
        include_color: bool = False,
        include_recipe: bool = False,
        exclude_legacy: bool = False,
    ) -> Result[FabricListSchema, CustomException]:
        fabrics = await self.repository.find_fabrics(
            include_color=include_color,
            include_simple_recipe=include_recipe,
            exclude_legacy=exclude_legacy,
        )
        if include_fabric_type:
            await self._assign_fabric_type_to_fabrics(fabrics)

        if include_recipe:
            await self._include_yarn_instance_to_recipes(fabrics=fabrics)

        return Success(FabricListSchema(fabrics=fabrics))

    async def create_fabric(
        self, form: FabricCreateSchema
    ) -> Result[None, CustomException]:
        validation_result = await self._validate_fabric_data(
            fabric_type_id=form.fabric_type_id, color_id=form.color_id
        )
        if validation_result.is_failure:
            return validation_result

        recipe_validation_result = await self._validate_fabric_recipe(
            fabric_recipe=form.recipe
        )
        if recipe_validation_result.is_failure:
            return recipe_validation_result

        if not (
            await self._is_fabric_unique(
                **form.model_dump(), current_recipe=form.recipe
            )
        ):
            return FABRIC_ALREADY_EXISTS_FAILURE

        fabric_id = str(await self.product_sequence.next_value())
        barcode = (
            await self.barcode_series.next_number()
        )  # Throws failure if series not found
        fabric = InventoryItem(
            id=fabric_id,
            family_id=FABRIC_FAMILY_ID,
            # subfamily_id=YARN_SUBFAMILY_ID,
            base_unit_code="KG",
            inventory_unit_code="KG",
            purchase_unit_code="KG",
            description=form.description,
            purchase_description=form.description,
            barcode=barcode,
            field1=str(form.density),
            field2=form.width_,
            field3=form.color_id,
            field4=form.fabric_type_id_,
            field5=form.structure_pattern,
        )
        await self.repository.save(fabric)
        await self.recipe_repository.save_all(
            FabricYarn(fabric_id=fabric_id, **item.model_dump()) for item in form.recipe
        )

        return Success(None)

    async def update_status(
        self, fabric_id: str, is_active: bool = True
    ) -> Result[None, CustomException]:
        fabric_result = await self._read_fabric(fabric_id=fabric_id)
        if fabric_result.is_failure:
            return fabric_result

        fabric: InventoryItem = fabric_result.value
        fabric.is_active = map_active_status(is_active)
        await self.repository.save(fabric)

        return Success(None)
