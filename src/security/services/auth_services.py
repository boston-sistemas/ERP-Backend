from typing import Generic, TypeVar

from sqlalchemy.future import select
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import BinaryExpression

from src.core.database import Base
from src.security.models import Sesion, Usuario

ModelType = TypeVar("ModelType", bound=Base)


class AuthService:
    def __init__(self, db: Session, commit: bool = True) -> None:
        self.db = db
        self.commit = commit

    def read_model_by_parameter(
        self, model: Generic[ModelType], filter: BinaryExpression
    ) -> Usuario:
        stmt = select(model).where(filter)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def create_session(self, sesion: Sesion) -> None:
        self.db.add(sesion)

        if self.commit:
            self.db.commit()
            self.db.refresh(sesion)

    def update_session(self, sesion: Sesion, data: dict) -> None:
        for key, value in data.items():
            setattr(sesion, key, value)

        if self.commit:
            self.db.commit()
            self.db.refresh(sesion)
