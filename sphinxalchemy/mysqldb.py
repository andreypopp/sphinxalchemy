""" MySQLdb connector"""

from __future__ import absolute_import

from sqlalchemy.connectors import mysqldb
from sphinxalchemy.dialect import SphinxDialect

__all__ = ("Dialect",)

class Dialect(SphinxDialect, mysqldb.MySQLDBConnector):
    pass
