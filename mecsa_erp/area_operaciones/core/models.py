from sqlalchemy import Column, CheckConstraint, CHAR, DATE, func
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
    proveedor_id: str = Field(foreign_key="proveedor.proveedor_id", index=True)

class Producto(SQLModel, table=True):
    __tablename__ = "producto"
    
    producto_id: str = Field(primary_key=True)
    descripcion: Optional[str] = Field(nullable=True)

class OrdenCompraDetalle(SQLModel, table=True):
    __tablename__ = "orden_compra_detalle"
    
    orden_compra_id: str = Field(primary_key=True, foreign_key="orden_compra.orden_compra_id")
    producto_id: str = Field(primary_key=True, foreign_key="producto.producto_id")
    
class Movimiento(SQLModel, table=True):
    __tablename__ = "movimiento"
    
    movimiento_id: str = Field(primary_key=True)
    movimiento_descripcion_id: str = Field(foreign_key="movimiento_descripcion.movimiento_descripcion_id")
    proveedor_id: str = Field(foreign_key="proveedor.proveedor_id")
    fecha: date = Field(sa_column=Column(DATE, server_default=func.current_date(), nullable=False)) 
    
class MovimientoDescripcion(SQLModel, table=True):
    __tablename__ = "movimiento_descripcion"
    
    movimiento_descripcion_id: str = Field(primary_key=True)
    movimiento_tipo: str = Field(sa_type=CHAR, sa_column_args=[CheckConstraint("movimiento_tipo IN ('I', 'S')")])
    almacen_id: str = Field(foreign_key="almacen.almacen_id")
    descripcion: str
    
class Almacen(SQLModel, table=True):
    __tablename__ = "almacen"
    
    almacen_id: str = Field(primary_key=True)
    nombre: str
    
class MovimientoIngreso(SQLModel, table=True):
    __tablename__ = "movimiento_ingreso"
    
    movimiento_ingreso_id: str = Field(primary_key=True, foreign_key="movimiento.movimiento_id")
    guia_proveedor_nro_serie: str
    guia_proveedor_nro_correlativo: str

class MovimientoIngresoOrdenCompra(SQLModel, table=True):
    __tablename__ = "movimiento_ingreso_orden_compra"
    
    movimiento_ingreso_id: str = Field(primary_key=True, foreign_key="movimiento_ingreso.movimiento_ingreso_id")
    orden_compra_id: str = Field(primary_key=True, foreign_key="orden_compra.orden_compra_id")