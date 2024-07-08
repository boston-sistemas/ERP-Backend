from typing import Optional

from pydantic import BaseModel

from .partida import PartidaCreateSchema
from .proveedor import ProveedorSchema


class Color(BaseModel):
    color_id: int
    nombre: str
    descripcion: Optional[str] = None

    class Config:
        from_attributes = True


class ProgramacionTintoreriaResponse(BaseModel):
    tejedurias: list[ProveedorSchema]
    tintorerias: list[ProveedorSchema]
    colores: list[Color]


class ProgramacionTintoreriaCreateSchema(BaseModel):
    from_tejeduria_id: str
    to_tintoreria_id: str

    partidas: list[PartidaCreateSchema]
