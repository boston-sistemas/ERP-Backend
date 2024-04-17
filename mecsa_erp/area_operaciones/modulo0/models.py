from sqlalchemy import Boolean, ForeignKey, Numeric
from sqlmodel import SQLModel, Field

class Hilado(SQLModel, table=True):
    __tablename__ = "hilado"
    
    hilado_id: str = Field(primary_key=True, sa_column_args=[ForeignKey("producto.producto_id")])
    titulo: str
    fibra: str
    procedencia: str
    acabado: str
    proveedor: str = Field(sa_column_args=[ForeignKey("proveedor.proveedor_id")])
    
class Tejido(SQLModel, table=True):
    __tablename__ = "tejido"
    
    tejido_id: str = Field(primary_key=True)
    nombre: str

class Crudo(SQLModel, table=True):
    __tablename__ = "crudo"
    
    crudo_id: str = Field(primary_key=True)
    tejido_id: str = Field(sa_column_args=[ForeignKey("tejido.tejido_id")])
    densidad: int
    ancho: int
    galga: int
    diametro: int
    longitud_malla: float = Field(sa_type=Numeric)
 
class MovimientoIngresoHiladoDetalle(SQLModel, table=True):
    __tablename__ = "movimiento_ingreso_hilado_detalle"
    
    movimiento_ingreso_id: str = Field(primary_key=True, sa_column_args=[ForeignKey("movimiento.movimiento_id")])
    hilado_id: str = Field(sa_column_args=[ForeignKey("hilado.hilado_id")])
    nro_bultos: int
    nro_conos: int
    cantidad_kg: float = Field(sa_type=Numeric)
    codigo_lote: str

class OrdenServicioTejeduria(SQLModel, table=True):
    __tablename__ = "orden_servicio_tejeduria"
    
    orden_servicio_tejeduria_id: str = Field(primary_key=True)
    tejeduria_id: str = Field(sa_column_args=[ForeignKey("proveedor.proveedor_id")])
    estado_id: int = Field(sa_column_args=[ForeignKey("orden_servicio_tejeduria_estado.id")])

class OrdenServicioTejeduriaEstado(SQLModel, table=True):
    __tablename__ = "orden_servicio_tejeduria_estado"

    id: int = Field(primary_key=True)
    estado: str

class MovimientoSalidaHilado(SQLModel, table=True):
    __tablename__ = "movimiento_salida_hilado"
    
    movimiento_salida_id: str = Field(primary_key=True, sa_column_args=[ForeignKey("movimiento.movimiento_id")])
    orden_servicio_tejeduria_id: str = Field(sa_column_args=[ForeignKey("orden_servicio_tejeduria.orden_servicio_tejeduria_id")])
    
class MovimientoSalidaHiladoDetalle(SQLModel, table=True):
    __tablename__ = "movimiento_salida_hilado_detalle"
    
    movimiento_salida_id: str = Field(primary_key=True, sa_column_args=[ForeignKey("movimiento.movimiento_id")])
    movimiento_ingreso_id: str = Field(primary_key=True, sa_column_args=[ForeignKey("movimiento.movimiento_id")])
    hilado_id: str = Field(sa_column_args=[ForeignKey("hilado.hilado_id")])
    nro_bultos: int
    nro_conos: int
    cantidad_kg: float = Field(sa_type=Numeric)
    
class OrdenServicioTejeduriaDetalle(SQLModel, table=True):
    __tablename__ = "orden_servicio_tejeduria_detalle"
    
    orden_servicio_tejeduria_id: str = Field(primary_key=True, sa_column_args=[ForeignKey("orden_servicio_tejeduria.orden_servicio_tejeduria_id")])
    crudo_id: str = Field(primary_key=True, sa_column_args=[ForeignKey("crudo.crudo_id")])
    cantidad_kg: float = Field(sa_type=Numeric)
    es_complemento: bool = Field(sa_type=Boolean)
    estado_id: int = Field(sa_column_args=[ForeignKey("orden_servicio_tejeduria_detalle_estado.id")])
    reporte_tejeduria_nro_rollos: int
    reporte_tejeduria_cantidad_kg: float = Field(sa_type=Numeric)

class OrdenServicioTejeduriaDetalleEstado(SQLModel, table=True):
    __tablename__ = "orden_servicio_tejeduria_detalle_estado"

    id: int = Field(primary_key=True)
    estado: str