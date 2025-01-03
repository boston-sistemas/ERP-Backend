from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.repositories import SequenceRepository
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
    INVALID_STRUCTURE_PATTERN_FOR_JERSEY_FAILURE,
    INVALID_STRUCTURE_PATTERN_FOR_RIB_BVD_FAILURE,
    MECSA_COLOR_DISABLED_FAILURE,
    YARN_DISABLED_IN_FABRIC_RECIPE_FAILURE,
    YARN_NOT_FOUND_IN_FABRIC_RECIPE_FAILURE,
)
from src.operations.models import FabricYarn, InventoryItem
from src.operations.repositories import FabricRecipeRepository, FabricRepository
from src.operations.schemas import (
    FabricCreateSchema,
    FabricListSchema,
    FabricRecipeItemSimpleSchema,
    FabricSchema,
    FabricUpdateSchema,
)
from src.operations.sequences import product_id_seq
from src.security.loaders import FabricTypes, JerseyFabric, RibBvdFabric
from src.security.services import ParameterService

from .mecsa_color_service import MecsaColorService
from .series_service import BarcodeSeries
from .yarn_service import YarnService


class FabricService:
    def __init__(self, db: AsyncSession, promec_db: AsyncSession):
        self.repository = FabricRepository(db=promec_db)
        self.recipe_repository = FabricRecipeRepository(db=promec_db)
        self.mecsa_color_service = MecsaColorService(promec_db=promec_db)
        self.product_sequence = SequenceRepository(
            sequence=product_id_seq, db=promec_db
        )
        self.yarn_service = YarnService(db=db, promec_db=promec_db)
        self.parameter_service = ParameterService(db=db)
        self.barcode_series = BarcodeSeries(promec_db=promec_db)
        self.fabric_types = FabricTypes(db=db)
        self.jersey_fabric = JerseyFabric(db=db)
        self.rib_bvd_fabric = RibBvdFabric(db=db)
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

    async def _assign_recipe_to_fabrics(
        self, fabrics: list[InventoryItem], include_yarn_instance: bool = False
    ) -> None:
        if not fabrics:
            return None

        fabric_recipe_mapping = {fabric.id: [] for fabric in fabrics}
        items = await self.recipe_repository.find_all(
            filter=FabricYarn.fabric_id.in_(fabric_recipe_mapping.keys())
        )

        for item in items:
            fabric_recipe_mapping[item.fabric_id].append(item)

        for fabric in fabrics:
            fabric.fabric_recipe = fabric_recipe_mapping[fabric.id]

        if include_yarn_instance:
            await self._include_yarn_instance_to_recipes(fabrics=fabrics)

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
        self,
        fabric_type_id: int | None = None,
        color_id: str | None = None,
        **kwargs,
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

    def _validate_fabric(
        self, fabric_type_id: int, structure_pattern: str | None
    ) -> Result[None, CustomException]:
        if self.jersey_fabric.id == fabric_type_id and structure_pattern != "LISO":
            return INVALID_STRUCTURE_PATTERN_FOR_JERSEY_FAILURE

        if self.rib_bvd_fabric.id == fabric_type_id and structure_pattern:
            return INVALID_STRUCTURE_PATTERN_FOR_RIB_BVD_FAILURE

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

    async def _is_same_recipe(
        self,
        current_fabric: InventoryItem,
        new_recipe: list[FabricRecipeItemSimpleSchema],
    ) -> bool:
        if not current_fabric.fabric_recipe:
            current_fabric.fabric_recipe = await self.recipe_repository.find_all(
                filter=FabricYarn.fabric_id == current_fabric.id
            )

        return not self._is_fabric_recipe_unique(
            current_recipe=new_recipe, fabrics=[current_fabric]
        )

    async def _is_fabric_unique(
        self,
        fabric_type_id_: str,
        width_: str,
        color_id: str,
        structure_pattern: str,
        current_fabric: InventoryItem | None = None,
        current_recipe: list[FabricRecipeItemSimpleSchema] | None = None,
        **kwargs,
    ) -> bool:
        filter = (
            (InventoryItem.field2 == width_)
            & (InventoryItem.field4 == fabric_type_id_)
            & (InventoryItem.field3 == color_id)
            & (InventoryItem.field5 == structure_pattern)
        )
        _fabrics = await self.repository.find_fabrics(
            filter=filter, include_simple_recipe=True
        )
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
        include_yarn_instance_to_recipe: bool = False,
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

        if include_yarn_instance_to_recipe:
            await self._include_yarn_instance_to_recipes([fabric])

        return Success(fabric)

    async def read_fabric(
        self,
        fabric_id: str,
        include_fabric_type: bool = False,
        include_color: bool = False,
        include_recipe: bool = False,
        include_yarn_instance_to_recipe: bool = False,
    ) -> Result[FabricSchema, CustomException]:
        fabric_result = await self._read_fabric(
            fabric_id=fabric_id,
            include_color=include_color,
            include_fabric_type=include_fabric_type,
            include_recipe=include_recipe,
            include_yarn_instance_to_recipe=include_yarn_instance_to_recipe,
        )

        if fabric_result.is_failure:
            return fabric_result

        return Success(FabricSchema.model_validate(fabric_result.value))

    async def read_fabrics(
        self,
        include_fabric_type: bool = False,
        include_color: bool = False,
        include_recipe: bool = False,
        include_yarn_instance_to_recipe: bool = False,
        exclude_legacy: bool = False,
    ) -> Result[FabricListSchema, CustomException]:
        _include_recipe = (not exclude_legacy) and include_recipe
        fabrics = await self.repository.find_fabrics(
            include_color=include_color,
            include_simple_recipe=_include_recipe,
            exclude_legacy=exclude_legacy,
        )
        if include_fabric_type:
            await self._assign_fabric_type_to_fabrics(fabrics)

        if include_recipe:
            await self._assign_recipe_to_fabrics(
                fabrics=fabrics, include_yarn_instance=include_yarn_instance_to_recipe
            )

        return Success(FabricListSchema(fabrics=fabrics))

    async def create_fabric(
        self, form: FabricCreateSchema
    ) -> Result[None, CustomException]:
        data_validation = await self._validate_fabric_data(
            fabric_type_id=form.fabric_type_id, color_id=form.color_id
        )
        if data_validation.is_failure:
            return data_validation

        fabric_validation = self._validate_fabric(
            fabric_type_id=form.fabric_type_id, structure_pattern=form.structure_pattern
        )
        if fabric_validation.is_failure:
            return fabric_validation

        recipe_validation = await self._validate_fabric_recipe(
            fabric_recipe=form.recipe
        )
        if recipe_validation.is_failure:
            return recipe_validation

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

    async def update_fabric(
        self, fabric_id: str, form: FabricUpdateSchema
    ) -> Result[None, CustomException]:
        fabric_result = await self._read_fabric(fabric_id=fabric_id)
        if fabric_result.is_failure:
            return fabric_result

        fabric: InventoryItem = fabric_result.value
        fabric_data = form.model_dump(exclude_unset=True)
        if len(fabric_data) == 0:
            return Success(None)

        data_validation = await self._validate_fabric_data(**fabric_data)
        if data_validation.is_failure:
            return data_validation

        fabric.field1 = str(fabric_data.get("density", fabric.field1))
        fabric.field2 = str(fabric_data.get("width", fabric.field2))
        fabric.field3 = fabric_data.get("color_id", fabric.field3)
        fabric.field4 = str(fabric_data.get("fabric_type_id", fabric.field4))
        fabric.field5 = fabric_data.get("structure_pattern", fabric.field5)
        fabric.description = fabric_data.get("description", fabric.description)
        fabric.purchase_description = fabric.description

        try:
            fabric_validation = self._validate_fabric(
                fabric_type_id=int(fabric.field4), structure_pattern=fabric.field5
            )
            if fabric_validation.is_failure:
                return fabric_validation
        except Exception:
            pass

        if form.recipe is not None:
            recipe_validation_result = await self._validate_fabric_recipe(
                fabric_recipe=form.recipe
            )
            if recipe_validation_result.is_failure:
                return recipe_validation_result

        if any(
            field in fabric_data
            for field in (
                "fabric_type_id",
                "width",
                "color_id",
                "structure_pattern",
                "recipe",
            )
        ) and not (
            await self._is_fabric_unique(
                fabric_type_id_=fabric.field4,
                width_=fabric.field2,
                color_id=fabric.field3,
                structure_pattern=fabric.field5,
                current_fabric=fabric,
                current_recipe=form.recipe,
            )
        ):
            return FABRIC_ALREADY_EXISTS_FAILURE

        await self.repository.save(fabric)
        if form.recipe is None:
            return Success(None)

        same_recipe = await self._is_same_recipe(
            current_fabric=fabric, new_recipe=form.recipe
        )
        if same_recipe:
            mapping = {
                (item.yarn_id, item.num_plies): item for item in fabric.fabric_recipe
            }
            for item in form.recipe:
                current_item = mapping[(item.yarn_id, item.num_plies)]
                current_item.diameter = item.diameter
                current_item.galgue = item.galgue
                current_item.stitch_length = item.stitch_length

            await self.recipe_repository.save_all(list(mapping.values()))
        else:
            recipe_items = [item for item in fabric.fabric_recipe]
            fabric.fabric_recipe = []  # Ensures delete operations are executed before saving the new recipe

            await self.recipe_repository.delete_all(recipe_items, flush=False)
            await self.recipe_repository.save_all(
                FabricYarn(fabric_id=fabric.id, **item.model_dump())
                for item in form.recipe
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

    async def find_fabrics_by_ids(
        self,
        fabric_ids: list[str],
        include_fabric_type: bool = False,
        include_color: bool = False,
        include_recipe: bool = False,
        include_yarn_instance_to_recipe: bool = False,
    ) -> Result[FabricListSchema, CustomException]:
        if not fabric_ids:
            return Success([])

        fabrics = await self.repository.find_fabrics(
            filter=InventoryItem.id.in_(fabric_ids),
            include_color=include_color,
            include_simple_recipe=include_recipe,
        )

        if include_fabric_type:
            await self._assign_fabric_type_to_fabrics(fabrics)

        if include_yarn_instance_to_recipe:
            await self._include_yarn_instance_to_recipes(fabrics=fabrics)

        return Success(FabricListSchema(fabrics=fabrics))

    async def map_fabrics_by_ids(
        self,
        fabric_ids: list[str],
        include_fabric_type: bool = False,
        include_color: bool = False,
        include_recipe: bool = False,
        include_yarn_instance_to_recipe: bool = False,
    ) -> Result[dict[str, FabricSchema], CustomException]:
        fabrics = (
            await self.find_fabrics_by_ids(
                fabric_ids=fabric_ids,
                include_fabric_type=include_fabric_type,
                include_color=include_color,
                include_recipe=include_recipe,
                include_yarn_instance_to_recipe=include_yarn_instance_to_recipe,
            )
        ).value.fabrics

        return Success({fabric.id: fabric for fabric in fabrics})

    async def find_fabrics_by_recipe(
        self,
        yarn_ids: list[str],
        include_fabric_type: bool = False,
        include_color: bool = False,
        include_recipe: bool = False,
        include_yarn_instance_to_recipe: bool = False,
    ) -> Result[FabricListSchema, CustomException]:
        fabric_ids = await self.recipe_repository.find_fabrics_by_recipe(
            yarn_ids=yarn_ids
        )
        return await self.find_fabrics_by_ids(
            fabric_ids=fabric_ids,
            include_fabric_type=include_fabric_type,
            include_color=include_color,
            include_recipe=include_recipe,
            include_yarn_instance_to_recipe=include_yarn_instance_to_recipe,
        )
