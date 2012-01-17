""" Schema constructs for Sphinx"""

from sqlalchemy.schema import Table, Column

__all__ = ("Index", "Attribute")

Index = Table
Attribute = Column
