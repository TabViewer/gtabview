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

.. _xlrd: https://pypi.python.org/pypi/xlrd


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

`gtabview` is designed to integrate correctly with matplotlib. If you're
using `gtabview` with matplotlib either directly or indirectly (for
example, using the Pandas visualization API or Seaborn), be sure to
include matplotlib *first* to correctly initialize `gtabview`.

`gtabview` will also use matplotlib's ``interactive`` setting to
determine the default behavior of the data window: when interactive,
calls to ``view()`` will not block, and will keep recycling the same
window.

To use `gtabview` in a Python Notebook with inline graphics, you'll
probably want to force the detached behavior. In the first cell of your
notebook, initialize both `gtabview` and `matplotlib` as follows:

.. code:: python

  import gtabview
  gtabview.DETACH = True
  from gtabview import view
  %matplotlib inline

When using ``view``, a *separate* data window will show. The window can
be kept around or closed, but will only be refreshed when evaluating the
cell again. Jupyter is currently known not to work properly
(https://github.com/TabViewer/gtabview/issues/32).


Requirements and installation
-----------------------------

`gtabview` is available directly on the `Python Package Index
<https://pypi.python.org/pypi/gtabview>`_.

`gtabview` requires:

- Python 3 or Python 2
- PyQt5, PyQt4 or PySide
- setuptools (install-only)

Under Debian/Ubuntu, install the required dependencies with::

  sudo apt-get install python3 python3-pyqt5
  sudo apt-get install python3-setuptools

Then download and install simply via pip::

  pip install gtabview

Install ``xlrd`` if direct reading of Excel files is desired::

  pip install xlrd


License
-------

| gtabview is distributed under the MIT license (see ``LICENSE.txt``)
| Copyright(c) 2014-2020: wave++ "Yuri D'Elia" <wavexx@thregr.org>
| Copyright(c) 2014-2015: Scott Hansen <firecat4153@gmail.com>
