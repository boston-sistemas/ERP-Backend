from sqlalchemy.dialects import registry

# Registrar el dialecto con SQLAlchemy
registry.register("openedge.pyodbc", "openedge_sa.dialect", "OpenEdgeDialect")
registry.register("openedge.aioodbc", "openedge_sa.dialect", "OpenEdgeDialectAsync")
