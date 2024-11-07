from config import settings
from sqlalchemy import create_engine, text

engine = create_engine(settings.DATABASE_URL, echo=True)


def test_database_connection() -> bool:
    from sqlalchemy.exc import SQLAlchemyError

    dialect = engine.dialect.name
    stmt = "SELECT 1 FROM DUAL" if dialect == "oracle" else "SELECT 1"

    try:
        with engine.connect() as db:
            db.execute(text(stmt))

        print("\t***** Database connection successful *****")
        return True
    except SQLAlchemyError as e:
        print("SQLAlchemy Error:", str(e))
        print("\t***** Database connection unsuccessful *****")
        return False


def import_models() -> None:
    from src.operations.models import Proveedor  # noqa: F401
    from src.security.models import Usuario  # noqa: F401


def create_all() -> None:
    from src.core.database import Base  # noqa: F401
    from src.operations.sequences import product_id_seq  # noqa: F401

    import_models()
    Base.metadata.create_all(engine)


def delete_tables() -> None:
    from src.core.database import Base  # noqa: F401

    import_models()
    Base.metadata.drop_all(engine)


def delete_sequences() -> None:
    from src.core.database import Base  # noqa: F401
    from src.operations.sequences import product_id_seq  # noqa: F401

    Base.metadata.drop_all(engine)


def generate_sql_create_tables(output_file: str, dialect: str) -> None:
    from sqlalchemy.dialects import oracle, postgresql
    from sqlalchemy.schema import CreateIndex, CreateTable

    from src.core.database import Base

    dialect_available = {"oracle": oracle, "postgresql": postgresql}
    engine_dialect = dialect_available.get(dialect, postgresql).dialect()

    import_models()

    create_tables_statement = ""
    for model_table in Base.metadata.sorted_tables:
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


if __name__ == "__main__":
    test_database_connection()
    create_all()
    delete_tables()
    delete_sequences()
    generate_sql_create_tables()
