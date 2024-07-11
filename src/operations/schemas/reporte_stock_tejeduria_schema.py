from pydantic import BaseModel

from .orden_servicio_tejeduria_schema import OrdenServicioTejeduriaWithDetallesSchema


class ReporteStockTejeduriaResponse(BaseModel):
    ordenes: list[OrdenServicioTejeduriaWithDetallesSchema]
