from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import transactional
from src.core.result import Result, Success
from src.operations.failures import OrdenServicioTintoreriaFailures
from src.operations.models import (
    OrdenServicioTintoreria,
    OrdenServicioTintoreriaDetalle,
)
from src.operations.repositories import (
    OrdenServicioTintoreriaDetalleRepository,
    OrdenServicioTintoreriaRepository,
)
from src.operations.schemas import (
    OrdenServicioTintoreriaCreateSchemaWithDetalle,
    OrdenServicioTintoreriaDetalleCreateSchema,
)

from .color_service import ColorService


class OrdenServicioTintoreriaService:
    def __init__(self, db: AsyncSession) -> None:
        self.repository = OrdenServicioTintoreriaRepository(db)
        self.suborden_repository = OrdenServicioTintoreriaDetalleRepository(db)
        self.color_service = ColorService(db)

    @transactional
    async def create_orden_with_detalle(
        self, orden: OrdenServicioTintoreriaCreateSchemaWithDetalle
    ) -> Result[None, None]:
        instance = OrdenServicioTintoreria(**orden.model_dump(exclude={"detail"}))
        await self.repository.save(instance)
        subordenes = [
            OrdenServicioTintoreriaDetalleCreateSchema(
                orden_servicio_tintoreria_id=instance.orden_servicio_tintoreria_id,
                **suborden.model_dump(),
            )
            for suborden in orden.detail
        ]

        await self.detalle_service.create_subordenes(subordenes)
        return Success(None)

    @transactional
    async def create_ordenes_with_detalle(
        self, ordenes: list[OrdenServicioTintoreriaCreateSchemaWithDetalle]
    ) -> Result[None, None]:
        for color_id in {orden.color_id for orden in ordenes}:
            result = await self.color_service.read_color(color_id)
            if result.is_failure:
                return OrdenServicioTintoreriaFailures.COLOR_NOT_FOUND_WHEN_CREATING_MULTIPLE_ORDERS_FAILURE

        order_instances = [
            OrdenServicioTintoreria(**orden.model_dump(exclude={"detail"}))
            for orden in ordenes
        ]
        await self.repository.save_all(order_instances)

        suborder_instances = [
            OrdenServicioTintoreriaDetalle(
                orden_servicio_tintoreria_id=order_instance.orden_servicio_tintoreria_id,
                **suborden.model_dump(),
            )
            for order_instance, orden in zip(order_instances, ordenes)
            for suborden in orden.detail
        ]
        await self.suborden_repository.save_all(suborder_instances)

        return Success(None)
