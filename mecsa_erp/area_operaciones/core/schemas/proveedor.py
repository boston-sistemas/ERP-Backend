from sqlmodel import SQLModel


class ProveedorBase(SQLModel):
    proveedor_id: str
    razon_social: str


class ProveedorSchema(ProveedorBase):
    pass
