from sqlalchemy.ext.asyncio import AsyncSession

from src.core.result import Result, Success
from src.operations.models import MovimientoIngresoCrudo
from src.operations.repositories import (
    MovimientoIngresoCrudoRepository,
    OrdenServicioTejeduriaDetalleRepository,
)
from src.operations.schemas import MovimientoIngresoCrudoCreateSchema

from .orden_servicio_tejeduria_detalle_service import (
    OrdenServicioTejeduriaDetalleService,
)


class MovimientoIngresoCrudoService:
    def __init__(self, db: AsyncSession) -> None:
        self.repository = MovimientoIngresoCrudoRepository(db)
        self.suborden_tejeduria_repository = OrdenServicioTejeduriaDetalleRepository(db)
        self.suborden_tejeduria_service = OrdenServicioTejeduriaDetalleService(db)

    async def _get_subordenes_tejeduria(
        self, movimientos: list[MovimientoIngresoCrudoCreateSchema]
    ):
        mapping = dict()
        suborden_ids = {
            (movimiento.orden_servicio_tejeduria_id, movimiento.crudo_id)
            for movimiento in movimientos
        }

        for suborden_id in suborden_ids:
            mapping[suborden_id] = (
                await self.suborden_tejeduria_service.read_suborden(*suborden_id)
            ).value

        return mapping

    async def create_movimientos(
        self, movimientos: list[MovimientoIngresoCrudoCreateSchema]
    ) -> Result[None, None]:
        subordenes = await self._get_subordenes_tejeduria(movimientos)
        for movimiento in movimientos:
            suborden_id = (movimiento.orden_servicio_tejeduria_id, movimiento.crudo_id)
            subordenes[suborden_id].consumido_kg += movimiento.cantidad_kg
            await self.repository.save(
                MovimientoIngresoCrudo(**movimiento.model_dump())
            )

        self.suborden_tejeduria_repository.save_all(subordenes.values())
        return Success(None)
