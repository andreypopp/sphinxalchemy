""" Constructs for SphinxQL generation"""

from sqlalchemy.sql import expression

__all__ = ("SelectClause", "select")

class SelectClause(expression.SelectClause):
    pass

def select(*args, **kwargs):
    return SelectClause(*args, **kwargs)
