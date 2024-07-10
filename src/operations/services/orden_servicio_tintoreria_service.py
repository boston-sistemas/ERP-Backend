import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.result import Result, Success
from src.operations.models import OrdenServicioTintoreria
from src.operations.repositories import OrdenServicioTintoreriaRepository
from src.operations.schemas import (
    OrdenServicioTintoreriaCreateSchemaWithDetalle,
    OrdenServicioTintoreriaDetalleCreateSchema,
)

from .orden_servicio_tintoreria_detalle_service import (
    OrdenServicioTintoreriaDetalleService,
)


class OrdenServicioTintoreriaService:
    def __init__(self, db: AsyncSession) -> None:
        self.repository = OrdenServicioTintoreriaRepository(db)
        self.detalle_service = OrdenServicioTintoreriaDetalleService(db)

    def _create_orden_with_detalle_in_single_commit(func):
        async def wrapper(self, *args, **kwargs):
            self.repository.commit = False
            self.repository.flush = True
            # TODO: reiniciar los valores?
            return await func(self, *args, **kwargs)

        return wrapper

    @_create_orden_with_detalle_in_single_commit
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

    def _create_ordenes_with_detalle_in_single_commit(func):
        async def wrapper(self, *args, **kwargs):
            self.detalle_service.commit = False
            # TODO: reiniciar los valores?
            result = await func(self, *args, **kwargs)
            if self.repository.commit:
                self.repository.db.commit()
            return result

        return wrapper

    @_create_ordenes_with_detalle_in_single_commit
    async def create_ordenes_with_detalle(
        self, ordenes: list[OrdenServicioTintoreriaCreateSchemaWithDetalle]
    ) -> Result[None, None]:
        instances = [
            OrdenServicioTintoreria(**orden.model_dump(exclude={"detalle"}))
            for orden in ordenes
        ]
        await self.repository.save_all(instances)

        await asyncio.gather(
            *(self.create_orden_with_detalle(orden) for orden in ordenes)
        )
        return Success(None)
