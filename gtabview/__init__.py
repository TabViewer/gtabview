# -*- coding: utf-8 -*-
# gtabview: a simple graphical tabular data viewer
# Copyright(c) 2014-2015: wave++ "Yuri D'Elia" <wavexx@thregr.org>
# Copyright(c) 2014-2015: Scott Hansen <firecat4153@gmail.com>
# Distributed under the MIT license (see LICENSE) WITHOUT ANY WARRANTY.
from __future__ import print_function, unicode_literals, absolute_import

import atexit
import sys
import threading
import warnings

from .compat import *
from .dataio import read_table
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

    def view(self, data, hdr_rows, idx_cols, start_pos, wait, recycle):
        app = QtGui.QApplication.instance()
        if app is None:
            app = QtGui.QApplication([])
        if self._view is None or not recycle:
            self._view = Viewer()
        self._view.view(data, hdr_rows=hdr_rows, idx_cols=idx_cols, start_pos=start_pos)
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
                    self._view.view(self._data['data'], **self._data['kwargs'])
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

    def view(self, data, hdr_rows, idx_cols, start_pos, wait, recycle):
        with self._lock:
            kwargs = {'hdr_rows': hdr_rows, 'idx_cols': idx_cols, 'start_pos': start_pos}
            self._data = {'data': data, 'recycle': recycle, 'kwargs': kwargs}
            self._notify()
        if wait:
            with self._lock:
                while not self._view.closed:
                    self._lock.wait()


def view(data, enc=None, start_pos=None, delimiter=None, hdr_rows=None,
         idx_cols=None, wait=None, recycle=None, detach=None):
    global WAIT, RECYCLE, DETACH, VIEW

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

    # if data is a file/path, read it
    if isinstance(data, basestring) or isinstance(data, (io.IOBase, file)):
        data = read_table(data, enc, delimiter, hdr_rows)

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
    VIEW.view(data, wait=wait, hdr_rows=hdr_rows, idx_cols=idx_cols,
              start_pos=start_pos, recycle=recycle)
    return VIEW


# force matplotlib GUI to initialize
if 'matplotlib' in sys.modules:
    import matplotlib.pyplot as plt
    plt.close(plt.figure())
