from sqlalchemy import Column, ForeignKeyConstraint, Identity, Integer, String
from sqlmodel import Field, SQLModel

from mecsa_erp.area_operaciones.constants import (
    MAX_LENGTH_COLOR_DESCRIPCION,
    MAX_LENGTH_COLOR_NOMBRE,
    MAX_LENGTH_CRUDO_ID,
    MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_ID,
    MAX_LENGTH_PROVEEDOR_ID,
)


class Color(SQLModel, table=True):
    __tablename__ = "color"

    color_id: int = Field(
        sa_column=Column(Integer, Identity(start=1), primary_key=True)
    )
    nombre: str = Field(unique=True, sa_type=String(length=MAX_LENGTH_COLOR_NOMBRE))
    descripcion: str | None = Field(sa_type=String(length=MAX_LENGTH_COLOR_DESCRIPCION))


class ProgramacionTintoreria(SQLModel, table=True):
    __tablename__ = "programacion_tintoreria"

    programacion_tintoreria_id: int = Field(
        sa_column=Column(Integer, Identity(start=1), primary_key=True)
    )
    from_tejeduria_id: str = Field(sa_type=String(length=MAX_LENGTH_PROVEEDOR_ID))
    to_tintoreria_id: str = Field(sa_type=String(length=MAX_LENGTH_PROVEEDOR_ID))

    __table_args__ = (
        ForeignKeyConstraint(["from_tejeduria_id"], ["proveedor.proveedor_id"]),
        ForeignKeyConstraint(["to_tintoreria_id"], ["proveedor.proveedor_id"]),
    )


class Partida(SQLModel, table=True):
    __tablename__ = "partida"

    programacion_tintoreria_id: int = Field(primary_key=True)
    nro_partida: int = Field(primary_key=True)
    color_id: int

    __table_args__ = (
        ForeignKeyConstraint(
            ["programacion_tintoreria_id"],
            ["programacion_tintoreria.programacion_tintoreria_id"],
        ),
    )


class PartidaDetalle(SQLModel, table=True):
    __tablename__ = "partida_detalle"

    programacion_tintoreria_id: int = Field(primary_key=True)
    nro_partida: int = Field(primary_key=True)
    orden_servicio_tejeduria_id: str = Field(
        sa_type=String(length=MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_ID)
    )
    crudo_id: str = Field(sa_type=String(length=MAX_LENGTH_CRUDO_ID))
    nro_rollos: int
    cantidad_kg: float

    __table_args__ = (
        ForeignKeyConstraint(
            ["programacion_tintoreria_id", "nro_partida"],
            ["partida.programacion_tintoreria_id", "partida.nro_partida"],
        ),
        ForeignKeyConstraint(
            ["orden_servicio_tejeduria_id", "crudo_id"],
            [
                "orden_servicio_tejeduria_detalle.orden_servicio_tejeduria_id",
                "orden_servicio_tejeduria_detalle.crudo_id",
            ],
        ),
    )
