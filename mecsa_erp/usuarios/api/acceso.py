from fastapi import APIRouter
from sqlalchemy.orm import joinedload

from config.database import SessionDependency
from helpers.crud import CRUD

from mecsa_erp.usuarios.models import Acceso
from mecsa_erp.usuarios.schemas.usuario import AccesoListSchema

crud_acceso = CRUD[Acceso, Acceso](Acceso)

router = APIRouter(tags=["Accesos"], prefix="/accesos")


@router.get("/", response_model=AccesoListSchema)
def list_accesos(session: SessionDependency):
    accesos = crud_acceso.get_multi(
        session, options=[joinedload(Acceso.roles)], apply_unique=True
    )
    return AccesoListSchema(data=accesos)
