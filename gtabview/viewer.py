# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import, generators
from .compat import *

# Support PyQt4/PySide with either Python 2/3
try:
    from PyQt4 import QtCore, QtGui
except ImportError:
    from PySide import QtCore, QtGui


class ListModel(QtCore.QAbstractTableModel):
    def __init__(self, data, hdr_rows=None):
        super(ListModel, self).__init__()
        if hdr_rows is None:
            hdr_rows = 1 if len(data) > 1 else 0
        self.hdr_rows = hdr_rows
        self.rows = max(1, len(data) - hdr_rows)
        self.cols = max(1, len(data[0]))
        self.data = data

    def rowCount(self, index=None):
        return self.rows

    def columnCount(self, index=None):
        return self.cols

    def headerData(self, section, orientation, role):
        if role != QtCore.Qt.DisplayRole:
            return None
        if orientation == QtCore.Qt.Horizontal and self.hdr_rows:
            return self.data[0][section]
        else:
            return section

    def data(self, index, role):
        if role != QtCore.Qt.DisplayRole or not index.isValid():
            return None
        return str(self.data[self.hdr_rows + index.row()][index.column()])


class VectorModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(VectorModel, self).__init__()
        self.data = data

    def rowCount(self, index=None):
        return len(self.data)

    def columnCount(self, index=None):
        return 1

    def headerData(self, section, orientation, role):
        if role != QtCore.Qt.DisplayRole:
            return None
        if orientation == QtCore.Qt.Horizontal:
            return "[vector]"
        else:
            return section

    def data(self, index, role):
        if role != QtCore.Qt.DisplayRole or not index.isValid():
            return None
        return str(self.data[index.row()])


class MatrixModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(MatrixModel, self).__init__()
        self.data = data

    def rowCount(self, index=None):
        return self.data.shape[0]

    def columnCount(self, index=None):
        return self.data.shape[1]

    def headerData(self, section, orientation, role):
        if role != QtCore.Qt.DisplayRole:
            return None
        return section

    def data(self, index, role):
        if role != QtCore.Qt.DisplayRole or not index.isValid():
            return None
        return str(self.data[index.row(), index.column()])


class FrameModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(FrameModel, self).__init__()
        self.data = data

    def rowCount(self, index=None):
        return self.data.shape[0]

    def columnCount(self, index=None):
        return self.data.shape[1]

    def headerData(self, section, orientation, role):
        if role != QtCore.Qt.DisplayRole:
            return None
        if orientation == QtCore.Qt.Horizontal:
            return str(self.data.columns.values[section])
        else:
            return str(self.data.index.values[section])

    def data(self, index, role):
        if role != QtCore.Qt.DisplayRole or not index.isValid():
            return None
        return str(self.data.iat[index.row(), index.column()])


class Viewer(QtGui.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Viewer, self).__init__()
        self.table = QtGui.QTableView()
        self.setCentralWidget(self.table)
        self.table.setEditTriggers(QtGui.QTableWidget.NoEditTriggers)
        if args or kwargs:
            self.view(*args, **kwargs)

    def view(self, data, hdr_rows=None, start_pos=None):
        table = self.table

        # TODO: add specific data models to reduce overhead
        if data.__class__.__name__ in ['Series', 'Panel']:
            data = data.to_frame()
        elif isinstance(data, dict):
            data = [data.keys()] + list(map(list, zip(*[data[i] for i in data.keys()])))

        if data.__class__.__name__ == 'DataFrame':
            table.setModel(FrameModel(data))
        elif data.__class__.__name__ == 'ndarray':
            table.setModel(MatrixModel(data))
        elif isinstance(data[0], list):
            table.setModel(ListModel(data, hdr_rows))
        else:
            table.setModel(VectorModel(data))

        model = table.model()
        self.setWindowTitle("{} rows, {} columns".format(model.rowCount(), model.columnCount()))
        if model.rowCount() * model.columnCount() < 1e5:
            # resizing materializes the contents and might actually take longer
            # than loading all the data itself, so do it for small tables only
            table.resizeColumnsToContents()
        if start_pos:
            index = model.index(start_pos[0], start_pos[1])
            table.selectionModel().select(index, QtGui.QItemSelectionModel.ClearAndSelect)
