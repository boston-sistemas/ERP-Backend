from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlmodel import Session, create_engine

from src.core.config import settings

# engine = create_engine(
#     settings.DATABASE_URL,
#     max_identifier_length=60
# )
#


class Base(DeclarativeBase):
    pass


# def get_session() -> Generator[Session, None, None]:
#     with Session(bind=engine, expire_on_commit=False) as session:
#         yield session

engine_async = create_async_engine(settings.DATABASE_URL_ASYNC)
AsyncSessionLocal = async_sessionmaker(
    bind=engine_async, class_=AsyncSession, expire_on_commit=False
)


async def get_db() -> Generator[AsyncSession, None, None]:
    async with AsyncSessionLocal() as session:
        yield session


SessionDependency = Annotated[AsyncSession, Depends(get_db)]
