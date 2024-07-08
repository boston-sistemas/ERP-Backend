from pydantic import BaseModel


class ProveedorBase(BaseModel):
    proveedor_id: str
    razon_social: str
    alias: str

    class Config:
        from_attributes = True


class ProveedorSchema(ProveedorBase):
    pass
