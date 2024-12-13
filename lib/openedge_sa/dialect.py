from typing import Any

from sqlalchemy import Boolean, Connection, text
from sqlalchemy.connectors.aioodbc import aiodbcConnector
from sqlalchemy.connectors.pyodbc import PyODBCConnector
from sqlalchemy.engine.default import DefaultDialect
from sqlalchemy.engine.interfaces import DBAPIConnection
from sqlalchemy.types import Date, DateTime, Integer, String

from .compiler import (
    OpenEdgeCompiler,
    OpenEdgeDDLCompiler,
    OpenEdgeIdentifierPreparer,
    OpenEdgeTypeCompiler,
)
from .types import (
    OpenEdgeBoolean,
    OpenEdgeDate,
    OpenEdgeDateTime,
    OpenEdgeInteger,
    OpenEdgeString,
)


class OpenEdgeDialectBase(PyODBCConnector, DefaultDialect):
    name = "openedge"
    supports_native_boolean = False  # OpenEdge does not support native booleans
    supports_sane_rowcount = True
    supports_unicode_statements = True
    supports_statement_cache = True
    supports_sequences = True

    statement_compiler = OpenEdgeCompiler
    ddl_compiler = OpenEdgeDDLCompiler
    preparer = OpenEdgeIdentifierPreparer
    type_compiler = OpenEdgeTypeCompiler

    colspecs = {
        Integer: OpenEdgeInteger,
        String: OpenEdgeString,
        DateTime: OpenEdgeDateTime,
        Date: OpenEdgeDate,
        Boolean: OpenEdgeBoolean,
    }

    ischema_names = {
        "INTEGER": Integer,
        "CHAR": String,
        "VARCHAR": String,
        "DATE": Date,
        "TIMESTAMP": DateTime,
        "BIT": Boolean,
    }


class OpenEdgeDialect(OpenEdgeDialectBase):
    driver = "pyodbc"
    supports_statement_cache = True

    def has_table(
        self,
        connection: Connection,
        table_name: str,
        **kw: Any,
    ) -> bool:
        schema: str = "PUB"
        query = text(f"""
        SELECT 1
        FROM SYSPROGRESS.SYSTABLES
        WHERE OWNER = '{schema}' AND TBL = '{table_name}'
        """)
        result = connection.execute(query).fetchone()
        return result is not None

    def has_sequence(
        self,
        connection: Connection,
        sequence_name: str,
        **kw: Any,
    ) -> bool:
        schema: str = "PUB"
        query = text(f"""
        SELECT 1
        FROM SYSPROGRESS.SYSSEQUENCES
        WHERE "SEQ-OWNER" = '{schema}' AND "SEQ-NAME" = '{sequence_name}'
        """)
        result = connection.execute(query).fetchone()
        return result is not None

    def do_ping(self, dbapi_connection: DBAPIConnection) -> bool:
        cursor = None
        try:
            cursor = dbapi_connection.cursor()
            try:
                cursor.execute("SELECT 1 FROM SYSPROGRESS.SYSCALCTABLE WHERE 1=0")
            finally:
                cursor.close()
        except self.loaded_dbapi.Error:
            raise
        except Exception:
            # TODO: Handle only sqlalchemy.exc.OperationalError to identify disconnection causes.
            return False
        return True

    def is_disconnect(self, e, connection, cursor):
        error_codes = ["08S01", "HYT00", "08003"]
        if isinstance(e, self.loaded_dbapi.Error):
            error_code = getattr(e, "args", [None])[0]
            if error_code in error_codes:
                return True
        if "Socket closed" in str(e):
            return True
        if "connection is not available" in str(e):
            return True
        return False


class OpenEdgeDialectAsync(aiodbcConnector, OpenEdgeDialect):
    driver = "aioodbc"
    supports_statement_cache = True

    def initialize(self, connection):
        # Override to prevent calling getinfo on the async connection
        self.server_version_info = (0, 0, 0)

    def _get_server_version_info(self, connection):
        # Do not attempt to get server version info
        self.server_version_info = (0, 0, 0)
