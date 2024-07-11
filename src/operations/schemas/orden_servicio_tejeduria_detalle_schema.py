from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, computed_field


class OrdenServicioTejeduriaDetalleIDSchema(BaseModel):
    orden_servicio_tejeduria_id: str
    crudo_id: str


class OrdenServicioTejeduriaDetalleBase(BaseModel):
    orden_servicio_tejeduria_id: str
    crudo_id: str
    programado_kg: Decimal
    consumido_kg: Decimal
    es_complemento: bool
    estado: str
    reporte_tejeduria_nro_rollos: int
    reporte_tejeduria_cantidad_kg: Decimal

    class Config:
        from_attributes = True


class OrdenServicioTejeduriaDetalleSchema(OrdenServicioTejeduriaDetalleBase):
    @computed_field
    def kg_por_rollo(self) -> float:
        if self.reporte_tejeduria_nro_rollos == 0:
            return 0.0
        return round(
            self.reporte_tejeduria_cantidad_kg / self.reporte_tejeduria_nro_rollos, 3
        )


class OrdenServicioTejeduriaDetalleEstadoEnum(str, Enum):
    no_iniciado = "NO INICIADO"
    cerrado = "EN CURSO"
    liquidado = "DETENIDO"
    listo = "LISTO"


class OrdenServicioTejeduriaDetalleUpdateSchema(BaseModel):
    reporte_tejeduria_nro_rollos: int | None = Field(default=None, ge=0)
    reporte_tejeduria_cantidad_kg: float | None = Field(default=None, ge=0)
    estado: OrdenServicioTejeduriaDetalleEstadoEnum | None = None


class OrdenServicioTejeduriaDetalleUpdateSchemaByID(
    OrdenServicioTejeduriaDetalleUpdateSchema, OrdenServicioTejeduriaDetalleIDSchema
):
    pass


class OrdenServicioTejeduriaDetalleListUpdateSchema(BaseModel):
    subordenes: list[OrdenServicioTejeduriaDetalleUpdateSchemaByID]
