from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.operations.models import SupplierColor

from .supplier_color_failures import SupplierColorFailures
from .supplier_color_repository import SupplierColorRepository
from .supplier_color_schema import SupplierColorListSchema, SupplierColorSchema


class SupplierColorService:
    def __init__(self, promec_db: AsyncSession) -> None:
        self.promec_db = promec_db
        self.repository = SupplierColorRepository(promec_db=promec_db)

    async def read_supplier_colors_by_suppliers(
        self,
        supplier_id: str,
    ) -> Result[SupplierColorListSchema, CustomException]:
        supplier_colors = await self.repository.find_supplier_colors_by_suppliers(
            supplier_id=supplier_id
        )
        return Success(SupplierColorListSchema(supplier_colors=supplier_colors))

    async def _read_supplier_color(
        self,
        id: str,
        include_color: bool = False,
    ) -> Result[SupplierColor, CustomException]:
        supplier_color = await self.repository.find_supplier_color_by_id(
            id=id,
        )
        if supplier_color is None:
            return SupplierColorFailures.SUPPLIER_COLOR_NOT_FOUND_FAILURE

        return Success(supplier_color)

    async def read_supplier_color(
        self, id: str
    ) -> Result[SupplierColorSchema, CustomException]:
        supplier_color = await self._read_supplier_color(
            id=id,
        )

        if supplier_color.is_failure:
            return supplier_color

        supplier_color = supplier_color.value

        return Success(SupplierColorSchema.model_validate(supplier_color))
