from typing import Any, Generic, Sequence, TypeVar, Union

from sqlalchemy import BinaryExpression, ClauseElement, Column, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.strategy_options import Load

from src.core.database import Base, get_db

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

    async def save(self, object: ModelType, flush: bool = False) -> ModelType:
        from ..security.audit.audit_service import AuditService

        values_before = await AuditService.get_before_values(instance=object)

        self.db.add(object)

        if flush:
            await self.db.flush()

        values_after = await AuditService.get_after_values(instance=object)

        async for db in get_db():
            await AuditService.audit_data_log(
                db=db,
                instance=object,
                values_before=values_before,
                values_after=values_after,
            )

        return object

    async def save_all(
        self, objects: Sequence[ModelType], flush: bool = False
    ) -> Sequence[ModelType]:
        from ..security.audit.audit_service import AuditService

        values_before_list = []
        for obj in objects:
            values_before_list.append(
                await AuditService.get_before_values(instance=obj)
            )

        self.db.add_all(objects)

        if flush:
            await self.db.flush()

        values_after_list = []
        for obj in objects:
            values_after_list.append(await AuditService.get_after_values(instance=obj))

        async for db in get_db():
            for obj, before, after in zip(
                objects, values_before_list, values_after_list
            ):
                await AuditService.audit_data_log(
                    db=db,
                    instance=obj,
                    values_before=before,
                    values_after=after,
                )
        return objects

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
        use_outer_joins: bool = False,
        order_by: Union[
            Column, ClauseElement, Sequence[Union[Column, ClauseElement]]
        ] = None,
    ) -> list[ModelType]:
        stmt = select(self.model)

        if filter is not None:
            stmt = stmt.where(filter)

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
        from ..security.audit.audit_service import AuditService

        values_before = await AuditService.get_before_values(instance=object)

        await self.db.delete(object)

        if self.flush:
            await self.db.flush()

        async for db in get_db():
            await AuditService.audit_data_log(
                db=db,
                instance=object,
                values_before=values_before,
                values_after={},
            )

    async def delete_all(
        self, objects: Sequence[ModelType], flush: bool = False
    ) -> None:
        from ..security.audit.audit_service import AuditService

        values_before_list = [
            await AuditService.get_before_values(instance=obj) for obj in objects
        ]

        for object in objects:
            await self.db.delete(object)

        if flush:
            await self.db.flush()

        for obj, before in zip(objects, values_before_list):
            async for db in get_db():
                await AuditService.audit_data_log(
                    db=db,
                    instance=obj,
                    values_before=before,
                    values_after={},
                )

    def expunge_all(self) -> None:
        self.db.expunge_all()

    async def expunge_all_objects(self, objects: Sequence[ModelType]) -> None:
        for object in objects:
            self.db.expunge(object)

    async def expunge(self, object: ModelType) -> None:
        self.db.expunge(object)

    async def refresh(self, object: ModelType) -> None:
        await self.db.refresh(object)
