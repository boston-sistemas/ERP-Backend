from config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

engine = create_engine(settings.DATABASE_URL, echo=True)

from src.operations.models import (  # noqa: E402
    Color,
    Crudo,
    EspecialidadEmpresa,
    OrdenServicioTejeduria,
    OrdenServicioTejeduriaDetalle,
    Proveedor,
    ProveedorEspecialidad,
    Tejido,
)
from src.security.models import Acceso, ModuloSistema, Rol, RolAcceso  # noqa: E402


def insert_data(generate_data):
    def wrapper(*args, **kwargs):
        model, objects = generate_data(*args, **kwargs)

        with Session(engine) as db:
            data = []
            for object in objects:
                data.append(model(**object))

            db.add_all(data)
            db.commit()

    return wrapper


def get_objects_from_csv(filename, converters=None):
    import csv

    path = settings.BASE_DIR + "scripts/data/" + filename

    objects = []
    with open(path, "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for object in reader:
            if converters:
                for key in converters:
                    object[key] = converters[key](object[key])

            objects.append(object)

    return objects


@insert_data
def generate_tejido():
    objects = get_objects_from_csv("tejido.csv")
    return Tejido, objects


@insert_data
def generate_proveedor():
    objects = get_objects_from_csv("proveedor.csv")
    return Proveedor, objects


@insert_data
def generate_especialidad():
    objects = [
        {"nombre": "TEJEDURIA"},
        {"nombre": "TINTORERIA"},
    ]
    return EspecialidadEmpresa, objects


@insert_data
def generate_proveedor_especialidad():
    objects = get_objects_from_csv("proveedor_especialidad.csv")
    return ProveedorEspecialidad, objects


@insert_data
def generate_crudo():
    objects = get_objects_from_csv("crudo.csv")
    return Crudo, objects


@insert_data
def generate_orden_servicio_tejeduria():
    objects = get_objects_from_csv("orden_servicio_tejeduria.csv")
    return OrdenServicioTejeduria, objects


@insert_data
def generate_orden_servicio_tejeduria_detalle():
    converters = {"es_complemento": lambda value: value == "True"}
    objects = get_objects_from_csv("orden_servicio_tejeduria_detalle.csv", converters)
    return OrdenServicioTejeduriaDetalle, objects


@insert_data
def generate_color():
    objects = get_objects_from_csv("color.csv")
    return Color, objects


@insert_data
def generate_rol():
    objects = [
        {"nombre": "MASTER"},
        {"nombre": "Operaciones 1"},
        {"nombre": "Operaciones 2"},
        {"nombre": "Tejedor"},
    ]
    return Rol, objects


@insert_data
def generate_rol_acceso():
    objects = [
        {"rol_id": 1, "acceso_id": 1},
        {"rol_id": 1, "acceso_id": 2},
        {"rol_id": 1, "acceso_id": 3},
        {"rol_id": 1, "acceso_id": 4},
        {"rol_id": 1, "acceso_id": 5},
        {"rol_id": 1, "acceso_id": 6},
        {"rol_id": 1, "acceso_id": 7},
        {"rol_id": 1, "acceso_id": 8},
        {"rol_id": 2, "acceso_id": 1},
        {"rol_id": 2, "acceso_id": 2},
        {"rol_id": 3, "acceso_id": 4},
        {"rol_id": 3, "acceso_id": 5},
        {"rol_id": 4, "acceso_id": 6},
    ]

    return RolAcceso, objects


@insert_data
def generate_modulos():
    objects = [
        {"name": "Operaciones"},
        {"name": "Tejeduria"},
        {"name": "Seguridad"},
    ]
    return ModuloSistema, objects


@insert_data
def generate_accesos():
    modulos = {"Operaciones": 1, "Tejeduria": 2, "Seguridad": 3}

    objects = [
        {
            "nombre": "EPT",
            "scope": "operaciones",
            "modulo_id": modulos["Operaciones"],
            "view_path": "/operaciones/programacion-tintoreria",
        },
        {
            "nombre": "Revision de Stock",
            "scope": "operaciones",
            "modulo_id": modulos["Operaciones"],
            "view_path": "/operaciones/revision-stock",
        },
        {
            "nombre": "Panel",
            "scope": "operaciones",
            "modulo_id": modulos["Operaciones"],
            "view_path": "/operaciones/panel",
        },
        {
            "nombre": "O.S. Tejeduria",
            "scope": "operaciones",
            "modulo_id": modulos["Operaciones"],
            "view_path": "/operaciones/ordenes-servicio",
        },
        {
            "nombre": "Mov. Ingreso Crudo",
            "scope": "operaciones",
            "modulo_id": modulos["Operaciones"],
            "view_path": "/operaciones/movimientos-ingreso-crudo",
        },
        {
            "nombre": "Reporte de Stock",
            "scope": "tejeduria",
            "modulo_id": modulos["Tejeduria"],
            "view_path": "/tejeduria/reporte-stock",
        },
        {
            "nombre": "Roles",
            "scope": "seguridad",
            "modulo_id": modulos["Seguridad"],
            "view_path": "/seguridad/roles",
        },
        {
            "nombre": "Usuarios",
            "scope": "seguridad",
            "modulo_id": modulos["Seguridad"],
            "view_path": "/seguridad/usuarios",
        },
    ]
    return Acceso, objects


def generate_dummy_data():
    generate_proveedor()
    generate_especialidad()
    generate_proveedor_especialidad()
    generate_tejido()
    generate_crudo()
    generate_orden_servicio_tejeduria()
    generate_orden_servicio_tejeduria_detalle()
    generate_color()
    generate_modulos()
    generate_rol()
    generate_accesos()
    generate_rol_acceso()


if __name__ == "__main__":
    generate_dummy_data()
