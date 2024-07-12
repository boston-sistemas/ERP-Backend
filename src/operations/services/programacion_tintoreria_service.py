from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import transactional
from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.operations.models import ProgramacionTintoreria
from src.operations.repositories import ProgramacionTintoreriaRepository
from src.operations.schemas import (
    OrdenServicioTintoreriaCreateSchemaWithDetalle,
    ProgramacionTintoreriaCreateSchema,
    ProgramacionTintoreriaParametersResponse,
)
from src.operations.services import OrdenServicioTintoreriaService

from .color_service import ColorService
from .proveedor_service import ProveedorService


class ProgramacionTintoreriaService:
    def __init__(self, db: AsyncSession) -> None:
        self.repository = ProgramacionTintoreriaRepository(db)
        self.proveedor_service = ProveedorService(db)
        self.color_service = ColorService(db)
        self.orden_service = OrdenServicioTintoreriaService(db)

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

    @transactional
    async def create_programacion(
        self, programacion: ProgramacionTintoreriaCreateSchema
    ) -> Result[None, CustomException]:
        tejeduria_result = await self.proveedor_service.read_proveedor(
            proveedor_id=programacion.from_tejeduria_id
        )

        if tejeduria_result.is_failure:
            return tejeduria_result

        tintoreria_result = await self.proveedor_service.read_proveedor(
            proveedor_id=programacion.to_tintoreria_id
        )

        if tintoreria_result.is_failure:
            return tintoreria_result

        # tejeduria, tintoreria = tejeduria_result.value, tintoreria_result.value

        instance = ProgramacionTintoreria(
            from_tejeduria_id=programacion.from_tejeduria_id,
            to_tintoreria_id=programacion.to_tintoreria_id,
        )
        await self.repository.save(instance)

        ordenes = [
            OrdenServicioTintoreriaCreateSchemaWithDetalle(
                programacion_tintoreria_id=instance.id,
                estado="PROGRAMADO",
                **partida.model_dump(),
            )
            for partida in programacion.partidas
        ]

        await self.orden_service.create_ordenes_with_detalle(ordenes=ordenes)

        return Success(None)
