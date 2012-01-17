""" Dialect implementaiton for SphinxQL based on MySQLdb-Python protocol"""

from sqlalchemy.connectors import mysqldb
from sqlalchemy.engine import default
from sqlalchemy.sql import compiler

__all__ = ("SphinxDialect",)

class SphinxCompiler(compiler.SQLCompiler):
    pass

class SphinxDialect(default.DefaultDialect, mysqldb.MySQLDBConnector):

    name = "sphinx"
    statement_compiler = SphinxCompiler

    def do_rollback(self, connection):
        pass

    def do_commit(self, connection):
        pass

    def do_begin(self, connection):
        pass
