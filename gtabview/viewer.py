# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import, generators
from .compat import *
from .models import *

# Support PyQt4/PySide with either Python 2/3
try:
    from PyQt4 import QtCore, QtGui
except ImportError:
    from PySide import QtCore, QtGui


class Data4ExtModel(QtCore.QAbstractTableModel):
    def __init__(self, model):
        super(Data4ExtModel, self).__init__()
        self.model = model

    def rowCount(self, index=None):
        return self.model.shape()[0]

    def columnCount(self, index=None):
        return self.model.shape()[1]

    def data(self, index, role):
        if role != QtCore.Qt.DisplayRole or not index.isValid():
            return None
        return str(self.model.data(index.row(), index.column()))


class Header4ExtModel(QtCore.QAbstractTableModel):
    def __init__(self, model, axis, palette):
        super(Header4ExtModel, self).__init__()
        self.model = model
        self.axis = axis
        self._palette = palette

    def rowCount(self, index=None):
        return self.model.shape()[0] if self.axis == 1 \
            else self.model.header_shape()[0]

    def columnCount(self, index=None):
        return self.model.shape()[1] if self.axis == 0 \
            else self.model.header_shape()[1]

    def headerData(self, section, orientation, role):
        if role != QtCore.Qt.DisplayRole: return None
        return section

    def data(self, index, role):
        row, col = (index.row(), index.column()) if self.axis == 0 \
                   else (index.column(), index.row())
        if role == QtCore.Qt.BackgroundRole:
            prev = self.model.header(self.axis, col - 1, row) if col else None
            cur = self.model.header(self.axis, col, row)
            return self._palette.midlight() if prev != cur else None
        if role != QtCore.Qt.DisplayRole or not index.isValid():
            return None
        return str(self.model.header(self.axis, col, row))


class ExtTableView(QtGui.QWidget):
    def __init__(self):
        super(ExtTableView, self).__init__()
        self._selection_rec = False
        self._model = None

        layout = QtGui.QGridLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.hscroll = QtGui.QScrollBar(QtCore.Qt.Horizontal)
        self.vscroll = QtGui.QScrollBar(QtCore.Qt.Vertical)

        self.table_header = QtGui.QTableView()
        self.table_header.verticalHeader().hide()
        self.table_header.setEditTriggers(QtGui.QTableWidget.NoEditTriggers)
        self.table_header.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table_header.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table_header.setHorizontalScrollMode(QtGui.QTableView.ScrollPerPixel)
        self.table_header.setHorizontalScrollBar(self.hscroll)
        self.table_header.setFrameStyle(QtGui.QFrame.Plain)
        self.table_header.setSelectionMode(QtGui.QTableView.ContiguousSelection)
        self.table_header.horizontalHeader().sectionResized.connect(self._column_resized)
        layout.addWidget(self.table_header, 0, 1)

        self.table_index = QtGui.QTableView()
        self.table_index.horizontalHeader().hide()
        self.table_index.setEditTriggers(QtGui.QTableWidget.NoEditTriggers)
        self.table_index.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table_index.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table_index.setVerticalScrollMode(QtGui.QTableView.ScrollPerPixel)
        self.table_index.setVerticalScrollBar(self.vscroll)
        self.table_index.setFrameStyle(QtGui.QFrame.Plain)
        self.table_index.setSelectionMode(QtGui.QTableView.ContiguousSelection)
        self.table_index.verticalHeader().sectionResized.connect(self._row_resized)
        layout.addWidget(self.table_index, 1, 0)

        self.table_data = QtGui.QTableView()
        self.table_data.verticalHeader().hide()
        self.table_data.horizontalHeader().hide()
        self.table_data.setEditTriggers(QtGui.QTableWidget.NoEditTriggers)
        self.table_data.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table_data.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table_data.setHorizontalScrollMode(QtGui.QTableView.ScrollPerPixel)
        self.table_data.setVerticalScrollMode(QtGui.QTableView.ScrollPerPixel)
        self.table_data.setHorizontalScrollBar(self.hscroll)
        self.table_data.setVerticalScrollBar(self.vscroll)
        self.table_data.setFrameStyle(QtGui.QFrame.Plain)
        self.table_data.setSelectionMode(QtGui.QTableView.ContiguousSelection)
        layout.addWidget(self.table_data, 1, 1)

        layout.addWidget(self.hscroll, 2, 0, 2, 2)
        layout.addWidget(self.vscroll, 0, 2, 2, 2)


    def _select_columns(self, source, dest):
        if self._selection_rec: return
        self._selection_rec = True
        dsm = dest.selectionModel()
        ssm = source.selectionModel()
        dsm.clear()
        for col in (index.column() for index in ssm.selectedIndexes()):
            dsm.select(dest.model().index(0, col),
                       QtGui.QItemSelectionModel.Select | QtGui.QItemSelectionModel.Columns)
        self._selection_rec = False


    def _select_rows(self, source, dest):
        if self._selection_rec: return
        self._selection_rec = True
        dsm = dest.selectionModel()
        ssm = source.selectionModel()
        dsm.clear()
        for row in (index.row() for index in ssm.selectedIndexes()):
            dsm.select(dest.model().index(row, 0),
                       QtGui.QItemSelectionModel.Select | QtGui.QItemSelectionModel.Rows)
        self._selection_rec = False


    def model(self):
        return self._model

    def _column_resized(self, col, old_width, new_width):
        self.table_data.setColumnWidth(col, new_width)

    def _row_resized(self, row, old_height, new_height):
        self.table_data.setRowHeight(row, new_height)


    def _update_layout(self):
        last_row = self._model.header_shape()[0] - 1
        hdr_height = self.table_header.rowViewportPosition(last_row) + \
                     self.table_header.rowHeight(last_row) + \
                     self.table_header.horizontalHeader().height()
        self.table_header.setFixedHeight(hdr_height)

        last_col = self._model.header_shape()[1] - 1
        idx_width = self.table_index.columnViewportPosition(last_col) + \
                    self.table_index.columnWidth(last_col) + \
                    self.table_index.verticalHeader().width()
        self.table_index.setFixedWidth(idx_width)


    def setModel(self, model):
        self._model = model
        self.table_data.setModel(Data4ExtModel(model))

        sel_model = self.table_data.selectionModel()
        sel_model.selectionChanged.connect(
            lambda *_: self._select_columns(self.table_data, self.table_header))
        sel_model.selectionChanged.connect(
            lambda *_: self._select_rows(self.table_data, self.table_index))

        self.table_header.setModel(Header4ExtModel(model, 0, self.palette()))
        sel_model = self.table_header.selectionModel()
        sel_model.selectionChanged.connect(
            lambda *_: self._select_columns(self.table_header, self.table_data))

        self.table_index.setModel(Header4ExtModel(model, 1, self.palette()))
        sel_model = self.table_index.selectionModel()
        sel_model.selectionChanged.connect(
            lambda *_: self._select_rows(self.table_index, self.table_data))

        # needs to be called after setting all table models
        self._update_layout()


    def setFocus(self):
        self.table_data.setFocus()

    def setCurrentIndex(self, y, x):
        self.table_data.selectionModel().setCurrentIndex(
            self.table_data.model().index(y, x),
            QtGui.QItemSelectionModel.ClearAndSelect)

    def resizeIndexToContents(self):
        self.table_index.resizeColumnsToContents()
        self._update_layout()

    def resizeColumnsToContents(self):
        self.table_data.resizeColumnsToContents()
        for col in range(self._model.shape()[1]):
            self.table_header.setColumnWidth(col, self.table_data.columnWidth(col))
        self.resizeIndexToContents()


class Viewer(QtGui.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Viewer, self).__init__()
        self.table = ExtTableView()
        self.setCentralWidget(self.table)
        self.closed = False
        if args or kwargs:
            self.view(*args, **kwargs)

    def closeEvent(self, event):
        self.closed = True

    def view(self, data, hdr_rows=None, start_pos=None):
        table = self.table

        # TODO: add specific data models to reduce overhead
        if data.__class__.__name__ in ['Series', 'Panel']:
            data = data.to_frame()
        elif isinstance(data, dict):
            data = [data.keys()] + list(map(list, zip(*[data[i] for i in data.keys()])))

        if data.__class__.__name__ == 'DataFrame':
            table.setModel(ExtFrameModel(data))
        elif data.__class__.__name__ == 'ndarray':
            table.setModel(ExtMatrixModel(data))
        elif isinstance(data[0], list):
            table.setModel(ExtListModel(data, hdr_rows))
        else:
            table.setModel(ExtVectorModel(data))

        model = table.model()
        shape = model.shape()
        self.setWindowTitle("{} rows, {} columns".format(shape[1], shape[0]))
        if shape[0] * shape[1] < 1e5:
            # resizing materializes the contents and might actually take longer
            # than loading all the data itself, so do it for small tables only
            table.resizeColumnsToContents()
        elif model.header_shape()[1] * shape[0] < 1e5:
            # similarly for the index, although we still do some more effort
            # due to fact that we cannot resize it (yet)
            table.resizeIndexToContents()

        table.setFocus()
        if start_pos:
            table.setCurrentIndex(start_pos[0], start_pos[1])

        self.showNormal()
        self.setWindowState(QtCore.Qt.WindowActive)
        self.closed = False
