from sqlalchemy.types import Boolean, Date, DateTime, Integer, String, TypeDecorator


class OpenEdgeInteger(Integer):
    __visit_name__ = "INTEGER"


class OpenEdgeString(String):
    __visit_name__ = "VARCHAR"


class OpenEdgeDateTime(DateTime):
    __visit_name__ = "TIMESTAMP"


class OpenEdgeDate(Date):
    __visit_name__ = "DATE"


class OpenEdgeBoolean(TypeDecorator):
    impl = Boolean

    def get_col_spec(self, **kw):
        return "BIT"

    def process_bind_param(self, value, dialect):
        if value is not None:
            return int(value)
        return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return bool(value)
        return None
