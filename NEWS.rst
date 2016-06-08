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
