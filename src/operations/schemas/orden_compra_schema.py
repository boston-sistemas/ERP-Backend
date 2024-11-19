from datetime import datetime

from pydantic import BaseModel

class OrdenCompraBase(BaseModel):
    codcia: str
    tpooc: str
    nrooc: str

class OrdenCompraDetalleBase(BaseModel):
    codprod: str
    canord: float
    canate: float
    codund: str
    flgest: str

class OrdenCompraDetalleSchema(OrdenCompraDetalleBase):
    pass

class OrdenCompraSchema(OrdenCompraBase):
    codpro: str
    fchemi: datetime
    fchvto: datetime
    codmon: int
    flgest: str
    details: list[OrdenCompraDetalleSchema]

    class Config:
        from_attributes = True
