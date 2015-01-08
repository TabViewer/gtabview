#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, division, unicode_literals

import csv
import sys
import locale


# Support PySide/PyQt4 with either Python 2/3
try:
    from PySide import QtCore, QtGui
except ImportError:
    from PyQt4 import QtCore, QtGui
if sys.version_info.major < 3:
    str = unicode


class Viewer(QtGui.QMainWindow):
    def __init__(self, data):
        super(Viewer, self).__init__()
        table = QtGui.QTableWidget(len(data) - 1, len(data[0]))
        self.setCentralWidget(table)
        table.setHorizontalHeaderLabels(data[0])
        for y, row in enumerate(data[1:]):
            for x, cell in enumerate(row):
                widget = QtGui.QTableWidgetItem(str(cell))
                table.setItem(y, x, widget)


def csv_sniff(fn, enc):
    """Given a filename or a list of lists, sniff the dialect of the file and
    return it. This should keep any errors from popping up with tab or comma
    delimited files.

    Args:
        fn - complete file path/name or list like
            ["col1,col2,col3","data1,data2,data3","data1...]
        enc - python encoding value ('utf_8','latin-1','cp870', etc)
    Returns:
        csv.dialect

    """
    if sys.version_info.major < 3:
        with open(fn, 'rb') as f:
            dialect = csv.Sniffer().sniff(f.read(1024 * 8))
    else:
        with open(fn, 'r', encoding=enc, newline='') as f:
            dialect = csv.Sniffer().sniff(f.read(1024 * 8))
    return dialect


def detect_encoding(fn=None):
    """Return the default system encoding. If a filename is passed, try
    to decode the file with the default system encoding or from a short
    list of encoding types to test.

    Args:
        fn(optional) - complete path to file

    Returns:
        enc - system encoding

    """
    enc_list = ['UTF-8', 'LATIN-1', 'iso8859-1', 'iso8859-2',
                'UTF-16', 'CP720']
    code = locale.getpreferredencoding(False)
    if code not in enc_list:
        enc_list.insert(0, code)
    if fn is not None:
        for c in enc_list:
            try:
                with open(fn, 'rb') as f:
                    f.readline().decode(c)
            except (UnicodeDecodeError, UnicodeError):
                continue
            return c
        print("Encoding not detected. Please pass encoding value manually")
    else:
        return code


def process_file(fn, enc=None, dialect=None):
    """Given a filename, return the file as a list of lists.

    """
    if enc is None:
        enc = detect_encoding(fn)
    if dialect is None:
        dialect = csv_sniff(fn, enc)
    data = []
    if sys.version_info.major < 3:
        with open(fn, 'rb') as f:
            csv_obj = csv.reader(f, dialect=dialect)
            for row in csv_obj:
                row = map(lambda x: str(x, enc), row)
                data.append(row)
    else:
        with open(fn, 'r', encoding=enc, newline='') as f:
            csv_obj = csv.reader(f, dialect=dialect)
            for row in csv_obj:
                data.append(row)
    return data


def view(data, modal=True, **kwargs):
    stalone = QtGui.qApp is None
    if stalone:
        QtGui.QApplication([])
    view = Viewer(data)
    view.show()
    if modal or stalone:
        while view.isVisible():
            QtGui.QApplication.processEvents()


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('filename')
    ap.add_argument('--encoding', '-e', help="Encoding, if required.  "
                    "If the file is UTF-8, Latin-1(iso8859-1) or a few "
                    "other common encodings, it should be detected "
                    "automatically. If not, you can pass "
                    "'CP720', or 'iso8859-2', for example.")
    args = ap.parse_args()
    data = process_file(args.filename, args.encoding)
    view(data)
