from typing import Any, Generic, Sequence, TypeVar, Union

from sqlalchemy import BinaryExpression, ClauseElement, Column, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.strategy_options import Load

from src.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(
        self,
        model: ModelType,
        db: AsyncSession,
        flush: bool = False,
    ) -> None:
        self.model = model
        self.db = db
        self.flush = flush

    async def save(self, object: ModelType) -> ModelType:
        self.db.add(object)

        if self.flush:
            await self.db.flush()

        return object

    async def save_all(self, objects: Sequence[ModelType]) -> None:
        self.db.add_all(objects)

        if self.flush:
            await self.db.flush()

    async def find(
        self,
        filter: BinaryExpression,
        joins: Sequence[tuple] = None,
        use_outer_joins: bool = False,
        options: Sequence[Load] = None,
    ) -> ModelType:
        stmt = select(self.model).where(filter)

        if joins:
            for join_item in joins:
                if use_outer_joins:
                    if isinstance(join_item, tuple) and len(join_item) == 2:
                        stmt = stmt.outerjoin(join_item[0], join_item[1])
                    else:
                        stmt = stmt.outerjoin(join_item)
                else:
                    if isinstance(join_item, tuple) and len(join_item) == 2:
                        stmt = stmt.join(join_item[0], join_item[1])
                    else:
                        stmt = stmt.join(join_item)

        if options:
            stmt = stmt.options(*options)
            return (await self.db.execute(stmt)).scalars().unique().one_or_none()

        result = (await self.db.execute(stmt)).scalars().unique().one_or_none()

        if result is not None:
            await self.db.refresh(result)

        return result

    async def find_by_id(
        self, id: Any, options: Sequence[Load] = None, **kwargs
    ) -> ModelType:
        object = await self.db.get(self.model, id, options=options, **kwargs)

        return object

    async def find_all(
        self,
        filter: BinaryExpression = None,
        options: Sequence[Load] = None,
        joins: Sequence[tuple] = None,
        apply_unique: bool = False,
        offset: int = None,
        limit: int = None,
        order_by: Union[
            Column, ClauseElement, Sequence[Union[Column, ClauseElement]]
        ] = None,
    ) -> list[ModelType]:
        stmt = select(self.model)

        if filter is not None:
            stmt = stmt.where(filter)

        if joins:
            for join_item in joins:
                # stmt = stmt.join(*join_item)
                if isinstance(join_item, tuple) and len(join_item) == 2:
                    stmt = stmt.join(join_item[0], join_item[1])
                else:
                    stmt = stmt.join(join_item)

        if options:
            stmt = stmt.options(*options)

        if order_by is not None:
            if isinstance(order_by, (list, tuple)):
                stmt = stmt.order_by(*order_by)
            else:
                stmt = stmt.order_by(order_by)

        if offset is not None:
            stmt = stmt.offset(offset)

        if limit is not None:
            stmt = stmt.limit(limit)

        if apply_unique:
            results = (await self.db.execute(stmt)).scalars().unique().all()
        else:
            results = (await self.db.execute(stmt)).scalars().all()

        for obj in results:
            await self.db.refresh(obj)

        return results

    async def count(self, filter: BinaryExpression = None) -> int:
        stmt = select(func.count()).select_from(self.model)

        if filter is not None:
            stmt = stmt.where(filter)

        return (await self.db.execute(stmt)).scalar()

    async def exists(self, filter: BinaryExpression) -> tuple[bool, ModelType | None]:
        stmt = select(self.model).where(filter).limit(1)
        object = (await self.db.execute(stmt)).scalar()

        return object is not None, object

    async def delete(self, object: ModelType) -> None:
        await self.db.delete(object)

        if self.flush:
            await self.db.flush()

    async def delete_all(
        self, objects: Sequence[ModelType], flush: bool = False
    ) -> None:
        for object in objects:
            await self.db.delete(object)

        if flush:
            await self.db.flush()

    def expunge_all(self) -> None:
        self.db.expunge_all()
