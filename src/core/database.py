import json
from datetime import date, datetime
from typing import AsyncGenerator

from sqlalchemy import CLOB, TypeDecorator, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from src.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    max_identifier_length=60,
    echo=settings.DEBUG,
    pool_recycle=3600,
)
engine_async = create_async_engine(
    settings.DATABASE_URL_ASYNC,
    echo=settings.DEBUG,
    pool_recycle=3600,
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
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    query_cache_size=0,
)


class Base(DeclarativeBase):
    def __repr__(self):
        insp = inspect(self)
        formatted_attrs = ""
        for attr in self.__mapper__.column_attrs:
            column_name = attr.columns[0].name
            if attr.key in insp.unloaded:
                formatted_attrs += f"\n    {attr.key}({column_name})=None"
            else:
                value = getattr(self, attr.key, None)
                if isinstance(value, date):
                    formatted_attrs += (
                        f"\n    {attr.key}({column_name})={value.strftime('%d-%m-%Y')}"
                    )
                else:
                    formatted_attrs += f"\n    {attr.key}({column_name})={repr(value)}"

        return f"<{self.__class__.__name__}({formatted_attrs}\n)>"


class PromecBase(DeclarativeBase):
    def __repr__(self):
        insp = inspect(self)
        formatted_attrs = ""
        for attr in self.__mapper__.column_attrs:
            column_name = attr.columns[0].name
            if attr.key in insp.unloaded:
                formatted_attrs += f"\n    {attr.key}({column_name})=None"
            else:
                value = getattr(self, attr.key, None)
                if isinstance(value, date):
                    formatted_attrs += (
                        f"\n    {attr.key}({column_name})={value.strftime('%d-%m-%Y')}"
                    )
                else:
                    formatted_attrs += f"\n    {attr.key}({column_name})={repr(value)}"

        return f"<{self.__class__.__name__}({formatted_attrs}\n)>"


class JSONCLOB(TypeDecorator):
    """Convierte automáticamente JSON <-> CLOB en SQLAlchemy."""

    impl = CLOB  # Se almacena como CLOB en la BD

    def process_bind_param(self, value, dialect):
        """Convierte dict -> str antes de guardar."""
        if value is None:
            return None
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        """Convierte str -> dict al recuperar."""
        if value is None:
            return None
        return json.loads(value)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(
        bind=engine_async, expire_on_commit=False, autoflush=False
    ) as db:
        try:
            yield db
            await db.commit()
        except Exception:
            await db.rollback()
            raise


async def get_promec_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(
        bind=promec_async_engine, expire_on_commit=False, autoflush=False
    ) as db:
        try:
            yield db
            await db.commit()
        except Exception:
            await db.rollback()
            raise
        finally:
            await db.close()


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
