from sqlalchemy.sql.compiler import (
    DDLCompiler,
    GenericTypeCompiler,
    IdentifierPreparer,
    SQLCompiler,
)


class OpenEdgeCompiler(SQLCompiler):
    def visit_now_func(self, fn, **kw):
        # Cambia `func.now()` a `SYSDATE` para OpenEdge
        return "SYSDATE"

    def visit_sequence(self, sequence, **kw):
        txt = f"PUB.{sequence.name}.NEXTVAL FROM SYSPROGRESS.SYSCALCTABLE"
        return txt

    def limit_clause(self, select, **kw):
        text = ""

        if select._offset_clause is not None:
            text += f"\n OFFSET {self.process(select._offset_clause, literal_binds=True)} ROWS"

        if select._limit_clause is not None:
            text += f"\n FETCH FIRST {self.process(select._limit_clause, literal_binds=True)} ROWS ONLY"

        return text

    def fetch_clause(
        self,
        select,
        fetch_clause=None,
        require_offset=False,
        **kw,
    ):
        text = ""
        if fetch_clause is None:
            fetch_clause = select._fetch_clause

        if select._offset_clause is not None:
            offset_clause = select._offset_clause
            text += f"\n OFFSET {self.process(offset_clause, literal_binds=True)} ROWS"
        elif require_offset:
            text += "\n OFFSET 0 ROWS"

        if fetch_clause is not None:
            text += f"\n FETCH FIRST {self.process(fetch_clause, literal_binds=True)} ROWS ONLY"

        return text


class OpenEdgeTypeCompiler(GenericTypeCompiler):
    def visit_datetime(self, type_, **kw):
        return "TIMESTAMP"

    def visit_boolean(self, type_, **kw):
        return "BIT"


class OpenEdgeDDLCompiler(DDLCompiler):
    def visit_primary_key_constraint(self, constraint, **kw):
        if constraint.name is None:
            constraint.name = f"pk_{constraint.table.name}"

        return super().visit_primary_key_constraint(constraint, **kw)

    def visit_foreign_key_constraint(self, constraint, **kw):
        if constraint.name is None:
            local_table = constraint.table.name
            local_columns = "_".join(col.name for col in constraint.columns)
            constraint.name = f"fk_{local_table}_{local_columns}"

        return super().visit_foreign_key_constraint(constraint, **kw)

    def visit_unique_constraint(self, constraint, **kw):
        if constraint.name is None:
            table_name = constraint.table.name
            columns = "_".join(col.name for col in constraint.columns)
            constraint.name = f"uq_{table_name}_{columns}"

        return super().visit_unique_constraint(constraint, **kw)


class OpenEdgeIdentifierPreparer(IdentifierPreparer):
    pass
