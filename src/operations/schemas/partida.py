from sqlmodel import SQLModel

from .partida_detalle import PartidaDetalleCreateSchema


class PartidaCreateSchema(SQLModel):
    nro_partida: int
    color_id: int

    detalles: list[PartidaDetalleCreateSchema]
