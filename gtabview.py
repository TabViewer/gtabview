#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import io
import os
import sys


# Support PySide/PyQt4 with either Python 2/3
try:
    from PySide import QtCore, QtGui
except ImportError:
    from PyQt4 import QtCore, QtGui
if sys.version_info.major < 3:
    str = unicode


class Viewer(QtGui.QMainWindow):
    def __init__(self, data, start_pos=None):
        super(Viewer, self).__init__()
        if data.__class__.__name__ in ['Series', 'Panel']:
            data = data.to_frame()
        elif isinstance(data, dict):
            data = [data.keys()] + map(list, zip(*[data[i] for i in data.keys()]))
        if data.__class__.__name__ == 'DataFrame':
            table = QtGui.QTableWidget(len(data), len(data.columns))
            self.setCentralWidget(table)
            table.setHorizontalHeaderLabels(map(str, data.columns.values))
            table.setVerticalHeaderLabels(map(str, data.index.values))
            for x, col in enumerate(data):
                for y in range(len(data)):
                    widget = QtGui.QTableWidgetItem(str(data.iat[y, x]))
                    table.setItem(y, x, widget)
        elif data.__class__.__name__ == 'ndarray':
            table = QtGui.QTableWidget(data.shape[0], data.shape[1])
            self.setCentralWidget(table)
            table.setHorizontalHeaderLabels(map(str, range(data.shape[1])))
            table.setVerticalHeaderLabels(map(str, range(data.shape[0])))
            for x in range(data.shape[1]):
                for y in range(data.shape[0]):
                    widget = QtGui.QTableWidgetItem(str(data[y, x]))
                    table.setItem(y, x, widget)
        elif isinstance(data[0], list):
            rows = max(1, len(data) - 1)
            cols = len(data[0])
            table = QtGui.QTableWidget(rows, cols)
            self.setCentralWidget(table)
            table.setHorizontalHeaderLabels(data[0] if len(data) > 1 else
                                            map(str, range(cols)))
            table.setVerticalHeaderLabels(map(str, range(rows)))
            for y, row in enumerate(data[1 if len(data) > 1 else 0:]):
                for x, cell in enumerate(row):
                    widget = QtGui.QTableWidgetItem(str(cell))
                    table.setItem(y, x, widget)
        else:
            table = QtGui.QTableWidget(len(data), 1)
            self.setCentralWidget(table)
            table.setHorizontalHeaderLabels(["list"])
            table.setVerticalHeaderLabels(map(str, range(len(data))))
            for y in range(len(data)):
                widget = QtGui.QTableWidgetItem(str(data[y]))
                table.setItem(y, 0, widget)
        if start_pos:
            table.setCurrentCell(start_pos[0], start_pos[1])


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
        csv_obj = csv.reader(data, delimiter=delim)
        for row in csv_obj:
            csv_data.append(row)
    return csv_data


def view(data, modal=True, enc=None, start_pos=(0, 0),
         delimiter=None, hdr_rows=None):
    # read data into a regular list of lists
    if isinstance(data, basestring):
        with open(data, 'rb') as fd:
            data = _parse_lines(fd.readlines())
    elif isinstance(data, (io.IOBase, file)):
        data = _parse_lines(data.readlines())

    stalone = QtGui.qApp is None
    if stalone:
        QtGui.QApplication([])
    view = Viewer(data, start_pos)
    view.show()
    if modal or stalone:
        while view.isVisible():
            QtGui.QApplication.processEvents()


def _arg_parse():
    import argparse
    parser = argparse.ArgumentParser(description="View a tab-delimited file "
                                     "in a spreadsheet-like display. ")
    parser.add_argument('filename', help="File to read. Use '-' to read from "
                        "the standard input instead.")
    parser.add_argument('--encoding', '-e', help="Encoding, if required.  "
                        "If the file is UTF-8, Latin-1(iso8859-1) or a few "
                        "other common encodings, it should be detected "
                        "automatically. If not, you can pass "
                        "'CP720', or 'iso8859-2', for example.")
    parser.add_argument('--delimiter', '-d', default=None,
                        help="CSV delimiter. Not typically necessary since "
                        "automatic delimiter sniffing is used.")
    parser.add_argument('--header', '-H', default=None, type=int,
                        help="Set number of header rows (defaults to 1)")
    parser.add_argument('--start_pos', '-s',
                        help="Initial cursor display position. "
                        "Single number for just y (row) position, or two "
                        "comma-separated numbers (--start_pos 2,3) for both. "
                        "Alternatively, you can pass the numbers in the more "
                        "classic +y:[x] format without the --start_pos label. "
                        "Like 'tabview <fn> +5:10'")
    return parser.parse_known_args()


def _start_position(start_norm, start_classic):
    """Given a string "[y, x, ...]" or a string "+[y]:[x]", return a tuple (y, x)
    for the start position

    Args: start_norm - string [y,x, ...]
          start_classic - string "+[y]:[x]"

    Returns: tuple (y, x)
    """
    if start_norm is not None:
        start_pos = start_norm.split(',')[:2]
        if not start_pos[0]:
            start_pos[0] = 0
        start_pos = [int(i) for i in start_pos]
    elif start_classic:
        sp = start_classic[0].strip('+').split(':')
        if not sp[0]:
            sp[0] = 0
        try:
            start_pos = (int(sp[0]), int(sp[1]))
        except IndexError:
            start_pos = (int(sp[0]), 0)
    else:
        start_pos = (0, 0)
    return start_pos


def _fixup_stdin():
    print("gtabview: Reading from stdin...", file=sys.stderr)
    data = os.fdopen(os.dup(0), 'rb')
    os.dup2(os.open("/dev/tty", os.O_RDONLY), 0)
    return data


if __name__ == '__main__':
    args, extra = _arg_parse()
    pos_plus = [i for i in extra if i.startswith('+')]
    start_pos = _start_position(args.start_pos, pos_plus)
    if args.filename != '-':
        data = args.filename
    else:
        data = _fixup_stdin()
    view(data, enc=args.encoding, start_pos=start_pos,
         delimiter=args.delimiter, hdr_rows=args.header)
