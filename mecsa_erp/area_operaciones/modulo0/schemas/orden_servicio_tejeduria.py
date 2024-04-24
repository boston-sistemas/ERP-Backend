from typing import List
from sqlmodel import SQLModel

from ..models import OrdenServicioTejeduria

class OrdenServicioTejeduriaListSchema(SQLModel):
    data: List[OrdenServicioTejeduria]
    count: int