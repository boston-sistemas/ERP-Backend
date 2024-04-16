from sqlmodel import SQLModel, Field

class Hilado(SQLModel, table=True):
    __tablename__ = "hilado"
    
    hilado_id: str = Field(primary_key=True, foreign_key="producto.producto_id")
    titulo: str
    fibra: str
    procedencia: str
    acabado: str