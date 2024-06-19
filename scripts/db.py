from config import settings
from sqlmodel import Session, create_engine

engine = create_engine(settings.DATABASE_URL)


def test_database_connection() -> bool:
    from sqlalchemy import text
    from sqlalchemy.exc import SQLAlchemyError

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


def import_models():
    from src.operations.models import Proveedor  # noqa: F401
    from src.security.models import Usuario  # noqa: F401


def create_tables():
    from sqlmodel import SQLModel

    import_models()
    SQLModel.metadata.create_all(engine)


def delete_tables():
    from sqlmodel import SQLModel

    import_models()
    SQLModel.metadata.drop_all(engine)


def generate_sql_create_tables(output_file: str, dialect: str):
    from sqlalchemy.dialects import oracle, postgresql
    from sqlalchemy.schema import CreateIndex, CreateTable
    from sqlmodel import SQLModel

    dialect_available = {"oracle": oracle, "postgresql": postgresql}
    engine_dialect = dialect_available[dialect].dialect()

    import_models()

    create_tables_statement = ""
    for model_table in SQLModel.metadata.sorted_tables:
        create_table_statement = CreateTable(model_table).compile(
            dialect=engine_dialect
        )
        create_tables_statement += str(create_table_statement)
        for index in model_table.indexes:
            create_index_statement = CreateIndex(index).compile(dialect=engine_dialect)
            create_tables_statement += str(create_index_statement) + "\n"

    if output_file:
        with open(output_file, "w") as file:
            file.write(create_tables_statement)
    else:
        print(create_tables_statement)


if __name__ == '__main__':
    test_database_connection()

