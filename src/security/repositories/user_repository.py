from sqlalchemy import BinaryExpression
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.strategy_options import Load

from src.core.repository import BaseRepository
from src.security.models import Usuario


class UserRepository(BaseRepository[Usuario]):
    def __init__(self, db: AsyncSession, commit: bool = True) -> None:
        super().__init__(Usuario, db, commit)

    @staticmethod
    def include_roles() -> Load:
        return joinedload(Usuario.roles)

    async def find_user(
        self, filter: BinaryExpression, include_roles=False
    ) -> Usuario | None:
        options: list[Load] = []

        if include_roles:
            options.append(self.include_roles())

        user = await self.find(filter, options=options)

        return user
