import functions
from config.database import get_session
from mecsa_erp.area_operaciones.core.models import Proveedor
from mecsa_erp.area_operaciones.modulo0.models import (
    Crudo,
    OrdenServicioTejeduria,
    OrdenServicioTejeduriaDetalle,
    OrdenServicioTejeduriaDetalleEstado,
    OrdenServicioTejeduriaEstado,
    Tejido,
)


def insert_data(generate_data):
    def wrapper(*args, **kwargs):
        model, objects = generate_data(*args, **kwargs)

        session = next(get_session())
        data = []
        for object in objects:
            data.append(model(**object))

        session.add_all(data)
        session.commit()

    return wrapper


def get_objects_from_csv(filename, converters=None):
    import csv

    path = functions.settings.BASE_DIR + "utils/data/" + filename

    objects = []
    with open(path, "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for object in reader:
            if(converters):
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
def generate_crudo():
    objects = get_objects_from_csv("crudo.csv")
    return Crudo, objects

@insert_data
def generate_orden_servicio_tejeduria():
    objects = get_objects_from_csv("orden_servicio_tejeduria.csv")
    return OrdenServicioTejeduria, objects

@insert_data
def generate_orden_servicio_tejeduria_detalle():
    converters = {
        "es_complemento": lambda value: value == "True"
    }
    objects = get_objects_from_csv("orden_servicio_tejeduria_detalle.csv", converters)
    return OrdenServicioTejeduriaDetalle, objects

def generate_dummy_data():
    generate_proveedor()
    generate_tejido()
    generate_crudo()
    generate_orden_servicio_tejeduria_estado()
    generate_orden_servicio_tejeduria_detalle_estado()
    generate_orden_servicio_tejeduria()
    generate_orden_servicio_tejeduria_detalle()

if __name__ == "__main__":
    generate_dummy_data()