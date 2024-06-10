from sqlalchemy import (
    Column,
    CheckConstraint,
    CHAR,
    DATE,
    ForeignKeyConstraint,
    Identity,
    Index,
    Integer,
    func,
    String,
)
from sqlmodel import Relationship, SQLModel, Field
from typing import TYPE_CHECKING, Optional
from datetime import date

from mecsa_erp.area_operaciones.constants import (
    MAX_LENGTH_ALMACEN_ID,
    MAX_LENGTH_ALMACEN_NOMBRE,
    MAX_LENGTH_GUIA_PROVEEDOR_NRO_CORRELATIVO,
    MAX_LENGTH_GUIA_PROVEEDOR_NRO_SERIE,
    MAX_LENGTH_MOVIMIENTO_DESCRIPCION,
    MAX_LENGTH_MOVIMIENTO_DESCRIPCION_ID,
    MAX_LENGTH_MOVIMIENTO_ID,
    MAX_LENGTH_ORDEN_COMPRA_ID,
    MAX_LENGTH_PRODUCTO_DESCRIPCION,
    MAX_LENGTH_PRODUCTO_ID,
    MAX_LENGTH_PROVEEDOR_ALIAS,
    MAX_LENGTH_PROVEEDOR_ID,
    MAX_LENGTH_PROVEEDOR_RAZON_SOCIAL,
    MAX_LENGTH_SERVICIO_NOMBRE,
)

if TYPE_CHECKING:
    from mecsa_erp.area_operaciones.modulo0.models import OrdenServicioTejeduria


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


class OrdenCompra(SQLModel, table=True):
    __tablename__ = "orden_compra"

    orden_compra_id: str = Field(
        primary_key=True, sa_type=String(length=MAX_LENGTH_ORDEN_COMPRA_ID)
    )
    proveedor_id: str = Field(sa_type=String(length=MAX_LENGTH_PROVEEDOR_ID))

    __table_args__ = (
        ForeignKeyConstraint(["proveedor_id"], ["proveedor.proveedor_id"]),
        Index(None, "proveedor_id", postgresql_using="hash"),
    )


class Producto(SQLModel, table=True):
    __tablename__ = "producto"

    producto_id: str = Field(primary_key=True, sa_type=String(MAX_LENGTH_PRODUCTO_ID))
    descripcion: Optional[str] = Field(
        nullable=True, sa_type=String(MAX_LENGTH_PRODUCTO_DESCRIPCION)
    )


class OrdenCompraDetalle(SQLModel, table=True):
    __tablename__ = "orden_compra_detalle"

    orden_compra_id: str = Field(
        primary_key=True, sa_type=String(MAX_LENGTH_ORDEN_COMPRA_ID)
    )
    producto_id: str = Field(primary_key=True, sa_type=String(MAX_LENGTH_PRODUCTO_ID))

    __table_args__ = (
        ForeignKeyConstraint(["orden_compra_id"], ["orden_compra.orden_compra_id"]),
        ForeignKeyConstraint(["producto_id"], ["producto.producto_id"]),
    )


class Movimiento(SQLModel, table=True):
    __tablename__ = "movimiento"

    movimiento_id: str = Field(
        primary_key=True, sa_type=String(MAX_LENGTH_MOVIMIENTO_ID)
    )
    movimiento_descripcion_id: str = Field(
        sa_type=String(length=MAX_LENGTH_MOVIMIENTO_DESCRIPCION_ID)
    )
    proveedor_id: str = Field(sa_type=String(length=MAX_LENGTH_PROVEEDOR_ID))
    fecha: date = Field(
        sa_column=Column(DATE, server_default=func.current_date(), nullable=False)
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["movimiento_descripcion_id"],
            ["movimiento_descripcion.movimiento_descripcion_id"],
        ),
        ForeignKeyConstraint(["proveedor_id"], ["proveedor.proveedor_id"]),
    )


class MovimientoDescripcion(SQLModel, table=True):
    __tablename__ = "movimiento_descripcion"

    movimiento_descripcion_id: str = Field(
        primary_key=True, sa_type=String(length=MAX_LENGTH_MOVIMIENTO_DESCRIPCION_ID)
    )
    movimiento_tipo: str = Field(sa_type=CHAR(length=1))
    almacen_id: str = Field(sa_type=String(length=MAX_LENGTH_ALMACEN_ID))
    descripcion: str = Field(sa_type=String(length=MAX_LENGTH_MOVIMIENTO_DESCRIPCION))

    __table_args__ = (
        ForeignKeyConstraint(["almacen_id"], ["almacen.almacen_id"]),
        CheckConstraint("movimiento_tipo IN ('I', 'S')"),
    )


class Almacen(SQLModel, table=True):
    __tablename__ = "almacen"

    almacen_id: str = Field(
        primary_key=True, sa_type=String(length=MAX_LENGTH_ALMACEN_ID)
    )
    nombre: str = Field(sa_type=String(length=MAX_LENGTH_ALMACEN_NOMBRE))


class MovimientoIngreso(SQLModel, table=True):
    __tablename__ = "movimiento_ingreso"

    movimiento_ingreso_id: str = Field(
        primary_key=True, sa_type=String(length=MAX_LENGTH_MOVIMIENTO_ID)
    )
    guia_proveedor_nro_serie: str = Field(
        sa_type=String(length=MAX_LENGTH_GUIA_PROVEEDOR_NRO_SERIE)
    )
    guia_proveedor_nro_correlativo: str = Field(
        sa_type=String(length=MAX_LENGTH_GUIA_PROVEEDOR_NRO_CORRELATIVO)
    )

    __table_args__ = (
        ForeignKeyConstraint(["movimiento_ingreso_id"], ["movimiento.movimiento_id"]),
    )


class MovimientoIngresoOrdenCompra(SQLModel, table=True):
    __tablename__ = "movimiento_ingreso_orden_compra"

    movimiento_ingreso_id: str = Field(
        primary_key=True, sa_type=String(length=MAX_LENGTH_MOVIMIENTO_ID)
    )
    orden_compra_id: str = Field(
        primary_key=True, sa_type=String(length=MAX_LENGTH_ORDEN_COMPRA_ID)
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["movimiento_ingreso_id"], ["movimiento_ingreso.movimiento_ingreso_id"]
        ),
        ForeignKeyConstraint(["orden_compra_id"], ["orden_compra.orden_compra_id"]),
    )
