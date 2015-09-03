# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import, generators
from .compat import *

# Support PyQt4/PySide with either Python 2/3
try:
    from PyQt4 import QtCore, QtGui
except ImportError:
    from PySide import QtCore, QtGui


def as_str(obj):
    return '' if obj is None else str(obj)


class Data4ExtModel(QtCore.QAbstractTableModel):
    def __init__(self, model):
        super(Data4ExtModel, self).__init__()
        self.model = model

    def rowCount(self, index=None):
        return max(1, self.model.shape()[0])

    def columnCount(self, index=None):
        return max(1, self.model.shape()[1])

    def data(self, index, role):
        if role != QtCore.Qt.DisplayRole or not index.isValid():
            return None
        return as_str(self.model.data(index.row(), index.column()))


class Header4ExtModel(QtCore.QAbstractTableModel):
    def __init__(self, model, axis, palette):
        super(Header4ExtModel, self).__init__()
        self.model = model
        self.axis = axis
        self._palette = palette
        if self.axis == 0:
            self._shape = (self.model.header_shape()[0], self.model.shape()[1])
        else:
            self._shape = (self.model.shape()[0], self.model.header_shape()[1])

    def rowCount(self, index=None):
        return max(1, self._shape[0])

    def columnCount(self, index=None):
        return max(1, self._shape[1])

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.TextAlignmentRole:
            if orientation == QtCore.Qt.Horizontal:
                return QtCore.Qt.AlignCenter | QtCore.Qt.AlignBottom
            else:
                return QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
        if role != QtCore.Qt.DisplayRole:
            return None
        return section if self.axis == (orientation - 1) else \
            self.model.name(self.axis, section)

    def data(self, index, role):
        if not index.isValid() or not self._shape[self.axis]:
            return None
        row, col = (index.row(), index.column()) if self.axis == 0 \
                   else (index.column(), index.row())
        if role == QtCore.Qt.BackgroundRole:
            prev = self.model.header(self.axis, col - 1, row) if col else None
            cur = self.model.header(self.axis, col, row)
            return self._palette.midlight() if prev != cur else None
        if role != QtCore.Qt.DisplayRole: return None
        return as_str(self.model.header(self.axis, col, row))


class Level4ExtModel(QtCore.QAbstractTableModel):
    def __init__(self, model, palette, font):
        super(Level4ExtModel, self).__init__()
        self.model = model
        self._background = palette.dark().color()
        if self._background.lightness() > 127:
            self._foreground = palette.text()
        else:
            self._foreground = palette.highlightedText()
        self._palette = palette
        font.setBold(True)
        self._font = font

    def rowCount(self, index=None):
        return max(1, self.model.header_shape()[0])

    def columnCount(self, index=None):
        return max(1, self.model.header_shape()[1])

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.TextAlignmentRole:
            if orientation == QtCore.Qt.Horizontal:
                return QtCore.Qt.AlignCenter | QtCore.Qt.AlignBottom
            else:
                return QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
        if role != QtCore.Qt.DisplayRole: return None
        return 'L' + str(section)

    def data(self, index, role):
        if not index.isValid():
            return None
        if role == QtCore.Qt.FontRole:
            return self._font
        if index.row() == self.model.header_shape()[0] - 1:
            if role == QtCore.Qt.DisplayRole:
                return str(self.model.name(1, index.column()))
            elif role == QtCore.Qt.ForegroundRole:
                return self._foreground
            elif role == QtCore.Qt.BackgroundRole:
                return self._background
        elif index.column() == self.model.header_shape()[1] - 1:
            if role == QtCore.Qt.DisplayRole:
                return str(self.model.name(0, index.row()))
            elif role == QtCore.Qt.ForegroundRole:
                return self._foreground
            elif role == QtCore.Qt.BackgroundRole:
                return self._background
        elif role == QtCore.Qt.BackgroundRole:
            return self._palette.background()
        return None


class ExtTableView(QtGui.QWidget):
    def __init__(self):
        super(ExtTableView, self).__init__()
        self._selection_rec = False
        self._model = None

        # We manually set the inactive highlight color to differentiate the
        # selection between the data/index/header. To actually make use of the
        # palette though, we also have to manually assign a new stock delegate
        # to each table view
        palette = self.palette()
        tmp = palette.highlight().color()
        tmp.setHsv(tmp.hsvHue(), 100, palette.midlight().color().lightness())
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Highlight, tmp)
        self.setPalette(palette)

        layout = QtGui.QGridLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.hscroll = QtGui.QScrollBar(QtCore.Qt.Horizontal)
        self.vscroll = QtGui.QScrollBar(QtCore.Qt.Vertical)

        self.table_level = QtGui.QTableView()
        self.table_level.setEditTriggers(QtGui.QTableWidget.NoEditTriggers)
        self.table_level.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table_level.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table_level.setFrameStyle(QtGui.QFrame.Plain)
        self.table_level.horizontalHeader().sectionResized.connect(self._index_resized)
        self.table_level.verticalHeader().sectionResized.connect(self._header_resized)
        self.table_level.setItemDelegate(QtGui.QItemDelegate())
        layout.addWidget(self.table_level, 0, 0)

        self.table_header = QtGui.QTableView()
        self.table_header.verticalHeader().hide()
        self.table_header.setEditTriggers(QtGui.QTableWidget.NoEditTriggers)
        self.table_header.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table_header.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table_header.setHorizontalScrollMode(QtGui.QTableView.ScrollPerPixel)
        self.table_header.setHorizontalScrollBar(self.hscroll)
        self.table_header.setFrameStyle(QtGui.QFrame.Plain)
        self.table_header.horizontalHeader().sectionResized.connect(self._column_resized)
        self.table_header.setItemDelegate(QtGui.QItemDelegate())
        layout.addWidget(self.table_header, 0, 1)

        self.table_index = QtGui.QTableView()
        self.table_index.horizontalHeader().hide()
        self.table_index.setEditTriggers(QtGui.QTableWidget.NoEditTriggers)
        self.table_index.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table_index.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table_index.setVerticalScrollMode(QtGui.QTableView.ScrollPerPixel)
        self.table_index.setVerticalScrollBar(self.vscroll)
        self.table_index.setFrameStyle(QtGui.QFrame.Plain)
        self.table_index.verticalHeader().sectionResized.connect(self._row_resized)
        self.table_index.setItemDelegate(QtGui.QItemDelegate())
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
        self.table_data.setItemDelegate(QtGui.QItemDelegate())
        layout.addWidget(self.table_data, 1, 1)
        self.setFocusProxy(self.table_data)

        layout.addWidget(self.hscroll, 2, 0, 2, 2)
        layout.addWidget(self.vscroll, 0, 2, 2, 2)


    def _select_columns(self, source, dest, deselect):
        if self._selection_rec: return
        self._selection_rec = True
        dsm = dest.selectionModel()
        ssm = source.selectionModel()
        dsm.clear()
        for col in (index.column() for index in ssm.selectedIndexes()):
            dsm.select(dest.model().index(0, col),
                       QtGui.QItemSelectionModel.Select | QtGui.QItemSelectionModel.Columns)
        deselect.selectionModel().clear()
        self._selection_rec = False


    def _select_rows(self, source, dest, deselect):
        if self._selection_rec: return
        self._selection_rec = True
        dsm = dest.selectionModel()
        ssm = source.selectionModel()
        dsm.clear()
        for row in (index.row() for index in ssm.selectedIndexes()):
            dsm.select(dest.model().index(row, 0),
                       QtGui.QItemSelectionModel.Select | QtGui.QItemSelectionModel.Rows)
        deselect.selectionModel().clear()
        self._selection_rec = False


    def model(self):
        return self._model

    def _column_resized(self, col, old_width, new_width):
        self.table_data.setColumnWidth(col, new_width)
        self._update_layout()

    def _row_resized(self, row, old_height, new_height):
        self.table_data.setRowHeight(row, new_height)
        self._update_layout()

    def _index_resized(self, col, old_width, new_width):
        self.table_index.setColumnWidth(col, new_width)
        self._update_layout()

    def _header_resized(self, row, old_height, new_height):
        self.table_header.setRowHeight(row, new_height)
        self._update_layout()

    def _update_layout(self):
        h_width = max(self.table_level.verticalHeader().sizeHint().width(),
                      self.table_index.verticalHeader().sizeHint().width())
        self.table_level.verticalHeader().setFixedWidth(h_width)
        self.table_index.verticalHeader().setFixedWidth(h_width)

        last_row = self._model.header_shape()[0] - 1
        if last_row < 0:
            hdr_height = self.table_level.horizontalHeader().height()
        else:
            hdr_height = self.table_level.rowViewportPosition(last_row) + \
                         self.table_level.rowHeight(last_row) + \
                         self.table_level.horizontalHeader().height()
        self.table_header.setFixedHeight(hdr_height)
        self.table_level.setFixedHeight(hdr_height)

        last_col = self._model.header_shape()[1] - 1
        if last_col < 0:
            idx_width = self.table_level.verticalHeader().width()
        else:
            idx_width = self.table_level.columnViewportPosition(last_col) + \
                        self.table_level.columnWidth(last_col) + \
                        self.table_level.verticalHeader().width()
        self.table_index.setFixedWidth(idx_width)
        self.table_level.setFixedWidth(idx_width)


    def _reset_model(self, table, model):
        old_sel_model = table.selectionModel()
        table.setModel(model)
        if old_sel_model:
            del old_sel_model


    def setModel(self, model):
        self._model = model
        self._reset_model(self.table_data, Data4ExtModel(model))
        sel_model = self.table_data.selectionModel()
        sel_model.selectionChanged.connect(
            lambda *_: self._select_columns(self.table_data, self.table_header, self.table_level))
        sel_model.selectionChanged.connect(
            lambda *_: self._select_rows(self.table_data, self.table_index, self.table_level))

        self._reset_model(self.table_level, Level4ExtModel(model, self.palette(), self.font()))
        sel_model = self.table_level.selectionModel()
        sel_model.selectionChanged.connect(
            lambda *_: self._select_columns(self.table_level, self.table_index, self.table_data))
        sel_model.selectionChanged.connect(
            lambda *_: self._select_rows(self.table_level, self.table_header, self.table_data))

        self._reset_model(self.table_header, Header4ExtModel(model, 0, self.palette()))
        sel_model = self.table_header.selectionModel()
        sel_model.selectionChanged.connect(
            lambda *_: self._select_columns(self.table_header, self.table_data, self.table_index))
        sel_model.selectionChanged.connect(
            lambda *_: self._select_rows(self.table_header, self.table_level, self.table_index))

        self._reset_model(self.table_index, Header4ExtModel(model, 1, self.palette()))
        sel_model = self.table_index.selectionModel()
        sel_model.selectionChanged.connect(
            lambda *_: self._select_rows(self.table_index, self.table_data, self.table_header))
        sel_model.selectionChanged.connect(
            lambda *_: self._select_columns(self.table_index, self.table_level, self.table_header))

        # needs to be called after setting all table models
        self._update_layout()


    def setCurrentIndex(self, y, x):
        self.table_data.selectionModel().setCurrentIndex(
            self.table_data.model().index(y, x),
            QtGui.QItemSelectionModel.ClearAndSelect)

    def resizeIndexToContents(self):
        for col in range(self._model.header_shape()[1]):
            hdr_width = self.table_level.sizeHintForColumn(col)
            idx_width = self.table_index.sizeHintForColumn(col)
            if idx_width > hdr_width or hdr_width > idx_width * 2:
                width = idx_width
            else:
                width = hdr_width
            self.table_level.setColumnWidth(col, width)
        self._update_layout()

    def resizeColumnsToContents(self):
        for col in range(self._model.shape()[1]):
            hdr_width = self.table_header.sizeHintForColumn(col)
            data_width = self.table_data.sizeHintForColumn(col)
            if data_width > hdr_width or hdr_width > data_width * 2:
                width = data_width
            else:
                width = hdr_width
            self.table_header.setColumnWidth(col, width)
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

    def view(self, model, hdr_rows=None, idx_cols=None,
             start_pos=None, metavar=None, title=None):
        self.table.setModel(model)
        shape = model.shape()

        if title is not None:
            self.setWindowTitle(title)
        else:
            title = "{} rows, {} columns".format(shape[0], shape[1])
            if metavar:
                title = "{}: {}".format(metavar, title)
            self.setWindowTitle(title)

        if shape[0] * shape[1] < 16384:
            # resizing materializes the contents and might actually take longer
            # than loading all the data itself, so do it for small tables only
            self.table.resizeColumnsToContents()
        elif model.header_shape()[1] * shape[0] < 16384:
            # similarly for the index
            self.table.resizeIndexToContents()

        self.table.setFocus()
        if start_pos:
            y = shape[0] + start_pos[0] if start_pos[0] < 0 else start_pos[0]
            x = shape[1] + start_pos[1] if start_pos[1] < 0 else start_pos[1]
            self.table.setCurrentIndex(y, x)

        self.showNormal()
        self.setWindowState(QtCore.Qt.WindowActive)
        self.closed = False
