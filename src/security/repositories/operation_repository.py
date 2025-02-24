from sqlalchemy import BinaryExpression, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.strategy_options import Load

from src.core.repository import BaseRepository
from src.security.models import Operation


class OperationRepository(BaseRepository[Operation]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Operation, db)

    async def find_operations(
        self,
        filter: BinaryExpression = None,
        options: list[Load] = None,
        limit: int = None,
        offset: int = None,
        apply_unique: bool = False,
        joins: list[tuple] = None,
    ) -> list[Operation]:
        options: list[Load] = [] if options is None else options
        base_filter: list[BinaryExpression] = []

        filter = (
            and_(filter, *base_filter) if filter is not None else and_(*base_filter)
        )

        return await self.find_all(
            filter=filter,
            options=options,
            apply_unique=apply_unique,
            joins=joins,
            limit=limit,
            offset=offset,
        )

    async def find_operation_by_id(
        self,
        id: str,
        filter: BinaryExpression = None,
        options: list[Load] = None,
        joins: list[tuple] = None,
    ) -> Operation | None:
        options: list[Load] = [] if options is None else options
        base_filter: list[BinaryExpression] = []

        base_filter.append(Operation.id == id)

        filter = (
            and_(filter, *base_filter) if filter is not None else and_(*base_filter)
        )

        return await self.find(
            filter=filter,
            options=options,
            joins=joins,
        )
