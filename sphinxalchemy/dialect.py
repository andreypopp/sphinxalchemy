""" Dialect implementaiton for SphinxQL based on MySQLdb-Python protocol"""

from sqlalchemy.engine import default
from sqlalchemy.sql import compiler
from sqlalchemy.sql import expression as sql
from sqlalchemy import util, exc

__all__ = ("SphinxDialect",)

class SphinxCompiler(compiler.SQLCompiler):

    def within_group_order_by_clause(self, select, **kw):
        order_by = select._within_group_order_by_clause._compiler_dispatch(
            self, **kw)
        if order_by:
            return " WITHIN GROUP ORDER BY " + order_by
        else:
            return ""

    def options_clause(self, select, **_kw):
        def _compile(o, inner=False):
            r = ", ".join("%s=%s" % (
                (k, v)
                    if not isinstance(v, dict)
                    else (k, _compile(v.items(),True)))
                for (k, v) in o)
            if inner:
                return "(" + r + ")"
            return r
        return " OPTION %s" % _compile(select._options)

    def limit_clause(self, select):
        text = ""
        if select._limit is not None and select._offset is None:
            text +=  "\n LIMIT " + self.process(sql.literal(select._limit))
        elif select._limit is not None and select._offset is not None:
            text +=  "\n LIMIT %s, %s" % (
                self.process(sql.literal(select._offset)),
                self.process(sql.literal(select._limit)))
        elif select._offset is not None:
            raise exc.CompileError(
                "Cannot compile LIMIT clause, SELECT couldn't have only OFFSET"
                " clause without LIMIT")
        return text

    def visit_column(self, column, result_map=None, **kwargs):
        name = column.name
        if name is None:
            raise exc.CompileError("Cannot compile Column object until "
                                   "it's 'name' is assigned.")

        is_literal = column.is_literal
        if not is_literal and isinstance(name, sql._generated_label):
            name = self._truncated_identifier("colident", name)

        if result_map is not None:
            result_map[name.lower()] = (name, (column, ), column.type)

        if is_literal:
            name = self.escape_literal_column(name)
        else:
            name = self.preparer.quote(name, column.quote)

        return name

    def visit_match(self, match):
        return "MATCH('%s')" % match.query.replace("'", "\\'")

    def visit_select(self, select, asfrom=False, parens=True,
                            iswrapper=False, fromhints=None,
                            compound_index=1, **kwargs):

        entry = self.stack and self.stack[-1] or {}

        existingfroms = entry.get('from', None)

        froms = select._get_display_froms(existingfroms)

        correlate_froms = set(sql._from_objects(*froms))

        # TODO: might want to propagate existing froms for
        # select(select(select)) where innermost select should correlate
        # to outermost if existingfroms: correlate_froms =
        # correlate_froms.union(existingfroms)

        self.stack.append({'from': correlate_froms, 'iswrapper'
                          : iswrapper})

        if compound_index==1 and not entry or entry.get('iswrapper', False):
            column_clause_args = {'result_map':self.result_map}
        else:
            column_clause_args = {}

        # the actual list of columns to print in the SELECT column list.
        inner_columns = [
            c for c in [
                self.label_select_column(select, co, asfrom=asfrom).\
                    _compiler_dispatch(self,
                        within_columns_clause=True,
                        **column_clause_args)
                for co in util.unique_list(select.inner_columns)
            ]
            if c is not None
        ]

        text = "SELECT "  # we're off to a good start !

        if select._hints:
            byfrom = dict([
                            (from_, hinttext % {
                                'name':from_._compiler_dispatch(
                                    self, ashint=True)
                            })
                            for (from_, dialect), hinttext in
                            select._hints.iteritems()
                            if dialect in ('*', self.dialect.name)
                        ])
            hint_text = self.get_select_hint_text(byfrom)
            if hint_text:
                text += hint_text + " "

        if select._prefixes:
            text += " ".join(
                            x._compiler_dispatch(self, **kwargs)
                            for x in select._prefixes) + " "
        text += self.get_select_precolumns(select)
        text += ', '.join(inner_columns)

        if froms:
            text += " \nFROM "

            if select._hints:
                text += ', '.join([f._compiler_dispatch(self,
                                    asfrom=True, fromhints=byfrom,
                                    **kwargs)
                                for f in froms])
            else:
                text += ', '.join([f._compiler_dispatch(self,
                                    asfrom=True, **kwargs)
                                for f in froms])
        else:
            text += self.default_from()

        if select._whereclause is not None:
            t = select._whereclause._compiler_dispatch(self, **kwargs)
            if t:
                text += " \nWHERE " + t

        if select._group_by_clause.clauses:
            group_by = select._group_by_clause._compiler_dispatch(
                                        self, **kwargs)
            if group_by:
                text += " GROUP BY " + group_by

        if select._having is not None:
            t = select._having._compiler_dispatch(self, **kwargs)
            if t:
                text += " \nHAVING " + t

        if select._order_by_clause.clauses:
            text += self.order_by_clause(select, **kwargs)
        if getattr(select, "_within_group_order_by_clause", None) is not None:
            if select._within_group_order_by_clause.clauses:
                text += self.within_group_order_by_clause(select, **kwargs)
        if select._limit is not None:
            text += self.limit_clause(select)
        if getattr(select, "_options", None) is not None:
            if select._options.options:
                text += self.options_clause(select, **kwargs)
        if select.for_update:
            text += self.for_update_clause(select)

        self.stack.pop(-1)

        if asfrom and parens:
            return "(" + text + ")"
        else:
            return text

class SphinxDialect(default.DefaultDialect):

    name = "sphinx"
    statement_compiler = SphinxCompiler

    def _check_unicode_returns(self, connection):
        return True

    def do_rollback(self, connection):
        pass

    def do_commit(self, connection):
        pass

    def do_begin(self, connection):
        pass
