from setuptools import find_packages, setup

setup(
    name="openedge_sa",
    version="0.1",
    packages=find_packages(),
    install_requires=["sqlalchemy", "pyodbc", "aioodbc"],
    entry_points={
        "sqlalchemy.dialects": [
            "openedge.pyodbc = openedge_sa.dialect:OpenEdgeDialect",
            "openedge.aioodbc = openedge_sa.dialect:OpenEdgeDialectAsync",
        ]
    },
)
