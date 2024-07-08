from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.operations.failures import OrdenServicioTejeduriaDetalleFailures
from src.operations.models import OrdenServicioTejeduriaDetalle
from src.operations.repositories import OrdenServicioTejeduriaDetalleRepository
from src.operations.schemas import OrdenServicioTejeduriaDetalleUpdateSchemaByID


class OrdenServicioTejeduriaDetalleService:
    def __init__(self, db: AsyncSession) -> None:
        self.repository = OrdenServicioTejeduriaDetalleRepository(db)

    async def read_suborden(
        self, orden_id: str, crudo_id: str
    ) -> Result[OrdenServicioTejeduriaDetalle, CustomException]:
        suborden = await self.repository.find_suborden(
            filter=(
                OrdenServicioTejeduriaDetalle.orden_servicio_tejeduria_id == orden_id
            )
            & (OrdenServicioTejeduriaDetalle.crudo_id == crudo_id)
        )

        if suborden is not None:
            return Success(suborden)

        return OrdenServicioTejeduriaDetalleFailures.SUBORDER_NOT_FOUND_FAILURE

    async def update_subordenes(
        self, subordenes: list[OrdenServicioTejeduriaDetalleUpdateSchemaByID]
    ) -> Result[None, CustomException]:
        instances: list[OrdenServicioTejeduriaDetalle] = []

        for suborden in subordenes:
            suborden_result = await self.read_suborden(
                suborden.orden_servicio_tejeduria_id, suborden.crudo_id
            )
            if suborden_result.is_failure:
                return OrdenServicioTejeduriaDetalleFailures.SUBORDER_NOT_FOUND_WHEN_UPDATING_MULTIPLE_SUBORDERS_FAILURE

            instance: OrdenServicioTejeduriaDetalle = suborden_result.value
            update_data = suborden.model_dump(
                exclude={"orden_servicio_tejeduria_id", "crudo_id"}, exclude_none=True
            )

            for key, value in update_data.items():
                setattr(instance, key, value)

            instances.append(instance)

        await self.repository.save_all(instances)
        return Success(None)
