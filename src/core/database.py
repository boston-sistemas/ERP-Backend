from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import DeclarativeBase
from sqlmodel import Session, create_engine

from src.core.config import settings

engine = create_engine(settings.DATABASE_URL)


class Base(DeclarativeBase):
    pass


def get_session() -> Generator[Session, None, None]:
    with Session(bind=engine, expire_on_commit=False) as session:
        yield session


SessionDependency = Annotated[Session, Depends(get_session)]
