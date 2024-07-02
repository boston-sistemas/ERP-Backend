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
def create():
    """Create all tables"""
    from db import create_tables

    create_tables()


@cli.command()
def delete():
    """Delete all tables"""
    from db import delete_tables

    delete_tables()


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
