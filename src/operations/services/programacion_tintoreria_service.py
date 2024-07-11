from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.operations.schemas import ProgramacionTintoreriaParametersResponse

from .color_service import ColorService
from .proveedor_service import ProveedorService


class ProgramacionTintoreriaService:
    def __init__(self, db: AsyncSession) -> None:
        self.proveedor_service = ProveedorService(db)
        self.color_service = ColorService(db)

    async def retrieve_parameters(
        self,
    ) -> Result[ProgramacionTintoreriaParametersResponse, CustomException]:
        tejedurias_result = (
            await self.proveedor_service.read_proveedores_by_especialidad("TEJEDURIA")
        )

        if tejedurias_result.is_failure:
            return tejedurias_result

        tintorerias_result = (
            await self.proveedor_service.read_proveedores_by_especialidad("TINTORERIA")
        )

        if tintorerias_result.is_failure:
            return tintorerias_result

        colores = await self.color_service.read_colores()
        return Success(
            ProgramacionTintoreriaParametersResponse(
                tejedurias=tejedurias_result.value,
                tintorerias=tintorerias_result.value,
                colores=colores,
            )
        )
