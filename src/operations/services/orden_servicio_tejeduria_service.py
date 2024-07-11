from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.operations.failures import OrdenServicioTejeduriaFailures
from src.operations.models import OrdenServicioTejeduria
from src.operations.repositories import OrdenServicioTejeduriaRepository
from src.operations.schemas import OrdenServicioTejeduriaUpdateSchemaByID


class OrdenServicioTejeduriaService:
    def __init__(self, db: AsyncSession) -> None:
        self.repository = OrdenServicioTejeduriaRepository(db)

    async def read_orden(
        self,
        orden_id: str,
        include_detalle: bool = False,
        include_proveedor: bool = False,
    ) -> Result[OrdenServicioTejeduria, CustomException]:
        orden = await self.repository.find_orden(
            OrdenServicioTejeduria.orden_servicio_tejeduria_id == orden_id,
            include_detalle=include_detalle,
            include_proveedor=include_proveedor,
        )

        if orden is not None:
            return Success(orden)

        return OrdenServicioTejeduriaFailures.ORDEN_NOT_FOUND_FAILURE

    async def read_ordenes(
        self, include_detalle: bool = False, include_proveedor: bool = False
    ) -> list[OrdenServicioTejeduria]:
        return await self.repository.find_ordenes(
            include_detalle=include_detalle, include_proveedor=include_proveedor
        )

    async def read_ordenes_by_tejeduria_and_estado(
        self,
        tejeduria_id: str,
        estado: str,
        include_detalle: bool = False,
        include_proveedor: bool = False,
    ) -> list[OrdenServicioTejeduria]:
        return await self.repository.find_ordenes(
            filter=(OrdenServicioTejeduria.tejeduria_id == tejeduria_id)
            & (OrdenServicioTejeduria.estado == estado),
            include_detalle=include_detalle,
            include_proveedor=include_proveedor,
        )

    async def read_ordenes_by_estado(
        self,
        estado: str,
        include_detalle: bool = False,
        include_proveedor: bool = False,
    ) -> list[OrdenServicioTejeduria]:
        return await self.repository.find_ordenes(
            filter=OrdenServicioTejeduria.estado == estado,
            include_detalle=include_detalle,
            include_proveedor=include_proveedor,
        )

    async def update_ordenes(
        self, ordenes: list[OrdenServicioTejeduriaUpdateSchemaByID]
    ) -> Result[None, CustomException]:
        instances: list[OrdenServicioTejeduria] = []

        for orden in ordenes:
            orden_result = await self.read_orden(orden.orden_servicio_tejeduria_id)
            if orden_result.is_failure:
                return OrdenServicioTejeduriaFailures.ORDEN_NOT_FOUND_WHEN_UPDATING_MULTIPLE_ORDERS_FAILURE

            instance: OrdenServicioTejeduria = orden_result.value
            update_data = orden.model_dump(
                exclude={"orden_servicio_tejeduria_id"}, exclude_none=True
            )

            for key, value in update_data.items():
                setattr(instance, key, value)

            instances.append(instance)

        await self.repository.save_all(instances)
        return Success(None)
