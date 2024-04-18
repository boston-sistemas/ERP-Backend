from sqlalchemy import Boolean, ForeignKey, ForeignKeyConstraint, Numeric
from sqlmodel import SQLModel, Field

class Hilado(SQLModel, table=True):
    __tablename__ = "hilado"
    
    hilado_id: str = Field(primary_key=True)
    titulo: str
    fibra: str
    procedencia: str
    acabado: str
    proveedor_id: str

    __table_args__ = (
        ForeignKeyConstraint(['hilado_id'], ['producto.producto_id']),
        ForeignKeyConstraint(['proveedor_id'], ['proveedor.proveedor_id']),
    )
    
class Tejido(SQLModel, table=True):
    __tablename__ = "tejido"
    
    tejido_id: str = Field(primary_key=True)
    nombre: str

class Crudo(SQLModel, table=True):
    __tablename__ = "crudo"
    
    crudo_id: str = Field(primary_key=True)
    tejido_id: str
    densidad: int
    ancho: int
    galga: int
    diametro: int
    longitud_malla: float = Field(sa_type=Numeric)

    __table_args__ = (
        ForeignKeyConstraint(['tejido_id'], ['tejido.tejido_id']),
    )
 
class MovimientoIngresoHiladoDetalle(SQLModel, table=True):
    __tablename__ = "movimiento_ingreso_hilado_detalle"
    
    movimiento_ingreso_id: str = Field(primary_key=True)
    hilado_id: str
    nro_bultos: int
    nro_conos: int
    cantidad_kg: float = Field(sa_type=Numeric)
    codigo_lote: str

    __table_args__ = (
        ForeignKeyConstraint(['movimiento_ingreso_id'], ['movimiento.movimiento_id']),
        ForeignKeyConstraint(['hilado_id'], ['hilado.hilado_id']),
    )

class OrdenServicioTejeduria(SQLModel, table=True):
    __tablename__ = "orden_servicio_tejeduria"
    
    orden_servicio_tejeduria_id: str = Field(primary_key=True)
    tejeduria_id: str
    estado: str

    __table_args__ = (
        ForeignKeyConstraint(['tejeduria_id'], ['proveedor.proveedor_id']),
        ForeignKeyConstraint(['estado'], ['orden_servicio_tejeduria_estado.estado']),
    )

class OrdenServicioTejeduriaEstado(SQLModel, table=True):
    __tablename__ = "orden_servicio_tejeduria_estado"

    estado: str = Field(primary_key=True)

class MovimientoSalidaHilado(SQLModel, table=True):
    __tablename__ = "movimiento_salida_hilado"
    
    movimiento_salida_id: str = Field(primary_key=True)
    orden_servicio_tejeduria_id: str

    __table_args__ = (
        ForeignKeyConstraint(['movimiento_salida_id'], ['movimiento.movimiento_id']),
        ForeignKeyConstraint(['orden_servicio_tejeduria_id'], ['orden_servicio_tejeduria.orden_servicio_tejeduria_id']),
    )
    
class MovimientoSalidaHiladoDetalle(SQLModel, table=True):
    __tablename__ = "movimiento_salida_hilado_detalle"
    
    movimiento_salida_id: str = Field(primary_key=True)
    movimiento_ingreso_id: str = Field(primary_key=True)
    hilado_id: str
    nro_bultos: int
    nro_conos: int
    cantidad_kg: float = Field(sa_type=Numeric)

    __table_args__ = (
        ForeignKeyConstraint(['movimiento_salida_id'], ['movimiento.movimiento_id']),
        ForeignKeyConstraint(['movimiento_ingreso_id'], ['movimiento.movimiento_id']),
        ForeignKeyConstraint(['hilado_id'], ['hilado.hilado_id']),
    )
    
class OrdenServicioTejeduriaDetalle(SQLModel, table=True):
    __tablename__ = "orden_servicio_tejeduria_detalle"
    
    orden_servicio_tejeduria_id: str = Field(primary_key=True)
    crudo_id: str = Field(primary_key=True)
    cantidad_kg: float = Field(sa_type=Numeric)
    es_complemento: bool = Field(sa_type=Boolean)
    estado: str
    reporte_tejeduria_nro_rollos: int
    reporte_tejeduria_cantidad_kg: float = Field(sa_type=Numeric)

    __table_args__ = (
        ForeignKeyConstraint(['orden_servicio_tejeduria_id'], ['orden_servicio_tejeduria.orden_servicio_tejeduria_id']),
        ForeignKeyConstraint(['crudo_id'], ['crudo.crudo_id']),
        ForeignKeyConstraint(['estado'], ['orden_servicio_tejeduria_detalle_estado.estado']),
    )

class OrdenServicioTejeduriaDetalleEstado(SQLModel, table=True):
    __tablename__ = "orden_servicio_tejeduria_detalle_estado"

    estado: str = Field(primary_key=True)