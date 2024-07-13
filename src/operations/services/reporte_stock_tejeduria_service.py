from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.operations.schemas import (
    OrdenServicioTejeduriaDetalleStockUpdateSchemaByID,
    OrdenServicioTejeduriaDetalleUpdateSchemaByID,
    ReporteStockTejeduriaResponse,
)
from src.security.services import UserService

from .orden_servicio_tejeduria_detalle_service import (
    OrdenServicioTejeduriaDetalleService,
)
from .orden_servicio_tejeduria_service import OrdenServicioTejeduriaService


class ReporteStockTejeduriaService:
    def __init__(self, db: AsyncSession) -> None:
        self.user_service = UserService(db)
        self.orden_tejeduria_service = OrdenServicioTejeduriaService(db)
        self.suborden_tejeduria_service = OrdenServicioTejeduriaDetalleService(db)

    async def retrieve_ordenes_pendientes_by_tejeduria(
        self, user_id: int
    ) -> Result[ReporteStockTejeduriaResponse, CustomException]:
        # result = self.user_service.retrieve_supplier_id(user_id)
        # if result.is_failure:
        # return ReporteServicioFailures.SUPPLIER_ID_NOT_FOUND_WHEN_RETRIEVING_ORDENES_TEJEDURIA_FAILURE
        # tejeduria_id: str = result.value
        tejeduria_id: str = "P006"
        ordenes = (
            await self.orden_tejeduria_service.read_ordenes_by_tejeduria_and_estado(
                tejeduria_id=tejeduria_id,
                estado="PENDIENTE",
                include_detalle=True,
            )
        )

        return Success(ReporteStockTejeduriaResponse(ordenes=ordenes))

    async def update_subordenes_stock(
        self, subordenes: list[OrdenServicioTejeduriaDetalleStockUpdateSchemaByID]
    ) -> Result[None, CustomException]:
        _subordenes = [
            OrdenServicioTejeduriaDetalleUpdateSchemaByID(**suborden.model_dump())
            for suborden in subordenes
        ]
        return await self.suborden_tejeduria_service.update_subordenes(_subordenes)
