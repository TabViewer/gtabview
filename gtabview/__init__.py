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
from .viewer import Viewer
from .viewer import QtGui, QtCore


# view defaults
WAIT = None     # When None, use matplotlib.is_interactive (if already imported)
RECYCLE = True  # Keep reusing the same window instead of creating new ones
DETACH = False  # Create a fully autonomous GUI thread

# Global ViewControler for instance recycling
VIEW = None


# Helper functions
def _detect_encoding(data=None):
    """Return the default system encoding. If data is passed, try
    to decode the data with the default system encoding or from a short
    list of encoding types to test.

    Args:
        data - list of lists
    Returns:
        enc - system encoding
    """
    import locale
    enc_list = ['utf-8', 'latin-1', 'iso8859-1', 'iso8859-2',
                'utf-16', 'cp720']
    code = locale.getpreferredencoding(False)
    if data is None:
        return code
    if code.lower() not in enc_list:
        enc_list.insert(0, code.lower())
    for c in enc_list:
        try:
            for line in data:
                line.decode(c)
        except (UnicodeDecodeError, UnicodeError, AttributeError):
            continue
        return c
    print("Encoding not detected. Please pass encoding value manually")


def _parse_lines(data, enc=None, delimiter=None):
    import csv
    if enc is None:
        enc = _detect_encoding(data)
    if delimiter is None:
        delimiter = csv.Sniffer().sniff(data[0].decode(enc)).delimiter
    csv_data = []
    if sys.version_info.major < 3:
        csv_obj = csv.reader(data, delimiter=delimiter.encode(enc))
        for row in csv_obj:
            row = [x.decode(enc) for x in row]
            csv_data.append(row)
    else:
        data = [i.decode(enc) for i in data]
        csv_obj = csv.reader(data, delimiter=delimiter)
        for row in csv_obj:
            csv_data.append(row)
    return csv_data


class ViewController(object):
    def __init__(self):
        super(ViewController, self).__init__()
        self._view = None

    def view(self, data, start_pos, hdr_rows, wait, recycle):
        app = QtGui.QApplication.instance()
        if app is None:
            app = QtGui.QApplication([])
        if self._view is None or not recycle:
            self._view = Viewer()
        self._view.view(data, start_pos=start_pos, hdr_rows=hdr_rows)
        if wait:
            while self._view.isVisible():
                app.processEvents(QtCore.QEventLoop.AllEvents |
                                  QtCore.QEventLoop.WaitForMoreEvents)


class DetachedViewController(threading.Thread):
    def __init__(self):
        super(DetachedViewController, self).__init__()
        self._view = None
        self._data = None
        self._lock = threading.Lock()
        self._cond = threading.Condition()
        self._lock.acquire()

    def is_detached(self):
        with self._lock:
            return super(DetachedViewController, self).is_alive()

    def run(self):
        app = QtGui.QApplication.instance()
        if app is None:
            app = QtGui.QApplication([])
        else:
            warnings.warn("cannot detach: QApplication already initialized",
                          category=RuntimeWarning)
            self._lock.release()
            return
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
            with self._cond:
                app.processEvents(QtCore.QEventLoop.AllEvents |
                                  QtCore.QEventLoop.WaitForMoreEvents)
                self._cond.notify()

    def _notify(self):
        app = QtGui.QApplication.instance()
        app.postEvent(self._view, QtCore.QEvent(QtCore.QEvent.None))

    def exit(self):
        with self._lock:
            self._data = False
            self._notify()
        self.join()

    def view(self, data, start_pos, hdr_rows, wait, recycle):
        with self._lock:
            kwargs = {'start_pos': start_pos, 'hdr_rows': hdr_rows}
            self._data = {'data': data, 'recycle': recycle, 'kwargs': kwargs}
            self._notify()
        if wait:
            with self._cond:
                while not self._view.closed:
                    self._cond.wait()


def view(data, enc=None, start_pos=None, delimiter=None, hdr_rows=None,
         wait=None, recycle=None, detach=None):
    global WAIT, RECYCLE, DETACH, VIEW

    # setup values
    if wait is None: wait = WAIT
    if recycle is None: recycle = RECYCLE
    if detach is None: detach = DETACH
    if wait is None:
        if 'matplotlib' in sys.modules:
            import matplotlib
            wait = not matplotlib.is_interactive()
        else:
            wait = not bool(detach)

    # read the file into a regular list of lists
    if isinstance(data, basestring):
        with open(data, 'rb') as fd:
            data = _parse_lines(fd.readlines(), enc, delimiter)
    elif isinstance(data, (io.IOBase, file)):
        data = _parse_lines(data.readlines(), enc, delimiter)

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
    VIEW.view(data, wait=wait, start_pos=start_pos,
              hdr_rows=hdr_rows, recycle=recycle)
    return VIEW
