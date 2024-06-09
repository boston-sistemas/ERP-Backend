from pydantic import computed_field
from sqlmodel import SQLModel
from decimal import Decimal


class OrdenServicioTejeduriaDetalleBase(SQLModel):
    orden_servicio_tejeduria_id: str
    crudo_id: str
    programado_kg: Decimal
    consumido_kg: Decimal
    es_complemento: bool
    estado: str
    reporte_tejeduria_nro_rollos: int
    reporte_tejeduria_cantidad_kg: Decimal


class OrdenServicioTejeduriaDetalleSchema(OrdenServicioTejeduriaDetalleBase):

    @computed_field
    def kg_por_rollo(self) -> float:
        if self.reporte_tejeduria_nro_rollos == 0:
            return 0.0
        return round(
            self.reporte_tejeduria_cantidad_kg / self.reporte_tejeduria_nro_rollos, 3
        )
