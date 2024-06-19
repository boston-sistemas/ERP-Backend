from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    TIMESTAMP,
    Column,
    ForeignKeyConstraint,
    Identity,
    Integer,
    String,
    func,
)
from sqlmodel import Field, Relationship, SQLModel

from src.core.database import Base

from src.operations.constants import (
    MAX_LENGTH_COLOR_DESCRIPCION,
    MAX_LENGTH_COLOR_NOMBRE,
    MAX_LENGTH_CRUDO_ID,
    MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_DETALLE_ESTADO,
    MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_ESTADO,
    MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_ID,
    MAX_LENGTH_PROVEEDOR_ALIAS,
    MAX_LENGTH_PROVEEDOR_ID,
    MAX_LENGTH_PROVEEDOR_RAZON_SOCIAL,
    MAX_LENGTH_SERVICIO_NOMBRE,
    MAX_LENGTH_TEJIDO_ID,
    MAX_LENGTH_TEJIDO_NOMBRE,
)


class ProveedorServicio(SQLModel, table=True):
    __tablename__ = "proveedor_servicio"

    proveedor_id: str = Field(
        primary_key=True, sa_type=String(length=MAX_LENGTH_PROVEEDOR_ID)
    )
    servicio_id: int = Field(primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(["proveedor_id"], ["proveedor.proveedor_id"]),
        ForeignKeyConstraint(["servicio_id"], ["servicio.servicio_id"]),
    )


class Proveedor(SQLModel, table=True):
    __tablename__ = "proveedor"

    proveedor_id: str = Field(
        primary_key=True, sa_type=String(length=MAX_LENGTH_PROVEEDOR_ID)
    )
    razon_social: str = Field(
        unique=True, sa_type=String(length=MAX_LENGTH_PROVEEDOR_RAZON_SOCIAL)
    )
    alias: str = Field(unique=True, sa_type=String(length=MAX_LENGTH_PROVEEDOR_ALIAS))

    ordenes_servicio_tejeduria: list["OrdenServicioTejeduria"] = Relationship(
        back_populates="proveedor"
    )


class Servicio(SQLModel, table=True):
    __tablename__ = "servicio"
    servicio_id: int = Field(
        sa_column=Column(Integer, Identity(start=1), primary_key=True)
    )
    nombre: str = Field(unique=True, sa_type=String(length=MAX_LENGTH_SERVICIO_NOMBRE))
    proveedores: list[Proveedor] = Relationship(link_model=ProveedorServicio)


class Tejido(SQLModel, table=True):
    __tablename__ = "tejido"

    # TODO: Agregar el campo ID: primary key
    tejido_id: str = Field(
        primary_key=True, sa_type=String(length=MAX_LENGTH_TEJIDO_ID)
    )
    nombre: str = Field(sa_type=String(length=MAX_LENGTH_TEJIDO_NOMBRE))


class Crudo(SQLModel, table=True):
    __tablename__ = "crudo"

    crudo_id: str = Field(primary_key=True, sa_type=String(length=MAX_LENGTH_CRUDO_ID))
    tejido_id: str = Field(sa_type=String(length=MAX_LENGTH_TEJIDO_ID))
    densidad: int
    ancho: int
    galga: int
    diametro: int
    longitud_malla: float

    __table_args__ = (ForeignKeyConstraint(["tejido_id"], ["tejido.tejido_id"]),)


class OrdenServicioTejeduria(SQLModel, table=True):
    __tablename__ = "orden_servicio_tejeduria"

    orden_servicio_tejeduria_id: str = Field(
        primary_key=True, sa_type=String(length=MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_ID)
    )
    tejeduria_id: str = Field(sa_type=String(length=MAX_LENGTH_PROVEEDOR_ID))
    fecha: datetime
    estado: str = Field(
        sa_type=String(length=MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_ESTADO)
    )

    proveedor: Proveedor = Relationship(back_populates="ordenes_servicio_tejeduria")
    detalles: list["OrdenServicioTejeduriaDetalle"] = Relationship(
        back_populates="orden_servicio"
    )

    __table_args__ = (
        ForeignKeyConstraint(["tejeduria_id"], ["proveedor.proveedor_id"]),
        ForeignKeyConstraint(["estado"], ["orden_servicio_tejeduria_estado.estado"]),
    )


class OrdenServicioTejeduriaEstado(SQLModel, table=True):
    __tablename__ = "orden_servicio_tejeduria_estado"

    estado: str = Field(
        primary_key=True,
        sa_type=String(length=MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_ESTADO),
    )


class OrdenServicioTejeduriaDetalle(SQLModel, table=True):
    __tablename__ = "orden_servicio_tejeduria_detalle"

    orden_servicio_tejeduria_id: str = Field(
        primary_key=True, sa_type=String(length=MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_ID)
    )
    crudo_id: str = Field(primary_key=True, sa_type=String(length=MAX_LENGTH_CRUDO_ID))
    programado_kg: float
    consumido_kg: float
    es_complemento: bool
    estado: str = Field(
        sa_type=String(length=MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_DETALLE_ESTADO)
    )
    reporte_tejeduria_nro_rollos: int
    reporte_tejeduria_cantidad_kg: float

    orden_servicio: OrdenServicioTejeduria = Relationship(back_populates="detalles")

    __table_args__ = (
        ForeignKeyConstraint(
            ["orden_servicio_tejeduria_id"],
            ["orden_servicio_tejeduria.orden_servicio_tejeduria_id"],
        ),
        ForeignKeyConstraint(["crudo_id"], ["crudo.crudo_id"]),
        ForeignKeyConstraint(
            ["estado"], ["orden_servicio_tejeduria_detalle_estado.estado"]
        ),
    )


class OrdenServicioTejeduriaDetalleEstado(SQLModel, table=True):
    __tablename__ = "orden_servicio_tejeduria_detalle_estado"

    estado: str = Field(
        primary_key=True,
        sa_type=String(length=MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_DETALLE_ESTADO),
    )


class OrdenServicioTejeduriaDetalleReporteLog(SQLModel, table=True):
    __tablename__ = "orden_servicio_tejeduria_detalle_reporte_log"

    log_id: UUID = Field(primary_key=True)
    proveedor_id: str = Field(sa_type=String(length=MAX_LENGTH_PROVEEDOR_ID))
    orden_servicio_tejeduria_id: str = Field(
        sa_type=String(length=MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_ID)
    )
    crudo_id: str = Field(sa_type=String(length=MAX_LENGTH_CRUDO_ID))
    estado: str = Field(
        sa_type=String(length=MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_DETALLE_ESTADO)
    )
    reporte_tejeduria_nro_rollos: int
    reporte_tejeduria_cantidad_kg: float
    created_at: datetime = Field(sa_column=Column(TIMESTAMP, server_default=func.now()))


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
