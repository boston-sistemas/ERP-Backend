from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result
from src.operations.schemas import (
    OrdenServicioTejeduriaUpdateSchemaByID,
    RevisionStockTejeduriaResponse,
)

from .orden_servicio_tejeduria_service import (
    OrdenServicioTejeduriaService,
)


class RevisionStockTejeduriaService:
    def __init__(self, db: AsyncSession) -> None:
        self.orden_tejeduria_service = OrdenServicioTejeduriaService(db)

    async def retrieve_ordenes_pendientes_and_cerradas(
        self,
    ) -> RevisionStockTejeduriaResponse:
        ordenes_pendientes = await self.orden_tejeduria_service.read_ordenes_by_estado(
            estado="PENDIENTE", include_detalle=True, include_proveedor=True
        )

        ordenes_cerradas = await self.orden_tejeduria_service.read_ordenes_by_estado(
            estado="CERRADO", include_detalle=True, include_proveedor=True
        )

        return RevisionStockTejeduriaResponse(
            ordenes_pendientes=ordenes_pendientes, ordenes_cerradas=ordenes_cerradas
        )

    async def update_ordenes_estado(
        self, ordenes: list[OrdenServicioTejeduriaUpdateSchemaByID]
    ) -> Result[None, CustomException]:
        return await self.orden_tejeduria_service.update_ordenes(ordenes=ordenes)
