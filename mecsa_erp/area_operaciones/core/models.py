from sqlalchemy import Column, CheckConstraint, CHAR, DATE, ForeignKeyConstraint, Index, func
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date

class Proveedor(SQLModel, table=True):
    __tablename__ = "proveedor"
    
    proveedor_id: str = Field(primary_key=True)
    razon_social: str = Field(unique=True)

class OrdenCompra(SQLModel, table=True):
    __tablename__ = "orden_compra"
    
    orden_compra_id: str = Field(primary_key=True)
    proveedor_id: str

    __table_args__ = (
        ForeignKeyConstraint(['proveedor_id'], ['proveedor.proveedor_id']),
        Index(None, "proveedor_id", postgresql_using='hash'),
    )

class Producto(SQLModel, table=True):
    __tablename__ = "producto"
    
    producto_id: str = Field(primary_key=True)
    descripcion: Optional[str] = Field(nullable=True)

class OrdenCompraDetalle(SQLModel, table=True):
    __tablename__ = "orden_compra_detalle"
    
    orden_compra_id: str = Field(primary_key=True)
    producto_id: str = Field(primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(['orden_compra_id'], ['orden_compra.orden_compra_id']),
        ForeignKeyConstraint(['producto_id'], ['producto.producto_id']),
    )
    
class Movimiento(SQLModel, table=True):
    __tablename__ = "movimiento"
    
    movimiento_id: str = Field(primary_key=True)
    movimiento_descripcion_id: str
    proveedor_id: str
    fecha: date = Field(sa_column=Column(DATE, server_default=func.current_date(), nullable=False)) 

    __table_args__ = (
        ForeignKeyConstraint(['movimiento_descripcion_id'], ['movimiento_descripcion.movimiento_descripcion_id']),
        ForeignKeyConstraint(['proveedor_id'], ['proveedor.proveedor_id']),
    )
    
class MovimientoDescripcion(SQLModel, table=True):
    __tablename__ = "movimiento_descripcion"
    
    movimiento_descripcion_id: str = Field(primary_key=True)
    movimiento_tipo: str = Field(sa_type=CHAR)
    almacen_id: str
    descripcion: str

    __table_args__ = (
        ForeignKeyConstraint(['almacen_id'], ['almacen.almacen_id']),
        CheckConstraint("movimiento_tipo IN ('I', 'S')"),
    )
    
class Almacen(SQLModel, table=True):
    __tablename__ = "almacen"
    
    almacen_id: str = Field(primary_key=True)
    nombre: str
    
class MovimientoIngreso(SQLModel, table=True):
    __tablename__ = "movimiento_ingreso"
    
    movimiento_ingreso_id: str = Field(primary_key=True)
    guia_proveedor_nro_serie: str
    guia_proveedor_nro_correlativo: str

    __table_args__ = (
        ForeignKeyConstraint(['movimiento_ingreso_id'], ['movimiento.movimiento_id']),
    )

class MovimientoIngresoOrdenCompra(SQLModel, table=True):
    __tablename__ = "movimiento_ingreso_orden_compra"
    
    movimiento_ingreso_id: str = Field(primary_key=True)
    orden_compra_id: str = Field(primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(['movimiento_ingreso_id'], ['movimiento_ingreso.movimiento_ingreso_id']),
        ForeignKeyConstraint(['orden_compra_id'], ['orden_compra.orden_compra_id']),
    )