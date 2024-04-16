from sqlmodel import SQLModel, Field
from typing import Optional

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