from collections.abc import Generator

from sqlmodel import Session, create_engine

from settings import settings

engine = create_engine(settings.DATABASE_URL)

def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

def test_database_connection() -> bool:
    from sqlalchemy.exc import SQLAlchemyError
    from sqlalchemy import text
    
    try:
        with Session(engine) as session:
            statement = text("select 1")
            session.exec(statement)
            session.commit()
            print("\t***** Database connection successful *****")
        return True
    except SQLAlchemyError as e:
        print("SQLAlchemy Error:", str(e))
        print("\t***** Database connection unsuccessful *****")
        return False

if __name__ == "__main__":
    test_database_connection()