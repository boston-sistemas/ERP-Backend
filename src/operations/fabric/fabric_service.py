from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.repositories import SequenceRepository
from src.core.result import Result, Success
from src.core.utils import is_active_status, map_active_status
from src.operations.failures import (
    DUPLICATE_YARN_IN_FABRIC_RECIPE_FAILURE,
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
    FabricRecipeItemSimpleSchema,
    YarnOptions,
)
from src.operations.sequences import product_id_seq
from src.operations.services import BarcodeSeries, MecsaColorService, YarnService
from src.security.loaders import FabricTypes, JerseyFabric, RibBvdFabric
from src.security.services import ParameterService


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

        fabric_recipe_mapping = {
            fabric.id: [] for fabric in fabrics if not fabric.fabric_recipe
        }
        if fabric_recipe_mapping:
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
                yarn_ids=list(yarn_ids), options=YarnOptions.all()
            )
        ).value
        for fabric in fabrics:
            for item in fabric.fabric_recipe:
                item.yarn = yarn_mapping.get(item.yarn_id, None)

    async def _load_related_data_for_fabrics(
        self,
        fabrics: list[InventoryItem],
        include_fabric_type: bool = False,
        include_recipe: bool = False,
        include_yarn_instance_to_recipe: bool = False,
    ) -> None:
        purchase_description_mapping = {
            fabric.id: fabric.purchase_description for fabric in fabrics
        }

        if include_fabric_type:
            await self._assign_fabric_type_to_fabrics(fabrics=fabrics)

        old_fabrics = [fabric for fabric in fabrics if not fabric.id.isdigit()]
        new_fabrics = [fabric for fabric in fabrics if fabric.id.isdigit()]

        if new_fabrics and include_recipe:
            await self._assign_recipe_to_fabrics(
                fabrics=new_fabrics,
                include_yarn_instance=include_yarn_instance_to_recipe,
            )

        if old_fabrics and include_recipe:
            await self._assign_old_recipe_to_fabrics(
                fabrics=old_fabrics,
                include_yarn_instance=include_yarn_instance_to_recipe,
            )

        for fabric in fabrics:
            fabric.purchase_description = purchase_description_mapping[fabric.id]

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
            await self.yarn_service.read_yarns_by_ids(yarn_ids=list(yarn_ids))
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
