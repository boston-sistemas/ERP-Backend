import click


@click.group()
def cli():
    """Execute utility functions"""
    pass


@cli.command()
def test():
    """Test database connection"""
    from db import test_database_connection

    test_database_connection()


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
    from db import create_promec_sequences, create_promec_tables

    create_promec_tables()
    create_promec_sequences()


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
