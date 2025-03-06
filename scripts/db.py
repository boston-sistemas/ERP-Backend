from config import settings
from loguru import logger
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_engine(settings.DATABASE_URL, echo=True)
promec_engine = create_engine(settings.PROMEC_DATABASE_URL, echo=True)
promec_silent_engine = create_engine(settings.PROMEC_DATABASE_URL, echo=False)
promec_async_silent_engine = create_async_engine(
    settings.PROMEC_DATABASE_URL_ASYNC,
    echo=False,
    query_cache_size=0,
)
pcp_async_silent_engine = create_async_engine(
    settings.PCP_DATABASE_URL_ASYNC,
    echo=False,
    query_cache_size=0,
)


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
        logger.info("Database connection successful")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Database connection unsuccessful, {str(e)}")
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
    Base.metadata.drop_all(engine, checkfirst=True)


def create_promec_tables() -> None:
    pass


def update_promec_tables() -> None:
    from sqlalchemy.exc import SQLAlchemyError

    from scripts.db_alter import Table, alter_tables

    tables: list[Table] = alter_tables(promec_silent_engine)

    with promec_silent_engine.connect() as db:
        for table in tables:
            logger.info(f"Actualizando tabla {table.name}...")
            stmt = table.query_update()
            for column in table.columns:
                try:
                    db.execute(text(f"{stmt}{column}"))
                    db.commit()
                    logger.info(
                        f"Se agregó la columna {column.name} a la tabla {table.name}."
                    )
                except SQLAlchemyError as e:
                    logger.error(
                        f"Error al actualizar tabla {table.name} con la columna {column.name}: {str(e)}"
                    )


async def update_promec_rows() -> None:
    from data_parser import DataParser

    data_parser = DataParser(
        promec_engine=promec_async_silent_engine,
        pcp_engine=pcp_async_silent_engine,
    )

    await data_parser.parse_yarn_purchase_entry_heavies()
    await data_parser.parse_period_yarn_purchase_entries(2024)
    await data_parser.parse_period_yarn_purchase_entries(2025)
    # await data_parser.parse_period_service_orders_weaving_from_pcp(2024)
    # await data_parser.parse_period_service_orders_weaving_from_pcp(2025)
    # await data_parser.parse_period_service_orders_supply_item_number(2024)
    # await data_parser.parse_period_service_orders_supply_item_number(2025)
    # await data_parser.parse_period_service_orders_weaving(2024)
    # await data_parser.parse_period_service_orders_weaving(2025)
    # await data_parser.parse_period_service_orders_weaving_stocks(2024)
    # await data_parser.parse_period_service_orders_weaving_stocks(2025)
    # await data_parser.parse_period_service_orders_weaving_stocks_lyc(2024)
    await promec_async_silent_engine.dispose()


async def inspect_tables() -> None:
    from data_inspector import DataInspector

    data_inspector = DataInspector(
        promec_engine=promec_async_silent_engine,
        pcp_engine=pcp_async_silent_engine,
    )

    # await data_inspector.inspect_period_yarn_weaving_dispatches(2022)
    # await data_inspector.inspect_period_yarn_weaving_dispatches(2023)
    # await data_inspector.inspect_period_yarn_weaving_dispatches(2024)
    # await data_inspector.inspect_period_yarn_weaving_dispatches(2025)
    await data_inspector.inspect_period_service_orders_weaving(2024)

    await promec_async_silent_engine.dispose()


async def update_name_tables() -> None:
    from data_watcher import DataWatcher

    data_watcher = DataWatcher(promec_engine=promec_async_silent_engine)

    await data_watcher.write_table_name()
    await promec_async_silent_engine.dispose()


async def update_row_counts() -> None:
    from data_watcher import DataWatcher

    data_watcher = DataWatcher(promec_engine=promec_async_silent_engine)
    output_file_names = "filtered_table_names.txt"
    row_count_file = "table_row_counts.txt"

    with open(output_file_names, "r") as file:
        table_names = [line.strip() for line in file]

    await data_watcher.save_initital_row_counts_parallel(
        table_names=table_names, output_file=row_count_file, max_workers=5
    )

    await promec_async_silent_engine.dispose()


async def detect_altered() -> None:
    from data_watcher import DataWatcher

    data_watcher = DataWatcher(promec_engine=promec_async_silent_engine)
    output_file_names = "filtered_table_names.txt"
    row_count_file = "table_row_counts.txt"

    with open(output_file_names, "r") as file:
        table_names = [line.strip() for line in file]

    current_counts = await data_watcher.get_table_row_counts_parallel(
        table_names=table_names, max_workers=5
    )

    alter_tables = await data_watcher.detect_altered_tables(
        current_counts, row_count_file
    )

    if alter_tables:
        logger.info("Tablas alteradas detectadas:")
        for table, prev, current in alter_tables:
            if prev == "nueva":
                logger.info(
                    f"Tabla nueva detectada: {table}, filas actuales: {current}."
                )
            else:
                logger.info(
                    f"Tabla alterada detectada: {table}, nuevos valores: {current - prev}"
                )
    else:
        logger.info("No se detectaron alteraciones en las tablas.")

    await promec_async_silent_engine.dispose()


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
