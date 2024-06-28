from sqlalchemy.future import select
from sqlalchemy.orm import Session

from src.security.models import Acceso


class AccessService:
    def __init__(self, db: Session, commit: bool = True) -> None:
        self.db = db
        self.commit = commit

    def read_access(self) -> list[Acceso]:
        stmt = select(Acceso)
        result = self.db.execute(stmt)
        return result.scalars().all()
