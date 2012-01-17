""" Schema constructs for Sphinx"""

from sqlalchemy.schema import Table, Column
from sqlalchemy import types

__all__ = ("Index", "Attribute")

class Index(Table):

    def __init__(self, *args, **kwargs):
        super(Index, self).__init__(*args, **kwargs)
        self.append_column(SpecialAttribute("id"))
        self.append_column(SpecialAttribute("weight"))

class Attribute(Column):

    def __init__(self, *args, **kwargs):
        args = list(args)
        if len(args) > 1 and isinstance(args[1], (types.TypeEngine, type)):
            args.pop(1)
        kwargs["type_"] = types.Integer()
        super(Attribute, self).__init__(*args, **kwargs)

class SpecialAttribute(Attribute):
    pass
