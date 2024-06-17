from datetime import datetime
from enum import Enum

from sqlmodel import SQLModel

from .orden_servicio_tejeduria_detalle import OrdenServicioTejeduriaDetalleSchema
from .proveedor import ProveedorSchema


class OrdenServicioTejeduriaIDSchema(SQLModel):
    orden_servicio_tejeduria_id: str


class OrdenServicioTejeduriaBase(SQLModel):
    orden_servicio_tejeduria_id: str
    tejeduria_id: str
    fecha: datetime
    estado: str


class OrdenServicioTejeduriaSimpleSchema(OrdenServicioTejeduriaBase):
    pass


class OrdenServicioTejeduriaSchema(OrdenServicioTejeduriaBase):
    proveedor: ProveedorSchema
    detalles: list[OrdenServicioTejeduriaDetalleSchema]


class OrdenServicioTejeduriaWithDetallesSchema(OrdenServicioTejeduriaBase):
    detalles: list[OrdenServicioTejeduriaDetalleSchema]


class OrdenServicioTejeduriaWithDetallesListSchema(SQLModel):
    ordenes: list[OrdenServicioTejeduriaWithDetallesSchema]


class OrdenServicioTejeduriaEstadoEnum(str, Enum):
    pendiente = "PENDIENTE"
    cerrado = "CERRADO"
    liquidado = "LIQUIDADO"


class OrdenServicioTejeduriaUpdateSchema(SQLModel):
    estado: OrdenServicioTejeduriaEstadoEnum


class OrdenServicioTejeduriaUpdateSchemaByID(
    OrdenServicioTejeduriaUpdateSchema, OrdenServicioTejeduriaIDSchema
):
    pass


class OrdenServicioTejeduriaListUpdateSchema(SQLModel):
    ordenes: list[OrdenServicioTejeduriaUpdateSchemaByID]
