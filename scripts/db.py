from config import settings
from sqlalchemy import Engine, create_engine, text

engine = create_engine(settings.DATABASE_URL, echo=True)
promec_engine = create_engine(settings.PROMEC_DATABASE_URL, echo=True)


def test_database_connection(_engine: Engine) -> bool:
    from sqlalchemy.exc import SQLAlchemyError

    dialect = _engine.dialect.name

    dialect_available = {
        "oracle": "SELECT 1 FROM DUAL",
        "postgresql": "SELECT 1",
        "openedge": "SELECT 1 FROM SYSPROGRESS.SYSTABLES",
    }

    stmt = dialect_available.get(dialect, "")

    if not stmt:
        raise ValueError("Dialect not supported")

    try:
        with _engine.connect() as db:
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


def create_tables() -> None:
    from src.core.database import Base  # noqa: F401

    import_models()
    Base.metadata.create_all(engine)


def delete_tables() -> None:
    from src.core.database import Base  # noqa: F401

    import_models()
    Base.metadata.drop_all(engine)


def create_promec_tables() -> None:
    pass


def create_promec_sequences() -> None:
    from src.core.database import PromecBase  # noqa: F401
    from src.operations.sequences import product_id_seq  # noqa: F401

    PromecBase.metadata.create_all(promec_engine)


def delete_promec_sequences() -> None:
    from src.core.database import PromecBase  # noqa: F401
    from src.operations.sequences import product_id_seq  # noqa: F401

    PromecBase.metadata.drop_all(promec_engine)


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
    # Any method called here will be executed
    pass
