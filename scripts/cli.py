import asyncio

import click


@click.group()
def cli():
    """Execute utility functions"""
    pass


@cli.command()
def ping_db():
    """Test main database connection"""
    from db import engine, test_database_connection

    test_database_connection(engine)


@cli.command()
def ping_promec_db():
    """Test promec database connection"""
    from db import promec_engine, test_database_connection

    test_database_connection(promec_engine)


@cli.command()
def init_db():
    """Initialize main database: create tables and sequences"""
    from db import create_tables

    create_tables()


@cli.command()
def drop_tables():
    """Drop all tables"""
    from db import delete_tables

    delete_tables()


@cli.command()
def init_promec_db():
    """Initialize promec database: create tables and sequences"""
    from db import create_promec_sequences, create_promec_tables, update_promec_tables

    create_promec_tables()
    update_promec_tables()
    create_promec_sequences()


@cli.command()
def pruebas():
    from db import update_promec_rows

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(update_promec_rows())


@cli.command()
def inspect():
    from db import inspect_tables

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(inspect_tables())


@cli.command()
def populate_data_test():
    from test.populate_purchase_order import populate_purchase_order

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(populate_purchase_order())


@cli.command()
def update_name_tables():
    from db import update_name_tables

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(update_name_tables())


@cli.command()
def update_row_counts():
    from db import update_row_counts

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(update_row_counts())


@cli.command()
def detect_altered():
    from db import detect_altered

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(detect_altered())


@cli.command()
@click.option("-o", "--output", help="Output file name", default="", required=False)
@click.option(
    "--dialect",
    type=click.Choice(["postgresql", "oracle"]),
    default="postgresql",
    help="SQL dialect",
)
def generate_sql(output, dialect):
    """Generate SQL create tables"""
    from db import generate_sql_create_tables

    generate_sql_create_tables(output, dialect)


@cli.command()
def insert_data():
    """Insert dummy data"""
    from dummy_data import generate_dummy_data

    generate_dummy_data()


if __name__ == "__main__":
    cli()
