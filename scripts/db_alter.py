from sqlalchemy.engine.base import Engine


class TypeColumn:
    def __init__(self, name: str):
        self.name = name


class TypeVarchar(TypeColumn):
    def __init__(self, length: int):
        super().__init__(name="VARCHAR")
        self.length = length

    def __str__(self):
        return f"{self.name}({self.length})"


class TypeNumeric(TypeColumn):
    def __init__(self, precision: int, scale: int):
        super().__init__(name="NUMERIC")
        self.precision = precision
        self.scale = scale

    def __str__(self):
        return f"{self.name}({self.precision}, {self.scale})"


class TypeBit(TypeColumn):
    def __init__(self):
        super().__init__(name="BIT")

    def __str__(self):
        return self.name


class TypeInteger(TypeColumn):
    def __init__(self):
        super().__init__(name="INTEGER")

    def __str__(self):
        return self.name


class Column:
    def __init__(self, name: str, type_column: TypeColumn):
        self.name = name
        self.type_column = type_column

    def __str__(self):
        return f"{self.name} {self.type_column}"


class Table:
    def __init__(self, name: str, columns: list[Column]):
        self.name = name
        self.columns = columns

    def query_update(self):
        query = f"ALTER TABLE PUB.{self.name} ADD "
        return query


def alter_tables(engine: Engine) -> list[Table]:
    tables = [
        Table(
            name="almcmovi",
            columns=[
                Column(name="loteprov", type_column=TypeVarchar(length=30)),
                Column(name="lotem", type_column=TypeVarchar(length=30)),
            ],
        ),
        Table(
            name="almdmovi",
            columns=[
                Column(
                    name="pesobrtoguia", type_column=TypeNumeric(precision=15, scale=5)
                ),
                Column(name="flgpesaje", type_column=TypeBit()),
                Column(name="nrogrupoingr", type_column=TypeInteger()),
                Column(name="nroitemingr", type_column=TypeInteger()),
                Column(name="periodoingr", type_column=TypeInteger()),
                Column(name="loteprov", type_column=TypeVarchar(length=30)),
                Column(name="nroiteminsumoos", type_column=TypeInteger()),
                Column(name="codprod2", type_column=TypeVarchar(length=12)),
            ],
        ),
        Table(
            name="opehilado",
            columns=[
                Column(name="nroitm", type_column=TypeInteger()),
                Column(name="periodo", type_column=TypeInteger()),
                Column(name="flgdesp", type_column=TypeBit()),
                Column(name="nrobolsasrest", type_column=TypeInteger()),
                Column(name="nroconosrest", type_column=TypeInteger()),
                Column(name="loteprov", type_column=TypeVarchar(length=30)),
            ],
        ),
        Table(
            name="almstkserv",
            columns=[
                Column(name="nroitm", type_column=TypeInteger()),
                Column(
                    name="cantidad_dada", type_column=TypeNumeric(precision=15, scale=5)
                ),
                Column(name="es_complemento", type_column=TypeBit()),
                Column(name="proveedor_hilado_id", type_column=TypeVarchar(length=22)),
                Column(name="status_param_id", type_column=TypeInteger()),
                Column(name="codprod2", type_column=TypeVarchar(length=12)),
            ],
        ),
        Table(
            name="almtejido",
            columns=[
                Column(name="protincol", type_column=TypeVarchar(length=40)),
            ],
        ),
        Table(
            name="opecosmp",
            columns=[
                Column(name="status_param_id", type_column=TypeInteger()),
            ],
        ),
        Table(
            name="opedosmp",
            columns=[
                Column(name="status_param_id", type_column=TypeInteger()),
            ],
        ),
        Table(
            name="operectej",
            columns=[
                Column(name="nro_cabos", type_column=TypeInteger()),
                Column(name="galga", type_column=TypeNumeric(precision=15, scale=5)),
                Column(name="diametro", type_column=TypeNumeric(precision=15, scale=5)),
                Column(
                    name="longitud_malla",
                    type_column=TypeNumeric(precision=15, scale=5),
                ),
            ],
        ),
        Table(
            name="admdtabla",
            columns=[
                Column(name="slug", type_column=TypeVarchar(length=80)),
            ],
        ),
        Table(
            name="opetarserv",
            columns=[
                Column(name="id", type_column=TypeInteger()),
            ],
        ),
    ]

    return tables
