from enum import Enum
from sqlmodel import Field, SQLModel

from mecsa_erp.area_operaciones.modulo0.schemas.orden_servicio_tejeduria import (
    OrdenServicioTejeduriaSchema,
)
from mecsa_erp.area_operaciones.modulo0.schemas.orden_servicio_tejeduria_detalle import (
    OrdenServicioTejeduriaDetalleSchema,
)


class ReporteStock(SQLModel):
    subordenes: list[OrdenServicioTejeduriaDetalleSchema]


class RevisionStock(SQLModel):
    ordenes_pendientes: list[OrdenServicioTejeduriaSchema]
    ordenes_cerradas: list[OrdenServicioTejeduriaSchema]


class OrdenServicioTejeduriaEstadoEnum(str, Enum):
    pendiente = "PENDIENTE"
    cerrado = "CERRADO"
    liquidado = "LIQUIDADO"


class OrdenServicioTejeduriaDetalleEstadoEnum(str, Enum):
    no_iniciado = "NO INICIADO"
    cerrado = "EN CURSO"
    liquidado = "DETENIDO"
    listo = "LISTO"


class OrdenServicioTejeduriaIDSchema(SQLModel):
    orden_servicio_tejeduria_id: str
    crudo_id: str


class OrdenServicioTejeduriaDetalleUpdateSchema(SQLModel):
    reporte_tejeduria_nro_rollos: int | None = Field(default=None, ge=0)
    reporte_tejeduria_cantidad_kg: float | None = Field(default=None, ge=0)
    estado: OrdenServicioTejeduriaDetalleEstadoEnum | None = None


class OrdenServicioTejeduriaSchema(
    OrdenServicioTejeduriaDetalleUpdateSchema, OrdenServicioTejeduriaIDSchema
):
    pass


class OrdenServicioTejeduriaDetalleListUpdateSchema(SQLModel):
    subordenes: list[OrdenServicioTejeduriaSchema]


class OrdenServicioTejeduriaUpdateSchema(SQLModel):
    orden_servicio_tejeduria_id: str
    estado: OrdenServicioTejeduriaEstadoEnum
