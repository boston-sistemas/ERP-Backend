from pydantic import BaseModel

from .orden_servicio_tejeduria import OrdenServicioTejeduriaWithDetallesSchema


class ReporteStockTejeduriaResponse(BaseModel):
    ordenes: list[OrdenServicioTejeduriaWithDetallesSchema]
