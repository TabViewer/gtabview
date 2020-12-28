# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import

import inspect
import sys
import warnings

from gtabview_cli import __version__
from .compat import *
from .dataio import read_model
from .viewer import QtGui, QtCore, QtWidgets
from .viewer import Viewer


# view defaults
WAIT = None     # When None, use matplotlib.is_interactive (if already imported)
RECYCLE = True  # Keep reusing the same window instead of creating new ones

# Global ViewControler for instance recycling
APP = None
VIEW = None


class ViewController(object):
    def __init__(self):
        super(ViewController, self).__init__()
        self._view = None

    def visible(self):
        if self._view is None:
            return False
        return self._view.isVisible()

    def wait(self):
        if self._view is None:
            return
        while self._view.isVisible():
            APP.processEvents(QtCore.QEventLoop.AllEvents |
                              QtCore.QEventLoop.WaitForMoreEvents)

    def view(self, data, view_kwargs, wait, recycle):
        global APP
        APP = QtWidgets.QApplication.instance()
        if APP is None:
            APP = QtWidgets.QApplication([])
        if self._view is None or not recycle:
            self._view = Viewer()
        self._view.view(data, **view_kwargs)
        if wait:
            self.wait()


def _varname_in_stack(var, skip):
    frame = inspect.currentframe().f_back
    while skip:
        frame = frame.f_back
        if not frame: return None
        skip -= 1
    for name in frame.f_locals:
        if frame.f_locals[name] is var:
            return name
    return None


def view(data, enc=None, start_pos=None, delimiter=None, hdr_rows=None,
         idx_cols=None, sheet_index=0, transpose=False, wait=None,
         recycle=None, detach=None, metavar=None, title=None, sort=False):
    """View the supplied data in an interactive, graphical table widget.

    data: When a valid path or IO object, read it as a tabular text
          file. Any other supported datatype is visualized directly and
          incrementally *without copying*.

    enc: File encoding (such as "utf-8", normally autodetected).

    delimiter: Text file delimiter (normally autodetected).

    hdr_rows: For files or lists of lists, specify the number of header rows.
              For files only, a default of one header line is assumed.

    idx_cols: For files or lists of lists, specify the number of index columns.
              By default, no index is assumed.

    sheet_index: For multi-table files (such as xls[x]), specify the sheet
                 index to read, starting from 0. Defaults to the first.

    start_pos: A tuple of the form (y, x) specifying the initial cursor
               position. Negative offsets count from the end of the dataset.

    transpose: Transpose the resulting view.

    sort: Request sorting of sets and keys of dicts where ordering is
          *normally* not meaningful.

    metavar: name of the variable being shown for display purposes (inferred
             automatically when possible).

    title: title of the data window.

    wait: Wait for the user to close the view before returning. By default, try
          to match the behavior of ``matplotlib.is_interactive()``. If
          matplotlib is not loaded, wait only if ``detach`` is also False. The
          default value can also be set through ``gtabview.WAIT``.

    recycle: Recycle the previous window instead of creating a new one. The
             default is True, and can also be set through ``gtabview.RECYCLE``.

    detach: Ignored for backward compatibility.
    """
    global WAIT, RECYCLE, VIEW

    model = read_model(data, enc=enc, delimiter=delimiter, hdr_rows=hdr_rows,
                       idx_cols=idx_cols, sheet_index=sheet_index,
                       transpose=transpose, sort=sort)
    if model is None:
        warnings.warn("cannot visualize the supplied data type: {}".format(type(data)),
                      category=RuntimeWarning)
        return None

    # install gui hooks in ipython/jupyter
    gui_support = False
    if 'IPython' in sys.modules:
        from IPython import get_ipython
        ip = get_ipython()
        if ip is not None:
            ip.enable_gui('qt')
            gui_support = True

    # setup defaults
    if wait is None: wait = WAIT
    if recycle is None: recycle = RECYCLE
    if wait is None:
        if 'matplotlib' in sys.modules:
            import matplotlib.pyplot as plt
            wait = not plt.isinteractive()
        else:
            wait = not gui_support

    # try to fetch the variable name in the upper stack
    if metavar is None:
        if isinstance(data, basestring):
            metavar = data
        else:
            metavar = _varname_in_stack(data, 1)

    # create a view controller
    if VIEW is None:
        VIEW = ViewController()

    # actually show the data
    view_kwargs = {'hdr_rows': hdr_rows, 'idx_cols': idx_cols,
                   'start_pos': start_pos, 'metavar': metavar, 'title': title}
    VIEW.view(model, view_kwargs, wait=wait, recycle=recycle)
    return VIEW
