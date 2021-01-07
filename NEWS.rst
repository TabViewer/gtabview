gtabview 0.10.1
---------------

* Fixes an issue with column autosizing leading to a division by zero on
  some systems.

gtabview 0.10
-------------

* Fixes interactive support within IPython and Jupyter notebooks.


gtabview 0.9
------------

* All iterables with a known length (such as sets) can now be visualized
  as regular columns without an explicit conversion.
* Sets and dictionary keys are now displayed in native order by default.
  A new ``sort`` keyword has been added to enforce ordering again.
* Fixes column autosizing error with Python 3.7+
* A crash that could occur during shutdown with a running detached view
  and Qt5 has been fixed.
* The ``gtabview`` utility is now installed via ``console_scripts``,
  fixing usage on Windows platforms.
* Removed support for Blaze, due to broken/unmaintained upstream.
* Version information is now available as a command line via
  ``--version`` and in the module itself ``gtabview.__version__``.


gtabview 0.8
------------

* Added support for PyQt5


gtabview 0.7.1
--------------

* Sequences of bytes/strings are now correcly shown as a single column.


gtabview 0.7
------------

* More irregular/malformed data structures are now supported.
* Any missing value supported by NumPy/Pandas (such as NaT) is now displayed as
  an empty cell for consistency.
* Column-autosizing performance tweaks.


gtabview 0.6.1
--------------

* Fix exception with PySide.
* Fix segmentation fault in repeated calls to view() in stand-alone programs.


gtabview 0.6
------------

* Improved column auto-sizing.
* NaNs (as None) are now also displayed as empty cells.
* Empty structures no longer cause view() to fail.


gtabview 0.5
------------

* Correctly pass user-supplied encoding to Blaze.
* Fix color palette selection on Windows.


gtabview 0.4
------------

* Added support for Blaze (http://blaze.pydata.org)
* Improved documentation.


gtabview 0.3
------------

* Headers and indexes can now be resized.
* Level names in ``pd.DataFrame`` objects are now shown.
* Negative ``start_pos`` offsets are now allowed to conveniently position the
  cursor counting from the end of the dataset.


gtabview 0.2
------------

* Fix visualization of ``np.matrix`` types.
* Allow data transposition.
