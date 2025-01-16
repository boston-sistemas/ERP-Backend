from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.operations.failures import (
    YARN_PURCHASE_ENTRY_DETAIL_HEAVY_NOT_FOUND_FAILURE,
)
from src.operations.models import (
    MovementYarnOCHeavy,
)
from src.operations.repositories import YarnPurchaseEntryDetailHeavyRepository
from src.operations.schemas import (
    YarnPurchaseEntryDetailHeavyListSchema,
    YarnPurchaseEntryDetailHeavySchema,
)


class YarnPurchaseEntryDetailHeavyService:
    def __init__(self, promec_db: AsyncSession) -> None:
        self.promec_db = promec_db
        self.repository = YarnPurchaseEntryDetailHeavyRepository(promec_db)

    async def _read_yarn_purchase_entry_detail_heavy(
        self,
        ingress_number: str,
        item_number: int,
        group_number: int,
        period: int,
        include_entry_movement: bool = False,
        include_entry_movement_detail: bool = False,
        include_entry_movement_detail_heavy: bool = False,
    ) -> Result[MovementYarnOCHeavy, CustomException]:
        yarn_purchase_entry_detail_heavy = await self.repository.find_yarn_purchase_entry_detail_heavy_by_ingress_number_and_item_and_group(
            ingress_number=ingress_number,
            item_number=item_number,
            group_number=group_number,
            period=period,
            include_entry_movement=include_entry_movement,
            include_entry_movement_detail=include_entry_movement_detail,
            include_entry_movement_detail_heavy=include_entry_movement_detail_heavy,
        )

        if yarn_purchase_entry_detail_heavy is None:
            return YARN_PURCHASE_ENTRY_DETAIL_HEAVY_NOT_FOUND_FAILURE

        return Success(yarn_purchase_entry_detail_heavy)

    async def read_yarn_purchase_entry_detail_heavy(
        self,
        ingress_number: str,
        item_number: int,
        group_number: int,
        period: int,
    ) -> Result[MovementYarnOCHeavy, CustomException]:
        yarn_purchase_entry_detail_heavy_result = (
            await self._read_yarn_purchase_entry_detail_heavy(
                ingress_number=ingress_number,
                item_number=item_number,
                group_number=group_number,
                period=period,
            )
        )

        if yarn_purchase_entry_detail_heavy_result.is_failure:
            return yarn_purchase_entry_detail_heavy_result

        return Success(
            YarnPurchaseEntryDetailHeavySchema.model_validate(
                yarn_purchase_entry_detail_heavy_result.value
            )
        )

    async def rollback_yarn_purchase_entry_detail_heavy_by_yarn_dispatch(
        self,
        package_count: int,
        cone_count: int,
        item_number: int,
        group_number: int,
        entry_number: int,
        period: int,
    ) -> Result[None, CustomException]:
        yarn_purchase_entry_detail_heavy_result = (
            await self._read_yarn_purchase_entry_detail_heavy(
                ingress_number=entry_number,
                item_number=item_number,
                group_number=group_number,
                period=period,
                include_entry_movement=True,
                include_entry_movement_detail=True,
                include_entry_movement_detail_heavy=True,
            )
        )
        if yarn_purchase_entry_detail_heavy_result.is_failure:
            return yarn_purchase_entry_detail_heavy_result

        yarn_purchase_entry_detail_heavy: MovementYarnOCHeavy = (
            yarn_purchase_entry_detail_heavy_result.value
        )

        if yarn_purchase_entry_detail_heavy is None:
            return YARN_PURCHASE_ENTRY_DETAIL_HEAVY_NOT_FOUND_FAILURE

        yarn_purchase_entry_detail_heavy.packages_left += package_count
        yarn_purchase_entry_detail_heavy.cones_left += cone_count

        if (
            yarn_purchase_entry_detail_heavy.packages_left > 0
            or yarn_purchase_entry_detail_heavy.cones_left > 0
        ):
            yarn_purchase_entry_detail_heavy.status_flag = "P"
            yarn_purchase_entry_detail_heavy.dispatch_status = False

        if (
            yarn_purchase_entry_detail_heavy.packages_left
            == yarn_purchase_entry_detail_heavy.package_count
        ) and (
            yarn_purchase_entry_detail_heavy.cones_left
            == yarn_purchase_entry_detail_heavy.cone_count
        ):
            yarn_purchase_entry_detail_heavy.exit_number = None
            yarn_purchase_entry_detail_heavy.exit_user_id = None

        movement = yarn_purchase_entry_detail_heavy.movement

        count_detail_supplied = 0
        for detail in movement.detail:
            count_heavy_supplied = 0
            count_package_supplied = 0
            for heavy in detail.detail_heavy:
                if heavy.status_flag == "C":
                    count_heavy_supplied += 1

                if heavy.dispatch_status:
                    count_package_supplied += heavy.package_count

            if (
                count_heavy_supplied != len(detail.detail_heavy)
                or count_package_supplied != detail.detail_aux.guide_package_count
            ):
                detail.status_flag = "P"

            if detail.status_flag == "P":
                count_detail_supplied += 1

        if count_detail_supplied != len(movement.detail):
            movement.status_flag = "P"

        await self.repository.save(yarn_purchase_entry_detail_heavy)
        return Success(None)

    async def update_yarn_purchase_entry_detail_heavy_by_yarn_dispatch(
        self,
        package_count: int,
        cone_count: int,
        dispatch_number: str,
        item_number: int,
        group_number: int,
        entry_number: int,
        period: int,
    ) -> Result[None, CustomException]:
        self.repository.expunge_all()
        yarn_purchase_entry_detail_heavy_result = (
            await self._read_yarn_purchase_entry_detail_heavy(
                ingress_number=entry_number,
                item_number=item_number,
                group_number=group_number,
                period=period,
                include_entry_movement=True,
                include_entry_movement_detail=True,
                include_entry_movement_detail_heavy=True,
            )
        )

        if yarn_purchase_entry_detail_heavy_result.is_failure:
            return yarn_purchase_entry_detail_heavy_result

        yarn_purchase_entry_detail_heavy: MovementYarnOCHeavy = (
            yarn_purchase_entry_detail_heavy_result.value
        )

        if yarn_purchase_entry_detail_heavy is None:
            return YARN_PURCHASE_ENTRY_DETAIL_HEAVY_NOT_FOUND_FAILURE

        yarn_purchase_entry_detail_heavy.packages_left -= package_count
        yarn_purchase_entry_detail_heavy.cones_left -= cone_count

        if (
            yarn_purchase_entry_detail_heavy.packages_left == 0
            and yarn_purchase_entry_detail_heavy.cones_left == 0
        ):
            yarn_purchase_entry_detail_heavy.status_flag = "C"
            yarn_purchase_entry_detail_heavy.dispatch_status = True

        yarn_purchase_entry_detail_heavy.exit_number = dispatch_number
        yarn_purchase_entry_detail_heavy.exit_user_id = "DESA01"

        movement = yarn_purchase_entry_detail_heavy.movement

        count_detail_supplied = 0
        for detail in movement.detail:
            count_heavy_supplied = 0
            count_package_supplied = 0
            for heavy in detail.detail_heavy:
                if heavy.status_flag == "C":
                    count_heavy_supplied += 1

                if heavy.dispatch_status:
                    count_package_supplied += heavy.package_count

            if (
                count_heavy_supplied == len(detail.detail_heavy)
                and count_package_supplied == detail.detail_aux.guide_package_count
            ):
                detail.status_flag = "C"

            if detail.status_flag == "C":
                count_detail_supplied += 1

        if count_detail_supplied == len(movement.detail):
            movement.status_flag = "C"

        await self.repository.save(yarn_purchase_entry_detail_heavy)
        return Success(None)

    async def read_yarn_purchase_entries_item_group_availability(
        self,
        period: int,
    ) -> Result[YarnPurchaseEntryDetailHeavyListSchema, CustomException]:
        yarn_purchase_entries_detail_heavy_result = (
            await self.repository.find_yarn_purchase_entries_items_groups_availability(
                period=period,
                include_detail_entry=True,
            )
        )

        return Success(
            YarnPurchaseEntryDetailHeavyListSchema(
                yarn_purchase_entries_detail_heavy=yarn_purchase_entries_detail_heavy_result
            )
        )
