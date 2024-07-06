from collections.abc import Generator
from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Session

from src.core.config import settings

engine = create_engine(settings.DATABASE_URL, max_identifier_length=60)
engine_async = create_async_engine(settings.DATABASE_URL_ASYNC)
AsyncSessionLocal = async_sessionmaker(
    bind=engine_async, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


def get_session() -> Generator[Session, None, None]:
    with Session(bind=engine, expire_on_commit=False) as session:
        yield session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as db:
        yield db


SessionDependency = Annotated[Session, Depends(get_db)]
