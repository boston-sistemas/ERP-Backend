from datetime import datetime
from typing import AsyncGenerator

from sqlalchemy import create_engine, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.core.config import settings

engine = create_engine(
    settings.DATABASE_URL, max_identifier_length=60, echo=settings.DEBUG
)
engine_async = create_async_engine(settings.DATABASE_URL_ASYNC, echo=settings.DEBUG)

promec_engine = create_engine(settings.PROMEC_DATABASE_URL, echo=settings.DEBUG)
async_promec_engine = create_async_engine(
    settings.PROMEC_DATABASE_URL_ASYNC, echo=settings.DEBUG
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine_async, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
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
    async with AsyncSessionLocal() as db:
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
