gtabview: a simple graphical tabular data viewer
================================================

Graphical counterpart to `tabview <https://github.com/firecat53/tabview/>`_, a
simple tabular data viewer that can be used both stand-alone and as a Python
module for various files and Python/Pandas/NumPy data structures.


Stand-alone usage
-----------------

`gtabview` reads most text tabular data formats automatically::

  gtabview data.csv
  gtabview data.txt

If xlrd_ is installed, Excel files can be read directly::

  gtabview file.xls[x]

When Blaze_ is also installed, any Blaze source can be used by specifying a
`supported URI`_ on the command line::

  gtabview file://dataset.hdf5
  gtabview file://dataset.json
  gtabview sqlite://file.db::table
  gtabview postgresql://host.domain/db_name::table

The database URL syntax is inherited from SQLAlchemy, so refer to SQLAlchemy's
`database URLs`_ for a detailed reference.

.. _xlrd: https://pypi.python.org/pypi/xlrd
.. _Blaze: http://blaze.pydata.org/
.. _supported URI: http://blaze.pydata.org/en/latest/uri.html
.. _database URLs: http://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls


Usage as a module
-----------------

``gtabview.view()`` can be used to display simple Python types directly in
tabulated form:

.. code:: python

    from gtabview import view

    # view a file
    view("/path/to/file")

    # view a list
    view([1, 2, 3])

    # view a dict (by columns)
    view({'a': [1, 2, 3], 'b': [4, 5, 6], 'c': [7, 8, 9]})

    # view a dict (by rows)
    view({'a': [1, 2, 3], 'b': [4, 5, 6], 'c': [7, 8, 9]}, transpose=True)

    # view a simple list of lists
    view([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

    # view a simple list of lists (with headers)
    view([['a', 'b', 'c'], [1, 2, 3], [4, 5, 6], [7, 8, 9]], hdr_rows=1)

`gtabview` includes native support for NumPy and all features of Pandas'
DataFrames, such as MultiIndexes and level names:

.. code:: python

    from gtabview import view

    # numpy arrays up to two dimensions are supported
    import numpy as np
    view(np.array([[1, 2, 3], [4, 5, 6]]))

    # view a DataFrame/Series/Panel
    import pandas as pd
    df = pd.DataFrame([[1, 2, 3], [4, 5, 6]],
		      columns=['a', 'b', 'c'], index=['x', 'y'])
    view(df)

Blaze can also be used directly as a data source, either explicitly or
implicitly through an URI:

.. code:: python

    from gtabview import view
    import blaze as bz

    iris = bz.Data('sqlite:///blaze/examples/data/iris.db::iris')
    view(iris)

    view('postgresql://user:pass@host.domain:port/db_name::table')

`gtabview` is designed to integrate correctly with matplotlib. If you're using
`gtabview` with matplotlib either directly or indirectly (for example, using
the Pandas visualization API or Seaborn), be sure to include matplotlib *first*
to correctly initialize `gtabview`.

`gtabview` will also use matplotlib's ``interactive`` setting to determine the
default behavior of the data window: when interactive, calls to ``view()`` will
not block, and will keep recycling the same window.

To use `gtabview` in a Python Notebook with inline graphics, you'll probably
want to force the detached behavior. In the first cell of your notebook,
initialize both `gtabview` and `matplotlib` as follows:

.. code:: python

  import gtabview
  gtabview.DETACH = True
  from gtabview import view
  %matplotlib inline

When using ``view``, a *separate* data window will show. The window can be kept
around or closed, but will only be refreshed when evaluating the cell again.


Requirements and installation
-----------------------------

`gtabview` is available directly on the `Python Package Index
<https://pypi.python.org/pypi/gtabview>`_.

`gtabview` requires:

- Python 2 or Python 3
- PyQt4 or PySide
- setuptools and setuptools-git (install-only).

Under Debian/Ubuntu, install the required dependencies with::

  sudo apt-get install python python-qt4
  sudo apt-get install python-setuptools python-setuptools-git

Then download and install simply via pip::

  pip install gtabview

Install ``xlrd`` if reading Excel files directly is desired, and optionally
Blaze for interacting with other/scientific data formats::

  pip install xlrd
  pip install blaze


License
-------

| gtabview is distributed under the MIT license (see ``LICENSE.txt``)
| Copyright(c) 2014-2016: wave++ "Yuri D'Elia" <wavexx@thregr.org>
| Copyright(c) 2014-2015: Scott Hansen <firecat4153@gmail.com>
