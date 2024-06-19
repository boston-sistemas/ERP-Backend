from typing import Any, Generic, Sequence, Tuple, TypeVar

from fastapi import HTTPException, status
from sqlalchemy.orm.strategy_options import Load
from sqlalchemy.sql.elements import BinaryExpression
from sqlmodel import SQLModel, select

from src.core.database import SessionDependency

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)

"""
TODO: Extraer solo las columnas dadas por el esquema en la sentencia SQL
_extract_matching_columns_from_schema(
    model=self.model, schema=schema_to_select
    )
"""


class CRUD(Generic[ModelType, CreateSchemaType]):
    def __init__(self, model: type[ModelType]) -> None:
        self.model = model

    def get_by_pk(
        self, session: SessionDependency, pk: Any, options: Sequence[Load] = None
    ) -> ModelType:
        return session.get(self.model, pk, options=options)

    def get_by_pk_or_404(
        self, session: SessionDependency, pk: Any, options: Sequence[Load] = None
    ) -> ModelType:
        object = session.get(self.model, pk, options=options)
        if not object:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} {pk} no encontrado",
            )
        return object

    def get(
        self,
        session: SessionDependency,
        filter: BinaryExpression,
        options: Sequence[Load] = None,
    ) -> ModelType:
        statement = select(self.model).where(filter)

        if options is not None:
            statement.options(*options)

        return session.exec(statement).one_or_none()

    def get_or_404(
        self,
        session: SessionDependency,
        filter: BinaryExpression,
        options: Sequence[Load] = None,
    ) -> ModelType:
        object = self.get(session, filter, options)
        if not object:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} no encontrado",
            )
        return object

    def get_multi(
        self,
        session: SessionDependency,
        filter: BinaryExpression = None,
        options: Sequence[Load] = None,
        apply_unique: bool = False,
    ) -> list[ModelType]:
        statement = select(self.model)

        if filter is not None:
            statement = statement.where(filter)

        if options is not None:
            statement = statement.options(*options)

        if apply_unique:
            return session.exec(statement).unique().all()

        return session.exec(statement).all()

    def create(
        self,
        session: SessionDependency,
        object: CreateSchemaType,
        commit: bool = True,
        refresh: bool = False,
    ) -> Tuple[str, ModelType]:
        object_dict = object.model_dump()
        db_object: ModelType = self.model(**object_dict)

        session.add(db_object)

        if commit:
            session.commit()

        if refresh:
            session.refresh(db_object)

        message = f"{self.model.__name__} creado"
        return message, db_object

    def update(
        self,
        session: SessionDependency,
        object: ModelType,
        update_data: dict,
        commit: bool = True,
        refresh: bool = False,
    ):
        object.sqlmodel_update(update_data)
        session.add(object)

        if commit:
            session.commit()

        if refresh:
            session.refresh(object)

        message = f"{self.model.__name__} actualizado"

        return message, object

    def delete(
        self, session: SessionDependency, object: ModelType, commit: bool = True
    ) -> str:
        session.delete(object)

        if commit:
            session.commit()

        message = f"{self.model.__name__} eliminado"
        return message
