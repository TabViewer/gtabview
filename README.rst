gtabview: a simple graphical tabular data viewer
================================================

Graphical counterpart to `tabview <https://github.com/firecat53/tabview/>`_, a
simple tabular data viewer that can be used both stand-alone and as a Python
module for various files and Python/Pandas/NumPy data structures.


Stand-alone usage
-----------------

`gtabview` reads most tabular data formats automatically::

  gtabview data.csv


Usage as a module
-----------------

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

    # view a DataFrame/Series/Panel
    import pandas as pd
    df = pd.DataFrame([[1, 2, 3], [4, 5, 6]],
		      columns=['a', 'b', 'c'], index=['x', 'y'])
    view(df)

    # numpy is supported as well
    import numpy as np
    view(np.array([[1, 2, 3], [4, 5, 6]]))

If you're using gtabview with matplotlib either directly or indirectly (for
example, using the Pandas visualization API or Seaborn), be sure to include
matplotlib first to correctly initialize gtabview.

gtabview will also use matplotlib's ``interactive`` setting to determine the
default behavior of the data window: when interactive, calls to ``view()`` will
not block, and will keep recycling the same window.


Requirements and installation
-----------------------------

- Python 2 or Python 3
- PyQt4 or PySide
- setuptools and setuptools-git (install-only).

Under Debian/Ubuntu, install the required dependencies with::

  sudo apt-get install python python-qt4
  sudo apt-get install python-setuptools python-setuptools-git

Then download and install regularly with::

  git clone https://github.com/wavexx/gtabview
  cd gtabview
  ./setup.py install

You can also install directly via `pip`::

  pip install git+git://github.com/wavexx/gtabview

Excel files are supported if the ``xlrd`` module is also installed::

  sudo apt-get install python-xlrd

or::

  pip install xlrd


License
-------

| gtabview is distributed under the MIT license (see ``LICENSE.txt``)
| Copyright(c) 2014-2015: wave++ "Yuri D'Elia" <wavexx@thregr.org>
| Copyright(c) 2014-2015: Scott Hansen <firecat4153@gmail.com>
