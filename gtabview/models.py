# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import, generators

from .compat import *
import collections


class ExtDataModel(object):
    def shape(self):
        pass

    def header_shape(self):
        pass

    def data(self, y, x):
        pass

    def header(self, axis, x, level):
        pass


class ExtListModel(ExtDataModel):
    def __init__(self, data, hdr_rows=None, idx_cols=None):
        super(ExtListModel, self).__init__()
        if hdr_rows is None:
            hdr_rows = 1 if len(data) > 1 else 0
        if idx_cols is None:
            idx_cols = 0
        self._header_shape = (hdr_rows, idx_cols)
        self._shape = (len(data) - hdr_rows, len(data[0]) - idx_cols)
        self._data = data

    def shape(self):
        return self._shape

    def header_shape(self):
        return self._header_shape

    def header(self, axis, x, level):
        if axis == 0:
            return self._data[level][x + self._header_shape[1]]
        else:
            return self._data[x + self._header_shape[0]][level]

    def data(self, y, x):
        return self._data[y + self._header_shape[0]][x + self._header_shape[1]]


class ExtVectorModel(ExtDataModel):
    def __init__(self, data):
        super(ExtVectorModel, self).__init__()
        self._data = data

    def shape(self):
        return (len(self._data), 1)

    def header_shape(self):
        return (0, 0)

    def data(self, y, x):
        return self._data[y]


class ExtMatrixModel(ExtDataModel):
    def __init__(self, data):
        super(ExtMatrixModel, self).__init__()
        self._data = data

    def shape(self):
        return self._data.shape

    def header_shape(self):
        return (0, 0)

    def data(self, y, x):
        return self._data[y, x]


class ExtFrameModel(ExtDataModel):
    def __init__(self, data):
        super(ExtFrameModel, self).__init__()
        self._data = data

    def _axis(self, axis):
        return self._data.columns if axis == 0 else self._data.index

    def _axis_levels(self, axis):
        ax = self._axis(axis)
        return 1 if not hasattr(ax, 'levels') \
            else len(ax.levels)

    def shape(self):
        return self._data.shape

    def header_shape(self):
        return (self._axis_levels(0), self._axis_levels(1))

    def data(self, y, x):
        return str(self._data.iat[y, x])

    def header(self, axis, x, level=0):
        ax = self._axis(axis)
        return str(ax.values[x]) if not hasattr(ax, 'levels') \
            else str(ax.values[x][level])


def as_model(data, hdr_rows=None, idx_cols=None):
    if isinstance(data, ExtDataModel):
        return data

    # TODO: add specific data models to reduce overhead
    if data.__class__.__name__ in ['Series', 'Panel']:
        data = data.to_frame()
    elif isinstance(data, dict):
        data = [data.keys()] + list(map(list, zip(*[data[i] for i in data.keys()])))

    if data.__class__.__name__ == 'DataFrame':
        return ExtFrameModel(data)
    elif data.__class__.__name__ == 'ndarray':
        return ExtMatrixModel(data)
    elif isinstance(data, collections.Sequence) and \
         isinstance(data[0], collections.Sequence):
        return ExtListModel(data, hdr_rows=hdr_rows, idx_cols=idx_cols)
    elif isinstance(data, collections.Sequence):
        return ExtVectorModel(data)

    return None
