gtabview: a simple graphical tabular data viewer
================================================

Graphical counterpart to `tabview
<https://github.com/firecat53/tabview/>`_, a simple tabular data viewer
that can be used both stand-alone and as a Python module for various
files and Python/Pandas/NumPy data structures.


Stand-alone usage
-----------------

`gtabview` reads most text tabular data formats automatically::

  gtabview data.csv
  gtabview data.txt

If xlrd_ is installed, Excel files can be read directly::

  gtabview file.xls[x]

.. _xlrd: https://pypi.org/project/xlrd/


Usage as a module
-----------------

``gtabview.view()`` can be used to display simple Python types directly
in tabulated form:

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

`gtabview` is designed to integrate correctly with `IPython`, `Jupyter`
and `matplotlib`.

When `matplotlib` is used, `gtabview` will automatically default to use
mpl's ``interactive`` setting to determine the default behavior of the
data window: when interactive, calls to ``view()`` will not block, and
will keep recycling the same window.

In `IPython` and `Jupyter` notebooks ``view()`` calls also default to
non-blocking behavior, while in plain Python calls will halt until the
window is closed.

You can change this behavior with the ``view(..., wait=False)`` argument
for each call, or by changing the module default::

  import gtabview
  gtabview.WAIT = False

In a `Jupyter` notebook a *separate* data window will always show. The
window can be kept around or closed, but will only be refreshed when
evaluating the cell again.

Separate data windows can also be opened by using the ``view(...,
recycle=False)`` argument, or again by setting the global
``gtabview.RECYCLE`` default. See the built-in documentation of
``gtabview.view`` for more details.


Requirements and installation
-----------------------------

`gtabview` is available directly on the `Python Package Index
<https://pypi.org/project/gtabview/>`_ and on `conda-forge
<https://anaconda.org/conda-forge/gtabview>`_.

`gtabview` requires:

- Python 3 or Python 2
- PyQt5, PyQt4 or PySide
- setuptools (install-only)

Under Debian/Ubuntu, install the required dependencies with::

  sudo apt-get install python3 python3-pyqt5
  sudo apt-get install python3-setuptools

Then download and install simply via pip::

  pip install gtabview

Or with conda::

  conda install -c conda-forge gtabview

You explicitly need to install ``xlrd`` if direct reading of Excel files
is desired::

  pip install xlrd


License
-------

| gtabview is distributed under the MIT license (see ``LICENSE.txt``)
| Copyright(c) 2014-2021: wave++ "Yuri D'Elia" <wavexx@thregr.org>
| Copyright(c) 2014-2015: Scott Hansen <firecat4153@gmail.com>
