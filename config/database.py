from collections.abc import Generator

from sqlmodel import Session, create_engine

from config.settings import settings

engine = create_engine(settings.DATABASE_URL)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session