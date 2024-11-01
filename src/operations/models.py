from datetime import datetime
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
    MAX_LENGTH_ORDEN_SERVICIO_TINTORERIA_CODIGO_MECSA,
    MAX_LENGTH_ORDEN_SERVICIO_TINTORERIA_ESTADO,
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

    __table_args__ = (PrimaryKeyConstraint("proveedor_id"),)


class EspecialidadEmpresa(Base):
    __tablename__ = "especialidad_empresa"

    especialidad_id: Mapped[int] = mapped_column(
        Identity(start=1),
    )
    nombre: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_SERVICIO_NOMBRE),
        unique=True,
    )

    proveedores: Mapped[list[Proveedor]] = relationship(
        secondary="proveedor_especialidad"
    )

    __table_args__ = (PrimaryKeyConstraint("especialidad_id"),)


class ProveedorEspecialidad(Base):
    __tablename__ = "proveedor_especialidad"

    proveedor_id: Mapped[str] = mapped_column(String(length=MAX_LENGTH_PROVEEDOR_ID))
    especialidad_id: Mapped[int] = mapped_column()

    __table_args__ = (
        PrimaryKeyConstraint("proveedor_id", "especialidad_id"),
        ForeignKeyConstraint(["proveedor_id"], ["proveedor.proveedor_id"]),
        ForeignKeyConstraint(
            ["especialidad_id"], ["especialidad_empresa.especialidad_id"]
        ),
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
    __tablename__ = "os_tejeduria"

    orden_servicio_tejeduria_id: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_ID)
    )
    tejeduria_id: Mapped[str] = mapped_column(String(length=MAX_LENGTH_PROVEEDOR_ID))
    fecha: Mapped[datetime] = mapped_column()
    estado: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_ESTADO)
    )

    proveedor: Mapped[Proveedor] = relationship()
    detalles: Mapped[list["OrdenServicioTejeduriaDetalle"]] = relationship()

    __table_args__ = (
        PrimaryKeyConstraint("orden_servicio_tejeduria_id"),
        ForeignKeyConstraint(["tejeduria_id"], ["proveedor.proveedor_id"]),
    )


class OrdenServicioTejeduriaDetalle(Base):
    __tablename__ = "os_tejeduria_detalle"

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

    __table_args__ = (
        PrimaryKeyConstraint("orden_servicio_tejeduria_id", "crudo_id"),
        ForeignKeyConstraint(
            ["orden_servicio_tejeduria_id"],
            ["os_tejeduria.orden_servicio_tejeduria_id"],
        ),
        ForeignKeyConstraint(["crudo_id"], ["crudo.crudo_id"]),
    )


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

    color_id: Mapped[int] = mapped_column(Integer, Identity(start=1))
    nombre: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_COLOR_NOMBRE), unique=True
    )
    descripcion: Mapped[str | None] = mapped_column(
        String(length=MAX_LENGTH_COLOR_DESCRIPCION), nullable=True
    )

    __table_args__ = (PrimaryKeyConstraint("color_id"),)

    def __repr__(self):
        return f"<Color(color_id='{self.color_id}',nombre='{self.nombre}')>"


class ProgramacionTintoreria(Base):
    __tablename__ = "programacion_tintoreria"

    id: Mapped[int] = mapped_column(
        Identity(start=1),
    )
    from_tejeduria_id: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_PROVEEDOR_ID)
    )
    to_tintoreria_id: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_PROVEEDOR_ID)
    )

    __table_args__ = (
        PrimaryKeyConstraint("id"),
        ForeignKeyConstraint(["from_tejeduria_id"], ["proveedor.proveedor_id"]),
        ForeignKeyConstraint(["to_tintoreria_id"], ["proveedor.proveedor_id"]),
    )


class OrdenServicioTintoreria(Base):
    __tablename__ = "os_tintoreria"

    orden_servicio_tintoreria_id: Mapped[int] = mapped_column(
        Identity(start=1),
    )
    programacion_tintoreria_id: Mapped[int | None] = mapped_column()
    color_id: Mapped[int] = mapped_column()
    estado: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_ORDEN_SERVICIO_TINTORERIA_ESTADO)
    )
    codigo_mecsa: Mapped[str | None] = mapped_column(
        String(length=MAX_LENGTH_ORDEN_SERVICIO_TINTORERIA_CODIGO_MECSA), unique=True
    )

    __table_args__ = (
        PrimaryKeyConstraint("orden_servicio_tintoreria_id"),
        ForeignKeyConstraint(
            ["programacion_tintoreria_id"],
            ["programacion_tintoreria.id"],
        ),
        ForeignKeyConstraint(["color_id"], ["color.color_id"]),
    )


class OrdenServicioTintoreriaDetalle(Base):
    __tablename__ = "os_tintoreria_detalle"

    id: Mapped[int] = mapped_column(Identity(start=1))
    orden_servicio_tintoreria_id: Mapped[int] = mapped_column()
    orden_servicio_tejeduria_id: Mapped[str] = mapped_column(
        String(MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_ID)
    )
    crudo_id: Mapped[str] = mapped_column(String(MAX_LENGTH_CRUDO_ID))
    nro_rollos: Mapped[int] = mapped_column()
    cantidad_kg: Mapped[float] = mapped_column()

    __table_args__ = (
        PrimaryKeyConstraint("id"),
        ForeignKeyConstraint(
            ["orden_servicio_tintoreria_id"],
            ["os_tintoreria.orden_servicio_tintoreria_id"],
        ),
        ForeignKeyConstraint(
            ["orden_servicio_tejeduria_id", "crudo_id"],
            [
                "os_tejeduria_detalle.orden_servicio_tejeduria_id",
                "os_tejeduria_detalle.crudo_id",
            ],
        ),
    )
