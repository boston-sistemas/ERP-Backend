import sys

from sqlmodel import Session
from database import engine

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
    from mecsa_erp.area_operaciones.modulo0.models import (
        Proveedor, 
        OrdenCompra, 
        Producto, 
        Hilado, 
        OrdenCompraDetalle
    )

def create_tables():
    from sqlmodel import SQLModel
    import_models()
    SQLModel.metadata.create_all(engine)

def delete_tables():
    from sqlmodel import SQLModel
    import_models()
    SQLModel.metadata.drop_all(engine) 

if __name__ == "__main__":
    utils = {
        "test" : test_database_connection,
        "create": create_tables,
        "delete": delete_tables,
        }
    
    option = sys.argv[1] if len(sys.argv) > 1 else None  
    
    if (not option) or (option not in utils):
        sys.exit("specifies a function to execute: " + " | ".join(utils.keys()))
     
    utils[option]()