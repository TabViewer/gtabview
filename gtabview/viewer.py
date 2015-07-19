# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import sys

# Support PySide/PyQt4 with either Python 2/3
try:
    from PySide import QtCore, QtGui
except ImportError:
    from PyQt4 import QtCore, QtGui
if sys.version_info.major < 3:
    str = unicode


class Viewer(QtGui.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Viewer, self).__init__()
        self.table = QtGui.QTableWidget()
        self.setCentralWidget(self.table)
        self.table.setEditTriggers(QtGui.QTableWidget.EditTrigger.NoEditTriggers)
        if args or kwargs:
            self.view(*args, **kwargs)

    def view(self, data, start_pos=None):
        table = self.table
        table.clear()
        table.setSortingEnabled(False)
        table.sortItems(-1)

        if data.__class__.__name__ in ['Series', 'Panel']:
            data = data.to_frame()
        elif isinstance(data, dict):
            data = [data.keys()] + map(list, zip(*[data[i] for i in data.keys()]))

        if data.__class__.__name__ == 'DataFrame':
            table.setRowCount(len(data))
            table.setColumnCount(len(data.columns))
            table.setHorizontalHeaderLabels(map(str, data.columns.values))
            table.setVerticalHeaderLabels(map(str, data.index.values))
            for x, col in enumerate(data):
                for y in range(len(data)):
                    widget = QtGui.QTableWidgetItem(str(data.iat[y, x]))
                    table.setItem(y, x, widget)
        elif data.__class__.__name__ == 'ndarray':
            table.setRowCount(data.shape[0])
            table.setColumnCount(data.shape[1])
            table.setHorizontalHeaderLabels(map(str, range(data.shape[1])))
            table.setVerticalHeaderLabels(map(str, range(data.shape[0])))
            for x in range(data.shape[1]):
                for y in range(data.shape[0]):
                    widget = QtGui.QTableWidgetItem(str(data[y, x]))
                    table.setItem(y, x, widget)
        elif isinstance(data[0], list):
            rows = max(1, len(data) - 1)
            cols = len(data[0])
            table.setRowCount(rows)
            table.setColumnCount(cols)
            table.setHorizontalHeaderLabels(data[0] if len(data) > 1 else
                                            map(str, range(cols)))
            table.setVerticalHeaderLabels(map(str, range(rows)))
            for y, row in enumerate(data[1 if len(data) > 1 else 0:]):
                for x, cell in enumerate(row):
                    widget = QtGui.QTableWidgetItem(str(cell))
                    table.setItem(y, x, widget)
        else:
            table.setRowCount(len(data))
            table.setColumnCount(1)
            table.setHorizontalHeaderLabels(["list"])
            table.setVerticalHeaderLabels(map(str, range(len(data))))
            for y in range(len(data)):
                widget = QtGui.QTableWidgetItem(str(data[y]))
                table.setItem(y, 0, widget)

        table.resizeColumnsToContents()
        table.setSortingEnabled(True)
        if start_pos:
            table.setCurrentCell(start_pos[0], start_pos[1])

