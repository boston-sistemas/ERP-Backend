from decimal import Decimal

from pydantic import BaseModel, Field


class OrdenServicioTintoreriaDetalleBase(BaseModel):
    id: int
    orden_servicio_tintoreria_id: int
    orden_servicio_tejeduria_id: str
    crudo_id: str
    nro_rollos: int
    cantidad_kg: Decimal


class OrdenServicioTintoreriaDetalleSchema(OrdenServicioTintoreriaDetalleBase):
    pass


class OrdenServicioTintoreriaDetalleCreateSchema(BaseModel):
    orden_servicio_tintoreria_id: int
    orden_servicio_tejeduria_id: str
    crudo_id: str
    nro_rollos: int = Field(ge=0)
    cantidad_kg: Decimal = Field(ge=0)


class OrdenServicioTintoreriaDetalleCreateSchemaByProgramacion(BaseModel):
    orden_servicio_tejeduria_id: str
    crudo_id: str
    nro_rollos: int = Field(ge=0)
    cantidad_kg: Decimal = Field(ge=0)
