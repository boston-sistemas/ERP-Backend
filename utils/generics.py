from typing import Annotated, List, Type, TypeVar
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import SQLModel, Session, select

from config.database import get_session

from sqlalchemy.exc import IntegrityError

ModelType = TypeVar("ModelType", bound=SQLModel)

SessionDependency = Annotated[Session, Depends(get_session)]

class Message(SQLModel):
    message: str = "Exito"


"""
Forma de como utilizarlo en el módulo 0

tejido_view = GenericView(
    model_type=Tejido,
    scheme_type=Tejido,
    prefix="/tejido",
    tag="Modulo 0 - Tejido",
    name="Tejido"
)

crudo_view = GenericView(
    model_type=Crudo,
    scheme_type=Crudo,
    prefix="/crudo",
    tag="Modulo 0 - Crudo",
    name="Crudo"
)

router.include_router(tejido_view.as_view())
router.include_router(crudo_view.as_view())
"""

"""
TODO: Refactorizar el constructor
TODO: Cuando la llave primaria es de otro tipo de dato: entero, guardar el tipo de dato del pk
TODO: Cuando la llave primaria es compuesta
TODO: El scheme puede ser distinto en las operaciones que se realicen
TODO: Como agregar otro endpoint distinto al router 
TODO: Como se comporta con relaciones 
TODO: Manejar distintas dependencias
TODO: Clases mixin especializadas (ListMixin, RetrieveMixin, DeleteMixin, etc)
"""


class GenericView:

    def __init__(
        self,
        model_type: Type[SQLModel],
        scheme_type: Type[SQLModel],
        prefix: str,
        tag: str,
        name: str,
        name_plural: str = None,
    ):
        self.model_type = model_type
        self.scheme_type = scheme_type
        self.prefix = prefix
        self.tag = tag
        self.name = name
        self.name_plural = name_plural if name_plural else name + "s"
        self.actions = {
            "retrieve": self.add_api_retrieve,
            "list": self.add_api_list,
            "create": self.add_api_create,
            "update": self.add_api_update,
            "delete": self.add_api_delete,
        }

    def get_scheme_type(self, action):
        if action == "retrieve":
            return self.scheme_type
        return self.scheme_type

    def list(self, session: Session):
        statement = select(self.model_type)
        items = session.exec(statement).all()
        print(len(items))
        return items

    def retrieve(self, session: Session, id):
        return session.get(self.model_type, id)

    def create(self, session: Session, scheme):
        item = self.model_type.model_validate(scheme)
        try:
            session.add(item)
            session.commit()
            session.refresh(item)
            return item
        except IntegrityError as e:
            if "duplicate key value" in str(e):
                raise ValueError("El objeto ya existe.")
            raise e

    def destroy(self, session: Session, id):
        item = self.retrieve(session, id)
        if not item:
            raise ValueError("El objeto no existe")

        session.delete(item)
        session.commit()

        return Message(message="Objeto eliminado correctamente")

    def update(self, session: Session, id, scheme):
        item = self.retrieve(session, id)
        if not item:
            raise ValueError("El objeto no existe")

        update_dict = scheme.model_dump(exclude_unset=True)
        item.sqlmodel_update(update_dict)
        session.add(item)
        session.commit()
        session.refresh(item)
        return item

    def add_api_list(self, router):
        @router.get(
            path="/",
            name=f"Read {self.name_plural}",
            response_model=List[self.get_scheme_type("retrieve")],
        )
        def list_items(session: SessionDependency):
            return self.list(session)

    def add_api_retrieve(self, router):
        @router.get(
            path="/{id}", name=f"Read {self.name}", response_model=self.scheme_type
        )
        def retrieve_item(session: SessionDependency, id):
            item = self.retrieve(session, id)
            if not item:
                raise HTTPException(status_code=404, detail="Object not found")
            return item

    def add_api_create(self, router):
        @router.post("/", name=f"Create {self.name}")
        def create_item(session: SessionDependency, scheme: self.scheme_type):
            try:
                return self.create(session, scheme)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

    def add_api_update(self, router):
        @router.patch(
            "/{id}", name=f"Update {self.name}", response_model=self.scheme_type
        )
        def update_item(session: SessionDependency, id, scheme: self.scheme_type):
            try:
                return self.update(session, id, scheme)
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))

    def add_api_delete(self, router):
        @router.delete("/", name=f"Delete {self.name}", response_model=Message)
        def delete_item(session: SessionDependency, id):
            try:
                return self.destroy(session, id)
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))

    def as_view(self):
        router = APIRouter(tags=[self.tag], prefix=self.prefix)
        for api in self.actions:
            self.actions[api](router)
        return router
