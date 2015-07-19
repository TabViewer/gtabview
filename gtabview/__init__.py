# -*- coding: utf-8 -*-
# gtabview: a simple graphical tabular data viewer
# Copyright(c) 2014-2015: wave++ "Yuri D'Elia" <wavexx@thregr.org>
# Copyright(c) 2014-2015: Scott Hansen <firecat four one five three at gmail dot com>
# Distributed under the MIT license (see LICENSE) WITHOUT ANY WARRANTY.
from __future__ import print_function, unicode_literals, absolute_import

import io
import sys
import threading

from .viewer import Viewer
from .viewer import QtGui, QtCore

# Global Viewer for instance recycling
VIEWER = None


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
            row = [str(x, enc) for x in row]
            csv_data.append(row)
    else:
        data = [i.decode(enc) for i in data]
        csv_obj = csv.reader(data, delimiter=delimiter)
        for row in csv_obj:
            csv_data.append(row)
    return csv_data


def _process_events(widget):
    while widget.isVisible():
        QtGui.QApplication.processEvents()


def view(data, modal=True, enc=None, start_pos=(0, 0),
         delimiter=None, hdr_rows=None, recycle=True):
    # read data into a regular list of lists
    if isinstance(data, basestring):
        with open(data, 'rb') as fd:
            data = _parse_lines(fd.readlines())
    elif isinstance(data, (io.IOBase, file)):
        data = _parse_lines(data.readlines())

    # create one application instance if missing
    if QtGui.qApp is None:
        QtGui.QApplication([])

    # viewer instance
    global VIEWER
    if VIEWER is None or recycle is False:
        VIEWER = Viewer()
    view = VIEWER
    view.view(data, start_pos)

    # run the application loop
    if modal:
        view.setWindowModality(QtCore.Qt.ApplicationModal)
        view.show()
        _process_events(view)
    else:
        view.setWindowModality(QtCore.Qt.NonModal)
        if view.isVisible():
            # recycle the previous loop handler
            pass
        else:
            view.show()
            # we might have more than a single processing/thread loop active
            # (depending whether we're being used as a stand-alone app or a module
            # with a QtApp host), but simply, each loop is going to proceed in
            # lock-step until it's view is closed.
            thread = threading.Thread(target=_process_events, args=(view,))
            thread.start()
        return view

