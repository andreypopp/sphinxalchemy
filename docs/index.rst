.. sphinxalchemy documentation master file, created by
   sphinx-quickstart on Thu Jan 26 01:13:35 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

sphinxalchemy -- SQLAlchemy dialect for SphinxQL
================================================

This package provides a dialect for SQLAlchemy for interfacing with Sphinx_
search engine via SphinxQL_. It allows reusing core SQLAlchemy parts to generate
SphinxQL language constructs programmatically via :mod:`sqlalchemy.sql` and to
maintain a pool of connections to Sphinx via :mod:`sqlalchemy.pool`.

Basic usage
-----------

You need sphinxalchemy to be installed to allow SQLAlchemy to pick up SphinxQL
dialect classes. To install sphinxalchemy do::

  % pip install sphinxalchemy

or if you like ``easy_install`` command better::

  % easy_install sphinxalchemy

Now, as Sphinx uses MySQL protocol for interfacing via SphinxQL, you need to
decide which one of supported by sphinxalchemy MySQL connectivity libraries to
use -- MySQLdb_ or mysqlconnector-python_. Install one of those and use::

  sphinx+mysqldb://user@host:port

to connect to Sphinx using MySQLdb or::

  sphinx+mysqlconnector://user@host:port

to use mysqlconnector-python. You can now create engine using
:func:`sqlalchemy.create_engine` function as usually::

  from sqlalchemy import create_engine, MetaData

  engine = create_engine("sphinx+mysqlconnector://user@host:port")
  metadata = MetaData(bind=engine)

To define indexes (analogs of tables in relational databases) you should use
:mod:`sphinxalchemy.schema` module::

  from sphinxalchemy.schema import Index, Attribute, ArrayAttribute

  documents = Index("documents", metadata,
    Attribute("created"),
    ArrayAttribute("tag_ids"))

Now you can query your ``documents`` index::

  results = engine.execute(
    documents.select()
      .match("We think in generalities, but we live in details")
      .where(documents.c.tag_ids.in_([42, 1])))

API reference
-------------

.. module:: sphinxalchemy.schema

.. autoclass:: sphinxalchemy.schema.Index
.. autoclass:: sphinxalchemy.schema.Attribute
.. autoclass:: sphinxalchemy.schema.ArrayAttribute

.. module:: sphinxalchemy.sphinxql

.. autoclass:: sphinxalchemy.sphinxql.Select
   :members: match, options

.. autoclass:: sphinxalchemy.sphinxql.Replace
   :members: match, options

.. autofunction:: sphinxalchemy.sphinxql.select
.. autofunction:: sphinxalchemy.sphinxql.replace

.. _Sphinx: http://sphinxsearch.com
.. _SphinxQL: http://sphinxsearch.com/docs/2.0.2/sphinxql-reference.html
.. _MySQLdb: http://sourceforge.net/projects/mysql-python/
.. _mysqlconnector-python: https://launchpad.net/myconnpy
