from pydantic import BaseModel


class ColorBase(BaseModel):
    color_id: int
    nombre: str
    descripcion: str | None = None

    class Config:
        from_attributes = True


class ColorSchema(ColorBase):
    pass
