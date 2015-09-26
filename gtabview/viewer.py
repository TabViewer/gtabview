# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import, generators
from .compat import *
from . import models
import math

AUTOSIZE_LIMIT = models.DEFAULT_CHUNK_SIZE
MIN_TRUNC_CHARS = 8
MAX_WIDTH_CHARS = 64


# Support PyQt4/PySide with either Python 2/3
try:
    from PyQt4 import QtCore, QtGui
except ImportError:
    from PySide import QtCore, QtGui


def as_str(obj):
    if obj is None: return ''
    if isinstance(obj, float) and math.isnan(obj): return ''
    return str(obj)


class Data4ExtModel(QtCore.QAbstractTableModel):
    def __init__(self, model):
        super(Data4ExtModel, self).__init__()
        self.model = model

    def rowCount(self, index=None):
        return max(1, self.model.shape()[0])

    def columnCount(self, index=None):
        return max(1, self.model.shape()[1])

    def data(self, index, role):
        if role != QtCore.Qt.DisplayRole:
            return None
        if index.row() >= self.model.shape()[0] or \
           index.column() >= self.model.shape()[1]:
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
        if not index.isValid() or \
           index.row() >= self._shape[0] or \
           index.column() >= self._shape[1]:
            return None
        row, col = (index.row(), index.column()) if self.axis == 0 \
                   else (index.column(), index.row())
        if role == QtCore.Qt.BackgroundRole:
            prev = self.model.header(self.axis, col - 1, row) if col else None
            cur = self.model.header(self.axis, col, row)
            return self._palette.midlight() if prev != cur else None
        if role != QtCore.Qt.DisplayRole:
            return None
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

        # autosize columns on-demand
        self._autosized_cols = set()
        self._autosize_limit = None
        self.hscroll.sliderMoved.connect(self._resizeVisibleColumnsToContents)
        self.table_data.installEventFilter(self)

        avg_width = self.fontMetrics().averageCharWidth()
        self.min_trunc = avg_width * MIN_TRUNC_CHARS
        self.max_width = avg_width * MAX_WIDTH_CHARS


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
        self._resizeVisibleColumnsToContents()


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
        sel_model.currentColumnChanged.connect(self._resizeCurrentColumnToContents)

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

    def _sizeHintForColumn(self, table, col, limit):
        # TODO: use current chunk boundaries, do not start from the beginning
        max_row = table.model().rowCount()
        if limit is not None:
            max_row = min(max_row, limit)
        max_width = 0
        for row in range(max_row):
            v = table.sizeHintForIndex(table.model().index(row, col))
            max_width = max(max_width, v.width())
        return max_width

    def _resizeColumnToContents(self, header, data, col, limit):
        hdr_width = self._sizeHintForColumn(header, col, limit)
        data_width = self._sizeHintForColumn(data, col, limit)
        if data_width > hdr_width:
            width = min(self.max_width, data_width)
        elif hdr_width > data_width * 2:
            width = max(min(hdr_width, self.min_trunc), min(self.max_width, data_width))
        else:
            width = min(self.max_width, hdr_width)
        header.setColumnWidth(col, width)

    def _resizeColumnsToContents(self, header, data, limit):
        max_col = data.model().columnCount()
        if limit is not None:
            max_col = min(max_col, limit)
        for col in range(max_col):
            self._resizeColumnToContents(header, data, col, limit)

    def eventFilter(self, obj, event):
        if obj == self.table_data and event.type() == QtCore.QEvent.Resize:
            self._resizeVisibleColumnsToContents()
        return False

    def _resizeVisibleColumnsToContents(self):
        col = self.table_data.columnAt(self.table_data.rect().topLeft().x())
        width = self._model.shape()[1]
        end = self.table_data.columnAt(self.table_data.rect().bottomRight().x())
        end = width if end == -1 else end + 1
        while col < end:
            resized = False
            if col not in self._autosized_cols:
                self._autosized_cols.add(col)
                resized = True
                self._resizeColumnToContents(self.table_header, self.table_data,
                                             col, self._autosize_limit)
            col += 1
            if resized:
                # as we resize columns, the boundary will change
                end = self.table_data.columnAt(self.table_data.rect().bottomRight().x())
                end = width if end == -1 else end + 1

    def _resizeCurrentColumnToContents(self, new_index, old_index):
        if new_index.column() not in self._autosized_cols:
            # ensure the requested column is fully into view after resizing
            self._resizeVisibleColumnsToContents()
            self.table_data.scrollTo(new_index)

    def resizeColumnsToContents(self, limit=None):
        self._autosized_cols = set()
        self._autosize_limit = limit
        self._resizeColumnsToContents(self.table_level, self.table_index, limit)
        self._update_layout()


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

        # resizing materializes the contents and might actually take longer
        # than loading all the data itself, so do it only on a single chunk
        self.table.resizeColumnsToContents(min(AUTOSIZE_LIMIT, model.chunk_size()))

        self.table.setFocus()
        if start_pos:
            y = shape[0] + start_pos[0] if start_pos[0] < 0 else start_pos[0]
            x = shape[1] + start_pos[1] if start_pos[1] < 0 else start_pos[1]
            self.table.setCurrentIndex(y, x)

        self.showNormal()
        self.setWindowState(QtCore.Qt.WindowActive)
        self.closed = False
