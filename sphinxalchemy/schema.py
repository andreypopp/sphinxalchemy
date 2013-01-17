""" Schema constructs for Sphinx"""

from sqlalchemy.schema import Table, Column
from sqlalchemy import types
from sqlalchemy.sql import expression

from sphinxalchemy.sphinxql import select, replace

__all__ = ("Index", "Attribute", "ArrayAttribute")


class Index(Table):
    """ Sphinx index metadata

    Accepted arguments are the same as :class:`sqlalchemy.schema.Table` accepts.
    """

    def __init__(self, *args, **kwargs):
        super(Index, self).__init__(*args, **kwargs)

    def select(self, whereclause=None, **params):
        return select([self], whereclause, **params)

    def replace(self, values=None, inline=False, **kwargs):
        """Generate an :func:`.replace` construct against this
        :class:`.Index`.

        E.g.::

            index.replace().values(name='foo')

        See :func:`.replace` for argument and usage information.

        """

        return replace(self, values=values, inline=inline, **kwargs)


class Attribute(Column):
    """ Sphinx index scalar attribute metadata

    Accepted arguments are the same as :class:`sqlalchemy.schema.Column`
    accepts.
    """

    def __init__(self, *args, **kwargs):
        args = list(args)
        if len(args) > 1 and isinstance(args[1], (types.TypeEngine, type)):
            args.pop(1)
        kwargs["type_"] = types.Integer()
        super(Attribute, self).__init__(*args, **kwargs)


class ArrayAttribute(Column):
    """ Sphinx index array attribute metadata

    Accepted arguments are the same as :class:`sqlalchemy.schema.Column`
    accepts.
    """

    def __init__(self, *args, **kwargs):
        args = list(args)
        if len(args) > 1 and isinstance(args[1], (types.TypeEngine, type)):
            args.pop(1)
        kwargs["type_"] = ArrayAttributeType()
        super(ArrayAttribute, self).__init__(*args, **kwargs)

    def _bind_param(self, operator, obj):
        return expression._BindParamClause(
            None, obj, _compared_to_operator=operator,
            _compared_to_type=types.Integer(), unique=True)


class ArrayAttributeType(types.TypeDecorator):

    impl = types.String

    def process_bind_param(self, value, dialect):
        return ",".join(map(str, value))

    def process_result_value(self, value, dialect):
        return map(int, value.split(","))

    def copy(self):
        return ArrayAttributeType()
