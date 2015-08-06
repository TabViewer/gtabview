# -*- coding: utf-8 -*-
# gtabview: a simple graphical tabular data viewer
# Copyright(c) 2014-2015: wave++ "Yuri D'Elia" <wavexx@thregr.org>
# Copyright(c) 2014-2015: Scott Hansen <firecat4153@gmail.com>
# Distributed under the MIT license (see LICENSE) WITHOUT ANY WARRANTY.
from __future__ import print_function, unicode_literals, absolute_import

import atexit
import inspect
import io
import sys
import threading
import warnings

from .compat import *
from .dataio import read_table
from .models import as_model
from .viewer import QtGui, QtCore
from .viewer import Viewer


# view defaults
WAIT = None     # When None, use matplotlib.is_interactive (if already imported)
RECYCLE = True  # Keep reusing the same window instead of creating new ones
DETACH = False  # Create a fully autonomous GUI thread

# Global ViewControler for instance recycling
VIEW = None


class ViewController(object):
    def __init__(self):
        super(ViewController, self).__init__()
        self._view = None

    def view(self, data, view_kwargs, wait, recycle):
        app = QtGui.QApplication.instance()
        if app is None:
            app = QtGui.QApplication([])
        if self._view is None or not recycle:
            self._view = Viewer()
        self._view.view(data, **view_kwargs)
        if wait:
            while self._view.isVisible():
                app.processEvents(QtCore.QEventLoop.AllEvents |
                                  QtCore.QEventLoop.WaitForMoreEvents)


class DetachedViewController(threading.Thread):
    def __init__(self):
        super(DetachedViewController, self).__init__()
        self._view = None
        self._data = None
        self._lock = threading.Condition(threading.Lock())
        self._lock.acquire()

    def is_detached(self):
        with self._lock:
            return super(DetachedViewController, self).is_alive()

    def run(self):
        app = QtGui.QApplication.instance()
        if app is not None:
            warnings.warn("cannot detach: QApplication already initialized",
                          category=RuntimeWarning)
            self._lock.release()
            return
        app = QtGui.QApplication([])
        self._view = Viewer()
        self._lock.release()
        while True:
            with self._lock:
                if self._data == False:
                    return
                elif self._data is not None:
                    if not self._data['recycle']:
                        self._view = Viewer()
                    self._view.view(self._data['data'], **self._data['view_kwargs'])
                    self._data = None
            app.processEvents(QtCore.QEventLoop.AllEvents |
                              QtCore.QEventLoop.WaitForMoreEvents)
            with self._lock:
                self._lock.notify()

    def _notify(self):
        app = QtGui.QApplication.instance()
        app.postEvent(self._view, QtCore.QEvent(0))

    def exit(self):
        with self._lock:
            self._data = False
            self._notify()
        self.join()

    def view(self, data, view_kwargs, wait, recycle):
        with self._lock:
            self._data = {'data': data, 'recycle': recycle,
                          'view_kwargs': view_kwargs}
            self._notify()
        if wait:
            with self._lock:
                while not self._view.closed:
                    self._lock.wait()


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


def blaze_from_uri(uri, enc):
    import blaze

    # make file:// uris work uniformly
    if uri.startswith('file://'):
        uri = uri[7:]

    return blaze.Data(uri, encoding=enc)


def view(data, enc=None, start_pos=None, delimiter=None, hdr_rows=None,
         idx_cols=None, sheet_index=0, transpose=False, wait=None,
         recycle=None, detach=None, metavar=None, title=None):
    """View the supplied data in an interactive, graphical table widget.

    data: When a valid path or IO object, read it as a tabular text file. When
          a valid URI, a Blaze object is constructed and visualized. Any other
          supported datatype is visualized directly and incrementally *without
          copying*.

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

    metavar: name of the variable being shown for display purposes (inferred
             automatically when possible).

    title: title of the data window.

    wait: Wait for the user to close the view before returning. By default, try
          to match the behavior of ``matplotlib.is_interactive()``. If
          matplotlib is not loaded, wait only if ``detach`` is also False. The
          default value can also be set through ``gtabview.WAIT``.

    recycle: Recycle the previous window instead of creating a new one. The
             default is True, and can also be set through ``gtabview.RECYCLE``.

    detach: Create a fully detached GUI thread for interactive use (note: this
            is *not* necessary if matplotlib is loaded). The default is False,
            and can also be set through ``gtabview.DETACH``.
    """
    global WAIT, RECYCLE, DETACH, VIEW

    # if data is a uri/file/path, read it
    if isinstance(data, basestring) or isinstance(data, (io.IOBase, file)):
        if isinstance(data, basestring) and '://' in data:
            data = blaze_from_uri(data, enc)
        else:
            data, hdr_rows = read_table(data, enc, delimiter, hdr_rows, sheet_index)

    # only assume an header when loading from a file
    if hdr_rows is None: hdr_rows = 0
    if idx_cols is None: idx_cols = 0

    model = as_model(data, hdr_rows=hdr_rows, idx_cols=idx_cols, transpose=transpose)
    if model is None:
        warnings.warn("cannot visualize the supplied data type: {}".format(type(data)),
                      category=RuntimeWarning)
        return None

    # setup defaults
    if wait is None: wait = WAIT
    if recycle is None: recycle = RECYCLE
    if detach is None: detach = DETACH
    if wait is None:
        if 'matplotlib' not in sys.modules:
            wait = not bool(detach)
        else:
            import matplotlib.pyplot as plt
            wait = not plt.isinteractive()

    # try to fetch the variable name in the upper stack
    if metavar is None:
        if isinstance(data, basestring):
            metavar = data
        else:
            metavar = _varname_in_stack(data, 1)

    # create a view controller
    if VIEW is None:
        if not detach:
            VIEW = ViewController()
        else:
            VIEW = DetachedViewController()
            VIEW.setDaemon(True)
            VIEW.start()
            if VIEW.is_detached():
                atexit.register(VIEW.exit)
            else:
                VIEW = None
                return None

    # actually show the data
    view_kwargs = {'hdr_rows': hdr_rows, 'idx_cols': idx_cols,
                   'start_pos': start_pos, 'metavar': metavar, 'title': title}
    VIEW.view(model, view_kwargs, wait=wait, recycle=recycle)
    return VIEW


# force matplotlib GUI to initialize
if 'matplotlib' in sys.modules:
    import matplotlib.pyplot as plt
    plt.close(plt.figure())
