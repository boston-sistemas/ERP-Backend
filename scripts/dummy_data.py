from sqlmodel import Session, create_engine

from scripts.config import settings

engine = create_engine(settings.DATABASE_URL)

from src.operations.models import (  # noqa: E402
    Color,
    Crudo,
    OrdenServicioTejeduria,
    OrdenServicioTejeduriaDetalle,
    OrdenServicioTejeduriaDetalleEstado,
    OrdenServicioTejeduriaEstado,
    Proveedor,
    ProveedorServicio,
    Servicio,
    Tejido,
)
from src.security.models import Acceso, Rol, RolAcceso  # noqa: E402


def insert_data(generate_data):
    def wrapper(*args, **kwargs):
        model, objects = generate_data(*args, **kwargs)

        with Session(engine) as session:
            data = []
            for object in objects:
                data.append(model(**object))

            session.add_all(data)
            session.commit()

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
def generate_orden_servicio_tejeduria_estado():
    objects = [{"estado": "PENDIENTE"}, {"estado": "CERRADO"}, {"estado": "LIQUIDADO"}]

    return OrdenServicioTejeduriaEstado, objects


@insert_data
def generate_orden_servicio_tejeduria_detalle_estado():
    objects = [
        {"estado": "NO INICIADO"},
        {"estado": "EN CURSO"},
        {"estado": "DETENIDO"},
        {"estado": "LISTO"},
    ]

    return OrdenServicioTejeduriaDetalleEstado, objects


@insert_data
def generate_tejido():
    objects = get_objects_from_csv("tejido.csv")
    return Tejido, objects


@insert_data
def generate_proveedor():
    objects = get_objects_from_csv("proveedor.csv")
    return Proveedor, objects


@insert_data
def generate_servicio():
    objects = [
        {"nombre": "TEJEDURIA"},
        {"nombre": "TINTORERIA"},
    ]
    return Servicio, objects


@insert_data
def generate_proveedor_servicio():
    objects = get_objects_from_csv("proveedor_servicio.csv")
    return ProveedorServicio, objects


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
        {"nombre": "MECSA_OPERACIONES"},
        {"nombre": "PROVEEDOR"},
    ]
    return Rol, objects


@insert_data
def generate_acceso():
    objects = [
        {"nombre": "REPORTE_STOCK"},
        {"nombre": "REVISION_STOCK"},
        {"nombre": "PROGRAMACION_TINTORERIA"},
    ]

    return Acceso, objects


@insert_data
def generate_rol_acceso():
    objects = [
        {"rol_id": 1, "acceso_id": 2},
        {"rol_id": 1, "acceso_id": 3},
        {"rol_id": 2, "acceso_id": 1},
    ]

    return RolAcceso, objects


def generate_dummy_data():
    generate_proveedor()
    generate_servicio()
    generate_proveedor_servicio()
    generate_tejido()
    generate_crudo()
    generate_orden_servicio_tejeduria_estado()
    generate_orden_servicio_tejeduria_detalle_estado()
    generate_orden_servicio_tejeduria()
    generate_orden_servicio_tejeduria_detalle()
    generate_color()

    generate_rol()
    generate_acceso()
    generate_rol_acceso()


if __name__ == "__main__":
    generate_dummy_data()
