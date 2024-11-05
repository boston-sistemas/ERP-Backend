from sqlalchemy import Boolean, Connection, text
from sqlalchemy.connectors.aioodbc import aiodbcConnector
from sqlalchemy.connectors.pyodbc import PyODBCConnector
from sqlalchemy.engine.default import DefaultDialect
from sqlalchemy.ext.asyncio import AsyncConnection
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
        self, connection: Connection, table_name: str, schema: str = "PUB"
    ) -> bool:
        query = text(f"""
        SELECT 1
        FROM SYSPROGRESS.SYSTABLES
        WHERE OWNER = '{schema}' AND TBL = '{table_name}'
        """)
        result = connection.execute(query).fetchone()
        return result is not None


class OpenEdgeDialectAsync(aiodbcConnector, OpenEdgeDialect):
    driver = "aioodbc"
    supports_statement_cache = True

    def initialize(self, connection):
        # Override to prevent calling getinfo on the async connection
        self.server_version_info = (0, 0, 0)

    def _get_server_version_info(self, connection):
        # Do not attempt to get server version info
        self.server_version_info = (0, 0, 0)

    async def has_table(
        self, connection: AsyncConnection, table_name: str, schema: str = "PUB"
    ) -> bool:
        query = text(f"""
        SELECT 1
        FROM SYSPROGRESS.SYSTABLES
        WHERE OWNER = '{schema}' AND TBL = '{table_name}'
        """)
        result = (await connection.execute(query)).fetchone()
        return result is not None
