from datetime import datetime
from sqlalchemy import ForeignKeyConstraint, String
from sqlmodel import Relationship, SQLModel, Field

from mecsa_erp.area_operaciones.constants import (
    MAX_LENGTH_CODIGO_LOTE,
    MAX_LENGTH_CRUDO_ID,
    MAX_LENGTH_HILADO_ACABADO,
    MAX_LENGTH_HILADO_FIBRA,
    MAX_LENGTH_HILADO_ID,
    MAX_LENGTH_HILADO_PROCEDENCIA,
    MAX_LENGTH_HILADO_TITULO,
    MAX_LENGTH_MOVIMIENTO_ID,
    MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_ESTADO,
    MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_DETALLE_ESTADO,
    MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_ID,
    MAX_LENGTH_PROVEEDOR_ID,
    MAX_LENGTH_TEJIDO_ID,
    MAX_LENGTH_TEJIDO_NOMBRE,
)
from mecsa_erp.area_operaciones.core.models import Proveedor


class Hilado(SQLModel, table=True):
    __tablename__ = "hilado"

    hilado_id: str = Field(
        primary_key=True, sa_type=String(length=MAX_LENGTH_HILADO_ID)
    )
    titulo: str = Field(sa_type=String(length=MAX_LENGTH_HILADO_TITULO))
    fibra: str = Field(sa_type=String(length=MAX_LENGTH_HILADO_FIBRA))
    procedencia: str = Field(sa_type=String(length=MAX_LENGTH_HILADO_PROCEDENCIA))
    acabado: str = Field(sa_type=String(length=MAX_LENGTH_HILADO_ACABADO))
    proveedor_id: str = Field(sa_type=String(length=MAX_LENGTH_PROVEEDOR_ID))

    __table_args__ = (
        ForeignKeyConstraint(["hilado_id"], ["producto.producto_id"]),
        ForeignKeyConstraint(["proveedor_id"], ["proveedor.proveedor_id"]),
    )


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


class MovimientoIngresoHiladoDetalle(SQLModel, table=True):
    __tablename__ = "movimiento_ingreso_hilado_detalle"

    movimiento_ingreso_id: str = Field(
        primary_key=True, sa_type=String(length=MAX_LENGTH_MOVIMIENTO_ID)
    )
    hilado_id: str = Field(sa_type=String(length=MAX_LENGTH_HILADO_ID))
    nro_bultos: int
    nro_conos: int
    cantidad_kg: float
    codigo_lote: str = Field(sa_type=String(length=MAX_LENGTH_CODIGO_LOTE))

    __table_args__ = (
        ForeignKeyConstraint(["movimiento_ingreso_id"], ["movimiento.movimiento_id"]),
        ForeignKeyConstraint(["hilado_id"], ["hilado.hilado_id"]),
    )


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


class MovimientoSalidaHilado(SQLModel, table=True):
    __tablename__ = "movimiento_salida_hilado"

    movimiento_salida_id: str = Field(
        primary_key=True, sa_type=String(length=MAX_LENGTH_MOVIMIENTO_ID)
    )
    orden_servicio_tejeduria_id: str = Field(
        sa_type=String(length=MAX_LENGTH_ORDEN_SERVICIO_TEJEDURIA_ID)
    )

    __table_args__ = (
        ForeignKeyConstraint(["movimiento_salida_id"], ["movimiento.movimiento_id"]),
        ForeignKeyConstraint(
            ["orden_servicio_tejeduria_id"],
            ["orden_servicio_tejeduria.orden_servicio_tejeduria_id"],
        ),
    )


class MovimientoSalidaHiladoDetalle(SQLModel, table=True):
    __tablename__ = "movimiento_salida_hilado_detalle"

    movimiento_salida_id: str = Field(
        primary_key=True, sa_type=String(length=MAX_LENGTH_MOVIMIENTO_ID)
    )
    movimiento_ingreso_id: str = Field(
        primary_key=True, sa_type=String(length=MAX_LENGTH_MOVIMIENTO_ID)
    )
    hilado_id: str = Field(sa_type=String(length=MAX_LENGTH_HILADO_ID))
    nro_bultos: int
    nro_conos: int
    cantidad_kg: float

    __table_args__ = (
        ForeignKeyConstraint(["movimiento_salida_id"], ["movimiento.movimiento_id"]),
        ForeignKeyConstraint(["movimiento_ingreso_id"], ["movimiento.movimiento_id"]),
        ForeignKeyConstraint(["hilado_id"], ["hilado.hilado_id"]),
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
