from fastapi import APIRouter
from sqlalchemy.orm import joinedload

from config.database import SessionDependency
from helpers.crud import CRUD

from mecsa_erp.usuarios.models import Rol
from mecsa_erp.usuarios.schemas.usuario import RolListSchema

crud_rol = CRUD[Rol, Rol](Rol)

router = APIRouter(tags=["Roles"], prefix="/roles")


@router.get("/", response_model=RolListSchema)
def list_roles(session: SessionDependency):
    roles = crud_rol.get_multi(
        session, options=[joinedload(Rol.accesos)], apply_unique=True
    )
    return RolListSchema(data=roles)
