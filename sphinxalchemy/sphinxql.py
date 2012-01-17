""" Constructs for SphinxQL generation"""

from sqlalchemy.sql import expression

__all__ = ("SelectClause", "select")

class _Options(object):

    def __init__(self, options):
        self.options = list(options)

    def extend(self, options):
        self.options.extend(options)

    def _clone(self):
        return _Options(self.options[:])

    def __iter__(self):
        return iter(self.options)

class Select(expression.Select):

    _within_group_order_by_clause = expression.ClauseList()
    _options = None

    @expression._generative
    def within_group_order_by(self, *clauses):
        self.append_within_group_order_by(*clauses)

    @expression._generative
    def options(self, *args, **kwargs):
        options = list(args) + kwargs.items()
        if self._options is None:
            self._options = _Options(options)
        else:
            self._options.extend(options)

    def append_within_group_order_by(self, *clauses):
        """Append the given WITHIN GROUP ORDER BY criterion applied to this
        selectable.

        The criterion will be appended to any pre-existing WITHIN GROUP ORDER BY
        criterion.
        """
        if len(clauses) == 1 and clauses[0] is None:
            self._within_group_order_by_clause = expression.ClauseList()
        else:
            if getattr(self, '_within_group_order_by_clause', None) is not None:
                clauses = list(self._within_group_order_by_clause) \
                        + list(clauses)
            self._within_group_order_by_clause = expression.ClauseList(*clauses)

    def _copy_internals(self, clone=expression._clone, **kw):
        super(Select, self)._copy_internals(clone=clone, **kw)
        for attr in '_within_group_order_by_clause', '_options':
            if getattr(self, attr) is not None:
                setattr(self, attr, clone(getattr(self, attr), **kw))

    def get_children(self, column_collections=True, **kwargs):
        """return child elements as per the ClauseElement specification."""
        c = super(Select, self).get_children(
            column_collections=column_collections, **kwargs)
        return c + [x for x
                    in self._within_group_order_by_clause
                    if x is not None]

def select(columns=None, whereclause=None, from_obj=[], **kwargs):
    return Select(columns, whereclause=whereclause, from_obj=from_obj, **kwargs)
