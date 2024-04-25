from sqlmodel import SQLModel

from mecsa_erp.area_operaciones.core.schemas.proveedor import ProveedorSchema

from .orden_servicio_tejeduria_detalle import OrdenServicioTejeduriaDetalleSchema


class OrdenServicioTejeduriaBase(SQLModel):
    orden_servicio_tejeduria_id: str
    estado: str


class OrdenServicioTejeduriaSimpleSchema(OrdenServicioTejeduriaBase):
    tejeduria_id: str


class OrdenServicioTejeduriaSchema(OrdenServicioTejeduriaSimpleSchema):
    proveedor: ProveedorSchema
    detalles: list[OrdenServicioTejeduriaDetalleSchema]


class OrdenServicioTejeduriaSimpleListSchema(SQLModel):
    data: list[OrdenServicioTejeduriaSimpleSchema]
    count: int = None


class OrdenServicioTejeduriaListSchema(SQLModel):
    data: list[OrdenServicioTejeduriaSchema]
    count: int = None


class OrdenServicioTejeduriaUpdateSchema(SQLModel):
    estado: str


class OrdenServicioTejeduriaUpdateMultipleSchema(SQLModel):
    data: list[OrdenServicioTejeduriaBase]
