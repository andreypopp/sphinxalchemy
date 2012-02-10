""" mysqlconnector connector"""

from __future__ import absolute_import

from mysql import connector
from mysql.connector import MySQLConnection
from sqlalchemy.dialects.mysql import mysqlconnector
from sphinxalchemy.dialect import SphinxDialect

__all__ = ("Dialect",)

class Connection(MySQLConnection):

    def get_autocommit(self):
        return False
    def set_autocommit(self, value):
        pass

    autocommit = property(get_autocommit, set_autocommit)

class DBAPIShim(object):

    def connect(self, *args, **kwargs):
        return Connection(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(connector, name)

class Dialect(SphinxDialect, mysqlconnector.MySQLDialect_mysqlconnector):

    def _get_default_schema_name(self, connection):
        pass

    def _detect_charset(self, connection):
        pass

    def _detect_casing(self, connection):
        pass

    def _detect_collations(self, connection):
        pass

    def _detect_ansiquotes(self, connection):
        self._server_ansiquotes = False

    @classmethod
    def dbapi(cls):
        return DBAPIShim()
