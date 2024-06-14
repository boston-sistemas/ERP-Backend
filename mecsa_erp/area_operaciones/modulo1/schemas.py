from datetime import datetime
from enum import Enum
from sqlmodel import Field, SQLModel

from mecsa_erp.area_operaciones.modulo0.schemas.orden_servicio_tejeduria import (
    OrdenServicioTejeduriaSchema,
)


class ReporteStock(SQLModel):
    ordenes: list[OrdenServicioTejeduriaSchema]


class RevisionStock(SQLModel):
    ordenes_pendientes: list[OrdenServicioTejeduriaSchema]
    ordenes_cerradas: list[OrdenServicioTejeduriaSchema]


#############################################################


class OrdenServicioTejeduriaDetalleEstadoEnum(str, Enum):
    no_iniciado = "NO INICIADO"
    cerrado = "EN CURSO"
    liquidado = "DETENIDO"
    listo = "LISTO"


class OrdenServicioTejeduriaDetalleIDSchema(SQLModel):
    orden_servicio_tejeduria_id: str
    crudo_id: str


class OrdenServicioTejeduriaDetalleUpdateSchema(SQLModel):
    reporte_tejeduria_nro_rollos: int | None = Field(default=None, ge=0)
    reporte_tejeduria_cantidad_kg: float | None = Field(default=None, ge=0)
    estado: OrdenServicioTejeduriaDetalleEstadoEnum | None = None


class OrdenServicioTejeduriaDetalleUpdateSchemaByID(
    OrdenServicioTejeduriaDetalleUpdateSchema, OrdenServicioTejeduriaDetalleIDSchema
):
    pass


class OrdenServicioTejeduriaDetalleListUpdateSchema(SQLModel):
    subordenes: list[OrdenServicioTejeduriaDetalleUpdateSchemaByID]


#############################################################


class OrdenServicioTejeduriaEstadoEnum(str, Enum):
    pendiente = "PENDIENTE"
    cerrado = "CERRADO"
    liquidado = "LIQUIDADO"


class OrdenServicioTejeduriaIDSchema(SQLModel):
    orden_servicio_tejeduria_id: str


class OrdenServicioTejeduriaUpdateSchema(SQLModel):
    estado: OrdenServicioTejeduriaEstadoEnum


class OrdenServicioTejeduriaUpdateSchemaByID(
    OrdenServicioTejeduriaUpdateSchema, OrdenServicioTejeduriaIDSchema
):
    pass


class OrdenServicioTejeduriaListUpdateSchema(SQLModel):
    ordenes: list[OrdenServicioTejeduriaUpdateSchemaByID]
