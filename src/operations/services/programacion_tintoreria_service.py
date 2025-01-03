from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import transactional
from src.core.exceptions import CustomException
from src.core.result import Result, Success
from src.core.services import EmailService
from src.operations.models import (
    OrdenServicioTejeduria,
    ProgramacionTintoreria,
    Proveedor,
)
from src.operations.repositories import (
    ColorRepository,
    OrdenServicioTejeduriaDetalleRepository,
    ProgramacionTintoreriaRepository,
)
from src.operations.schemas import (
    OrdenServicioTintoreriaCreateSchemaWithDetalle,
    ProgramacionTintoreriaCreateSchema,
    ProgramacionTintoreriaParametersResponse,
)
from src.operations.services import OrdenServicioTintoreriaService
from src.operations.utils.programacion_tintoreria import generate_pdf

from .orden_servicio_tejeduria_detalle_service import (
    OrdenServicioTejeduriaDetalleService,
)
from .orden_servicio_tejeduria_service import OrdenServicioTejeduriaService
from .proveedor_service import ProveedorService


class ProgramacionTintoreriaService:
    def __init__(self, db: AsyncSession) -> None:
        self.repository = ProgramacionTintoreriaRepository(db)
        self.color_repository = ColorRepository(db)
        self.proveedor_service = ProveedorService(db)
        self.orden_service = OrdenServicioTintoreriaService(db)
        self.email_service = EmailService()
        self.orden_tejeduria_service = OrdenServicioTejeduriaService(db)
        self.suborden_tejeduria_service = OrdenServicioTejeduriaDetalleService(db)
        self.suborden_tejeduria_repository = OrdenServicioTejeduriaDetalleRepository(db)

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

        colores = await self.color_repository.find_all()
        return Success(
            ProgramacionTintoreriaParametersResponse(
                tejedurias=tejedurias_result.value,
                tintorerias=tintorerias_result.value,
                colores=colores,
            )
        )

    async def get_current_stock_by_tejeduria(
        self, tejeduria_id: str
    ) -> list[OrdenServicioTejeduria]:
        ordenes = (
            await self.orden_tejeduria_service.read_ordenes_by_tejeduria_and_estado(
                tejeduria_id=tejeduria_id, estado="PENDIENTE", include_detalle=True
            )
        )
        return ordenes

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

        tejeduria, tintoreria = tejeduria_result.value, tintoreria_result.value

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
        await self._update_subordenes_stock(programacion.partidas)
        creation_result = await self.orden_service.create_ordenes_with_detalle(
            ordenes=ordenes
        )
        if creation_result.is_failure:
            return creation_result

        await self._send_email(tejeduria, tintoreria, programacion.partidas)
        return Success(None)

    async def _get_subordenes_tejeduria(self, partidas):
        mapping = dict()
        suborden_ids = {
            (suborden.orden_servicio_tejeduria_id, suborden.crudo_id)
            for partida in partidas
            for suborden in partida.detail
        }

        for suborden_id in suborden_ids:
            mapping[suborden_id] = (
                await self.suborden_tejeduria_service.read_suborden(*suborden_id)
            ).value

        return mapping

    async def _update_subordenes_stock(self, partidas):
        subordenes = await self._get_subordenes_tejeduria(partidas)
        for partida in partidas:
            for suborden in partida.detail:
                suborden_id = (suborden.orden_servicio_tejeduria_id, suborden.crudo_id)
                subordenes[
                    suborden_id
                ].reporte_tejeduria_nro_rollos -= suborden.nro_rollos
                subordenes[suborden_id].reporte_tejeduria_cantidad_kg -= float(
                    suborden.cantidad_kg
                )

        await self.suborden_tejeduria_repository.save_all(subordenes.values())

    async def _retrieve_colores(self, color_ids: set):
        mapping = dict()
        for color_id in color_ids:
            mapping[color_id] = await self.color_repository.find_by_id(color_id)

        return mapping

    async def _generate_table(self, partidas, colores, headers):
        table = [
            [
                str(index),
                suborden.orden_servicio_tejeduria_id,
                suborden.crudo_id[:3],
                suborden.crudo_id[-2:],
                str(suborden.nro_rollos),
                str(suborden.cantidad_kg),
                colores[partida.color_id].nombre,
            ]
            for index, partida in enumerate(partidas, start=1)
            for suborden in partida.detail
        ]

        table.insert(0, headers)
        return table

    async def _send_email(
        self, tejeduria: Proveedor, tintoreria: Proveedor, partidas, comment=None
    ):
        colores = await self._retrieve_colores(
            color_ids={partida.color_id for partida in partidas}
        )
        partidas_size = len(partidas)

        values = await self._generate_table(
            partidas,
            colores,
            [
                "Partida",
                "O.S.",
                "Tejido",
                "Ancho",
                "Rollos",
                "Peso",
                "Color",
            ],
        )

        pdf = generate_pdf(tejeduria, tintoreria, comment, partidas_size, values)

        await self.email_service.send_programacion_tintoreria_email(
            pdf,
            tejeduria,
            tintoreria,
            values,
            email_from="practicante.sistemas@boston.com.pe",
            email_to=["practicante.sistemas@boston.com.pe"],
        )
