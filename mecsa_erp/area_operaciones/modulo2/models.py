from sqlalchemy import Column, Identity, Integer, String
from sqlmodel import Field, SQLModel

from mecsa_erp.area_operaciones.constants import (
    MAX_LENGTH_COLOR_DESCRIPCION,
    MAX_LENGTH_COLOR_NOMBRE,
)


class Color(SQLModel, table=True):
    __tablename__ = "color"

    color_id: int = Field(
        sa_column=Column(Integer, Identity(start=1), primary_key=True)
    )
    nombre: str = Field(unique=True, sa_type=String(length=MAX_LENGTH_COLOR_NOMBRE))
    descripcion: str | None = Field(sa_type=String(length=MAX_LENGTH_COLOR_DESCRIPCION))
