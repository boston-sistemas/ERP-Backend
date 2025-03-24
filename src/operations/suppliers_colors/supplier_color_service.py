from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.operations.models import SupplierColor

from .supplier_color_failures import SupplierColorFailures
from .supplier_color_repository import SupplierColorRepository
from .supplier_color_schema import SupplierColorSchema


class SupplierColorService:
    def __init__(self, promec_db: AsyncSession) -> None:
        self.promec_db = promec_db
        self.repository = SupplierColorRepository(promec_db=promec_db)

    # async def read_supplier_color(
    #     self,
    #     supplier_id: str,
    # ) -> Result[SupplierColor, CustomException]:
    #     supplier_color = await self.repository.find_supplier_color_by_id(
    #         supplier_id=supplier_id
    #     )
    #     if supplier_color:
    #         return Success(supplier_color)
    #     return SUPPLIER_COLOR_NOT_FOUND_FAILURE

    async def read_supplier_colors(
        self,
    ) -> Result[list[SupplierColorSchema], CustomException]:
        supplier_colors = await self.repository.find_all()
        return Success(supplier_colors)

    async def _read_supplier_color(
        self,
        supplier_id: str,
        id: str,
        include_color: bool = False,
    ) -> Result[SupplierColor, CustomException]:
        supplier_color = await self.repository.find_supplier_color_by_id(
            supplier_id=supplier_id,
            id=id,
        )
        if supplier_color is None:
            return SupplierColorFailures.SUPPLIER_COLOR_NOT_FOUND_FAILURE

        return Success(supplier_color)

    async def read_supplier_color(
        self, supplier_id: str, id: str
    ) -> Result[SupplierColorSchema, CustomException]:
        supplier_color = await self._read_supplier_color(
            supplier_id=supplier_id,
            id=id,
        )

        if supplier_color.is_failure:
            return supplier_color

        supplier_color = supplier_color.value

        return Success(SupplierColorSchema.model_validate(supplier_color))
