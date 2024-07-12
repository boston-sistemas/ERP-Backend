
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import transactional
from src.core.result import Result, Success
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


class OrdenServicioTintoreriaService:
    def __init__(self, db: AsyncSession) -> None:
        self.repository = OrdenServicioTintoreriaRepository(db)
        self.suborden_repository = OrdenServicioTintoreriaDetalleRepository(db)

    @transactional
    async def create_orden_with_detalle(
        self, orden: OrdenServicioTintoreriaCreateSchemaWithDetalle
    ) -> Result[None, None]:
        instance = OrdenServicioTintoreria(**orden.model_dump(exclude={"detalle"}))
        await self.repository.save(instance)
        subordenes = [
            OrdenServicioTintoreriaDetalleCreateSchema(
                orden_servicio_tintoreria_id=instance.orden_servicio_tintoreria_id,
                **suborden.model_dump(),
            )
            for suborden in orden.detalle
        ]

        await self.detalle_service.create_subordenes(subordenes)
        return Success(None)

    @transactional
    async def create_ordenes_with_detalle(
        self, ordenes: list[OrdenServicioTintoreriaCreateSchemaWithDetalle]
    ) -> Result[None, None]:
        order_instances = [
            OrdenServicioTintoreria(**orden.model_dump(exclude={"detalle"}))
            for orden in ordenes
        ]
        await self.repository.save_all(order_instances)

        suborder_instances = [
            OrdenServicioTintoreriaDetalle(
                orden_servicio_tintoreria_id=order_instance.orden_servicio_tintoreria_id,
                **suborden.model_dump(),
            )
            for order_instance, orden in zip(order_instances, ordenes)
            for suborden in orden.detalle
        ]
        await self.suborden_repository.save_all(suborder_instances)

        return Success(None)
