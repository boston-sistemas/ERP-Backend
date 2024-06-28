# from pydantic import BaseModel
from typing import Optional

from sqlmodel import SQLModel

from .partida import PartidaCreateSchema
from .proveedor import ProveedorSchema


class Color(SQLModel):
    color_id: int
    nombre: str
    descripcion: Optional[str] = None


class ProgramacionTintoreriaResponse(SQLModel):
    tejedurias: list[ProveedorSchema]
    tintorerias: list[ProveedorSchema]
    colores: list[Color]


class ProgramacionTintoreriaCreateSchema(SQLModel):
    from_tejeduria_id: str
    to_tintoreria_id: str

    partidas: list[PartidaCreateSchema]
