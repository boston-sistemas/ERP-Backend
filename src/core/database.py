from datetime import datetime
from typing import AsyncGenerator

from sqlalchemy import create_engine, func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    max_identifier_length=60,
    echo=settings.DEBUG,
    pool_recycle=3600,
)
engine_async = create_async_engine(
    settings.DATABASE_URL_ASYNC, echo=settings.DEBUG, pool_recycle=3600
)

promec_engine = create_engine(
    settings.PROMEC_DATABASE_URL,
    echo=settings.DEBUG,
    pool_recycle=1800,
    pool_pre_ping=True,
    query_cache_size=0,
)
promec_async_engine = create_async_engine(
    settings.PROMEC_DATABASE_URL_ASYNC,
    echo=settings.DEBUG,
    pool_recycle=1800,
    pool_pre_ping=True,
    query_cache_size=0,
)


class Base(DeclarativeBase):
    pass


class PromecBase(DeclarativeBase):
    pass


class AuditMixin:
    is_deleted: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    created_by: Mapped[int] = mapped_column()
    updated_at: Mapped[datetime | None] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
    updated_by: Mapped[int | None] = mapped_column()
    deleted_at: Mapped[datetime | None] = mapped_column()
    deleted_by: Mapped[int | None] = mapped_column()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(bind=engine_async, expire_on_commit=False) as db:
        try:
            yield db
            await db.commit()
        except Exception:
            await db.rollback()
            raise


async def get_promec_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(bind=promec_async_engine, expire_on_commit=False) as db:
        try:
            yield db
            await db.commit()
        except Exception:
            await db.rollback()
            raise


def transactional(func):
    """
    Transactional decorator that enables `flush` in the repository to ensure that pending
    operations are sent to the database before executing the method.

    Useful when automatically generated values (such as IDs) are needed for dependent
    operations within the same transaction, without committing the transaction.

    Args:
        func (callable): Asynchronous method to which the decorator will be applied.

    Returns:
        callable: Function wrapped with transactional behavior.
    """

    async def wrapper(self, *args, **kwargs):
        self.repository.flush = True
        try:
            return await func(self, *args, **kwargs)
        finally:
            self.repository.flush = False

    return wrapper
