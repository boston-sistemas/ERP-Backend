from datetime import datetime
from sqlmodel import SQLModel

from mecsa_erp.area_operaciones.core.schemas.proveedor import ProveedorSchema

from .orden_servicio_tejeduria_detalle import OrdenServicioTejeduriaDetalleSchema


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


class OrdenServicioTejeduriaSimpleListSchema(SQLModel):
    data: list[OrdenServicioTejeduriaSimpleSchema]
    count: int = None


class OrdenServicioTejeduriaListSchema(SQLModel):
    data: list[OrdenServicioTejeduriaSchema]
    count: int = None


class OrdenServicioTejeduriaWithDetallesSchema(OrdenServicioTejeduriaBase):
    detalles: list[OrdenServicioTejeduriaDetalleSchema]


class OrdenServicioTejeduriaWithDetallesListSchema(SQLModel):
    ordenes: list[OrdenServicioTejeduriaWithDetallesSchema]


class OrdenServicioTejeduriaUpdateSchema(SQLModel):
    estado: str


class OrdenServicioTejeduriaUpdateMultipleSchema(SQLModel):
    data: list[OrdenServicioTejeduriaBase]
