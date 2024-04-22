import functions
import argparse
from sqlmodel import Session
from config.database import engine
from dummy_data import generate_dummy_data

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

def import_models():
    from mecsa_erp.area_operaciones.core.models import Proveedor
    from mecsa_erp.area_operaciones.modulo0.models import Hilado
    from mecsa_erp.area_operaciones.modulo1.models import OrdenServicioTejeduriaDetalleReporteLog
    from mecsa_erp.usuarios.models import Usuario

def create_tables():
    from sqlmodel import SQLModel
    import_models()
    SQLModel.metadata.create_all(engine)

def delete_tables():
    from sqlmodel import SQLModel
    import_models()
    SQLModel.metadata.drop_all(engine)
    
def generate_sql_create_tables():
    from sqlalchemy.schema import CreateTable, CreateIndex
    from sqlalchemy.dialects import postgresql, oracle 
    from sqlmodel import SQLModel
    
    output_file, dialect = args.output, args.dialect
    dialect_available = {'oracle': oracle, 'postgresql': postgresql}
    engine_dialect = dialect_available[dialect].dialect()
    
    import_models()

    create_tables_statement = ""
    for model_table in SQLModel.metadata.sorted_tables:
        create_table_statement = CreateTable(model_table).compile(dialect=engine_dialect)
        create_tables_statement += str(create_table_statement) 
        for index in model_table.indexes:
            create_index_statement = CreateIndex(index).compile(dialect=engine_dialect)
            create_tables_statement += str(create_index_statement) + '\n'
    
    if output_file:
        with open(output_file, "w") as file:
            file.write(create_tables_statement)
    else:
        print(create_tables_statement)

def initialize_args():
    parser = argparse.ArgumentParser(description="Execute utility functions")
    subparsers = parser.add_subparsers(title='commands', required=True, dest='option')
    subparsers.add_parser('test', help='Test database connection')
    subparsers.add_parser('create', help='Create all tables')
    subparsers.add_parser('delete', help='Delete all tables')
    subparsers.add_parser('insert_data', help='Insert dummy data')
    
    parser_generate_sql = subparsers.add_parser('generate_sql', help='Generate SQL create tables')
    parser_generate_sql.add_argument("-o", "--output", help="Output file name", default='', required=False)
    parser_generate_sql.add_argument("--dialect", choices=["postgresql", "oracle"], help="SQL dialect", default='postgresql', required=False)
    
    global args
    args = parser.parse_args()

if __name__ == "__main__":
    
    utils = {
        "test" : test_database_connection,
        "create": create_tables,
        "delete": delete_tables,
        "generate_sql": generate_sql_create_tables,
        "insert_data": generate_dummy_data,
        }
    
    initialize_args()
    
    utils[args.option]()