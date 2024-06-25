from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import (
    TIMESTAMP,
    ForeignKeyConstraint,
    Identity,
    Integer,
    PrimaryKeyConstraint,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

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


class Proveedor(Base):
    __tablename__ = "proveedor"

    proveedor_id: Mapped[str] = mapped_column(String(length=MAX_LENGTH_PROVEEDOR_ID))
    razon_social: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_PROVEEDOR_RAZON_SOCIAL),
        unique=True,
    )
    alias: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_PROVEEDOR_ALIAS),
        unique=True,
    )

    ordenes_servicio_tejeduria: Mapped[list["OrdenServicioTejeduria"]] = relationship(
        back_populates="proveedor"
    )

    __table_args__ = (PrimaryKeyConstraint("proveedor_id"),)


class Servicio(Base):
    __tablename__ = "servicio"

    servicio_id: Mapped[int] = mapped_column(
        Identity(start=1),
    )
    nombre: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_SERVICIO_NOMBRE),
        unique=True,
    )

    proveedores: Mapped[list[Proveedor]] = relationship(secondary="proveedor_servicio")

    __table_args__ = (PrimaryKeyConstraint("servicio_id"),)


class ProveedorServicio(Base):
    __tablename__ = "proveedor_servicio"

    proveedor_id: Mapped[str] = mapped_column(String(length=MAX_LENGTH_PROVEEDOR_ID))
    servicio_id: Mapped[int] = mapped_column()

    __table_args__ = (
        PrimaryKeyConstraint("proveedor_id", "servicio_id"),
        ForeignKeyConstraint(["proveedor_id"], ["proveedor.proveedor_id"]),
        ForeignKeyConstraint(["servicio_id"], ["servicio.servicio_id"]),
    )


class Tejido(Base):
    __tablename__ = "tejido"

    tejido_id: Mapped[str] = mapped_column(String(length=MAX_LENGTH_TEJIDO_ID))
    nombre: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_TEJIDO_NOMBRE),
    )

    __table_args__ = (PrimaryKeyConstraint("tejido_id"),)


class Crudo(Base):
    __tablename__ = "crudo"

    crudo_id: Mapped[str] = mapped_column(String(length=MAX_LENGTH_CRUDO_ID))
    tejido_id: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_TEJIDO_ID),
    )
    densidad: Mapped[int] = mapped_column()
    ancho: Mapped[int] = mapped_column()
    galga: Mapped[int] = mapped_column()
    diametro: Mapped[int] = mapped_column()
    longitud_malla: Mapped[float] = mapped_column()

    __table_args__ = (
        PrimaryKeyConstraint("crudo_id"),
        ForeignKeyConstraint(["tejido_id"], ["tejido.tejido_id"]),
    )


class OrdenServicioTejeduria(Base):
    __tablename__ = "orden_servicio_tejeduria"

    orden_servicio_tejeduria_id: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_ID)
    )
    tejeduria_id: Mapped[str] = mapped_column(String(length=MAX_LENGTH_PROVEEDOR_ID))
    fecha: Mapped[datetime] = mapped_column()
    estado: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_ESTADO)
    )

    proveedor: Mapped[Proveedor] = relationship(
        back_populates="ordenes_servicio_tejeduria"
    )
    detalles: Mapped[list["OrdenServicioTejeduriaDetalle"]] = relationship(
        back_populates="orden_servicio"
    )

    __table_args__ = (
        PrimaryKeyConstraint("orden_servicio_tejeduria_id"),
        ForeignKeyConstraint(["tejeduria_id"], ["proveedor.proveedor_id"]),
        ForeignKeyConstraint(["estado"], ["orden_servicio_tejeduria_estado.estado"]),
    )

<<<<<<< HEAD
=======

>>>>>>> e285d0370da119e713b3c57d518d3c41bc0c79c4
class OrdenServicioTejeduriaEstado(Base):
    __tablename__ = "orden_servicio_tejeduria_estado"

    estado: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_ESTADO)
    )

    __table_args__ = (PrimaryKeyConstraint("estado"),)


class OrdenServicioTejeduriaDetalle(Base):
    __tablename__ = "orden_servicio_tejeduria_detalle"

    orden_servicio_tejeduria_id: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_ID)
    )
    crudo_id: Mapped[str] = mapped_column(String(length=MAX_LENGTH_CRUDO_ID))
    programado_kg: Mapped[float] = mapped_column()
    consumido_kg: Mapped[float] = mapped_column()
    es_complemento: Mapped[bool] = mapped_column()
    estado: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_DETALLE_ESTADO)
    )
    reporte_tejeduria_nro_rollos: Mapped[int] = mapped_column()
    reporte_tejeduria_cantidad_kg: Mapped[float] = mapped_column()

    orden_servicio: Mapped[OrdenServicioTejeduria] = relationship(
        back_populates="detalles"
    )

    __table_args__ = (
        PrimaryKeyConstraint("orden_servicio_tejeduria_id", "crudo_id"),
        ForeignKeyConstraint(
            ["orden_servicio_tejeduria_id"],
            ["orden_servicio_tejeduria.orden_servicio_tejeduria_id"],
        ),
        ForeignKeyConstraint(["crudo_id"], ["crudo.crudo_id"]),
        ForeignKeyConstraint(
            ["estado"], ["orden_servicio_tejeduria_detalle_estado.estado"]
        ),
    )


class OrdenServicioTejeduriaDetalleEstado(Base):
    __tablename__ = "orden_servicio_tejeduria_detalle_estado"

    estado: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_DETALLE_ESTADO)
    )

    __table_args__ = (PrimaryKeyConstraint("estado"),)


class OrdenServicioTejeduriaDetalleReporteLog(Base):
    __tablename__ = "orden_servicio_tejeduria_detalle_reporte_log"

    log_id: Mapped[UUID] = mapped_column()
    proveedor_id: Mapped[str] = mapped_column(String(length=MAX_LENGTH_PROVEEDOR_ID))
    orden_servicio_tejeduria_id: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_ID)
    )
    crudo_id: Mapped[str] = mapped_column(String(length=MAX_LENGTH_CRUDO_ID))
    estado: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_DETALLE_ESTADO)
    )
    reporte_tejeduria_nro_rollos: Mapped[int] = mapped_column()
    reporte_tejeduria_cantidad_kg: Mapped[float] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

    __table_args__ = (PrimaryKeyConstraint("log_id"),)


class Color(Base):
    __tablename__ = "color"

    color_id: Mapped[int] = mapped_column(Integer, Identity(start=1), primary_key=True)
    nombre: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_COLOR_NOMBRE), unique=True
    )
    descripcion: Mapped[Optional[str]] = mapped_column(
        String(length=MAX_LENGTH_COLOR_DESCRIPCION), nullable=True
    )

    __table_args__ = (PrimaryKeyConstraint("color_id"),)


class ProgramacionTintoreria(Base):
    __tablename__ = "programacion_tintoreria"

    programacion_tintoreria_id: Mapped[int] = mapped_column(
        Identity(start=1),
    )
    from_tejeduria_id: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_PROVEEDOR_ID)
    )
    to_tintoreria_id: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_PROVEEDOR_ID)
    )

    __table_args__ = (
        PrimaryKeyConstraint("programacion_tintoreria_id"),
        ForeignKeyConstraint(["from_tejeduria_id"], ["proveedor.proveedor_id"]),
        ForeignKeyConstraint(["to_tintoreria_id"], ["proveedor.proveedor_id"]),
    )


class Partida(Base):
    __tablename__ = "partida"

    programacion_tintoreria_id: Mapped[int] = mapped_column()
    nro_partida: Mapped[int] = mapped_column()
    color_id: Mapped[int] = mapped_column()

    __table_args__ = (
        PrimaryKeyConstraint("programacion_tintoreria_id", "nro_partida"),
        ForeignKeyConstraint(
            ["programacion_tintoreria_id"],
            ["programacion_tintoreria.programacion_tintoreria_id"],
        ),
    )


class PartidaDetalle(Base):
    __tablename__ = "partida_detalle"

    programacion_tintoreria_id: Mapped[int] = mapped_column()
    nro_partida: Mapped[int] = mapped_column()
    orden_servicio_tejeduria_id: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_ID)
    )
    crudo_id: Mapped[str] = mapped_column(String(length=MAX_LENGTH_CRUDO_ID))
    nro_rollos: Mapped[int] = mapped_column()
    cantidad_kg: Mapped[float] = mapped_column()

    __table_args__ = (
        PrimaryKeyConstraint("programacion_tintoreria_id", "nro_partida"),
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
