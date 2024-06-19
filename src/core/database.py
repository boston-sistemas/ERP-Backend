from collections.abc import Generator
from typing import Annotated

from core.config import settings
from fastapi import Depends
from sqlmodel import Session, create_engine
from sqlalchemy.orm import DeclarativeBase


engine = create_engine(settings.DATABASE_URL)

class Base(DeclarativeBase):
    pass


def get_session() -> Generator[Session, None, None]:
    with Session(bind=engine, expire_on_commit=False) as session:
        yield session

SessionDependency = Annotated[Session, Depends(get_session)]
