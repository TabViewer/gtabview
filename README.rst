gtabview: a simple graphical tabular data viewer
================================================

A graphical counterpart to `tabview <https://github.com/firecat53/tabview/>`_,
a simple tabular data viewer that can be used both stand-alone and as a Python
module for various Python/Pandas/NumPy data structures.


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

    # view a simple list of lists
    view([['a', 'b', 'c'], [1, 2, 3], [4, 5, 6], [7, 8, 9]])

    # view a DataFrame/Series/Panel
    import pandas.io.data as web
    import datetime
    start = datetime.datetime(2010, 1, 1)
    end = datetime.datetime(2013, 1, 27)
    panel = web.DataReader(["F", "YHOO"], 'yahoo', start, end)
    df = panel.loc[:,:,"F"]
    view(df)

    # numpy is supported as well
    from numpy import array
    view(array([[1, 2, 3], [4, 5, 6]]))


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


License
-------

| gtabview is distributed under the MIT license (see ``LICENSE.txt``).
| Copyright(c) 2014-2015: wave++ "Yuri D'Elia" <wavexx@thregr.org>.
| Copyright(c) 2014-2015: Scott Hansen <firecat four one five three at gmail dot com>
