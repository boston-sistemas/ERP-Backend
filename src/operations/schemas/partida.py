from pydantic import BaseModel

from .partida_detalle import PartidaDetalleCreateSchema


class PartidaCreateSchema(BaseModel):
    nro_partida: int
    color_id: int

    detalles: list[PartidaDetalleCreateSchema]
