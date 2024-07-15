from collections.abc import Generator
from datetime import datetime
from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy import create_engine, func, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from src.core.config import settings

engine = create_engine(
    settings.DATABASE_URL, max_identifier_length=60, echo=settings.DEBUG
)
engine_async = create_async_engine(settings.DATABASE_URL_ASYNC, echo=settings.DEBUG)
AsyncSessionLocal = async_sessionmaker(
    bind=engine_async, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


class AuditMixin:
    is_deleted: Mapped[bool] = mapped_column(server_default=text("0"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.sysdate(), nullable=False
    )
    created_by: Mapped[int] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.sysdate(), onupdate=func.sysdate(), nullable=True
    )
    updated_by: Mapped[int] = mapped_column(nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(nullable=True)
    deleted_by: Mapped[int] = mapped_column(nullable=True)


def get_session() -> Generator[Session, None, None]:
    with Session(bind=engine, expire_on_commit=False) as session:
        yield session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as db:
        yield db


SessionDependency = Annotated[Session, Depends(get_db)]
