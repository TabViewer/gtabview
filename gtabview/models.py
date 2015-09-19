# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import, generators, division

from .compat import *
from collections import deque

DEFAULT_CHUNK_SIZE = 16384
DEFAULT_LRU_SIZE   = 9


def getitem(lst, idx, default=None):
    return lst[idx] if idx < len(lst) else default

def getitem2(lst, y, x, default=None):
    return getitem(getitem(lst, y, []), x, default)


class ExtDataModel(object):
    def shape(self):
        raise Exception()

    def header_shape(self):
        raise Exception()

    def data(self, y, x):
        raise Exception()

    def header(self, axis, x, level):
        raise Exception()

    def name(self, axis, level):
        return 'L' + str(level)

    def chunk_size(self):
        return max(*self.shape())

    def transpose(self):
        # TODO: remove from base model
        return TransposedExtDataModel(self)


class TransposedExtDataModel(ExtDataModel):
    def __init__(self, model):
        super(TransposedExtDataModel, self).__init__()
        self._model = model

    def shape(self):
        x, y = self._model.shape()
        return (y, x)

    def header_shape(self):
        x, y = self._model.header_shape()
        return (y, x)

    def data(self, y, x):
        return self._model.data(x, y)

    def header(self, axis, x, level):
        return self._model.header(not axis, x, level)

    def name(self, axis, level):
        return self._model.name(not axis, level)

    def transpose(self):
        return self._model



class ExtListModel(ExtDataModel):
    def __init__(self, data, hdr_rows=0, idx_cols=0):
        super(ExtListModel, self).__init__()
        self._header_shape = (hdr_rows, idx_cols)
        self._shape = (len(data) - hdr_rows, max(map(len, data)) - idx_cols)
        self._data = data

    def shape(self):
        return self._shape

    def header_shape(self):
        return self._header_shape

    def header(self, axis, x, level):
        if axis == 0:
            return getitem2(self._data, level, x + self._header_shape[1])
        else:
            return getitem2(self._data, x + self._header_shape[0], level)

    def data(self, y, x):
        return getitem2(self._data, y + self._header_shape[0],
                        x + self._header_shape[1])


class ExtMapModel(ExtDataModel):
    def __init__(self, data):
        super(ExtMapModel, self).__init__()
        self._data = data
        self._keys = list(data.keys())
        h = max((len(x) for x in data.values()))
        self._shape = (h, len(self._keys))

    def shape(self):
        return self._shape

    def header_shape(self):
        return (1, 0)

    def data(self, y, x):
        return getitem(self._data[self._keys[x]], y)

    def header(self, axis, x, level):
        return self._keys[x]


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


class ExtBlazeModel(ExtDataModel):
    class Chunk(object):
        def __init__(self, data, off):
            self.data = data
            self.off = off

    def __init__(self, data, chunk_size=DEFAULT_CHUNK_SIZE, lru_size=DEFAULT_LRU_SIZE):
        super(ExtBlazeModel, self).__init__()
        self._data = data
        self._chunk_size = chunk_size
        self._shape = (int(data.nrows), len(data.fields))
        self._lru = deque([], lru_size)

    def shape(self):
        return self._shape

    def header_shape(self):
        return (1, 0)

    def _chunk_get(self, off):
        cols = self._data.fields[off[1]:min(self._shape[1], off[1]+self._chunk_size)]
        data = list(self._data[cols][off[0]:min(self._shape[0], off[0]+self._chunk_size)])
        return ExtBlazeModel.Chunk(data, off)

    def _chunk_at(self, y, x):
        off = (y // self._chunk_size * self._chunk_size,
               x // self._chunk_size * self._chunk_size)
        for slot, chunk in enumerate(self._lru):
            if chunk.off == off:
                if slot:
                    self._lru[slot] = self._lru[0]
                    self._lru[0] = chunk
                return chunk
        chunk = self._chunk_get(off)
        self._lru.appendleft(chunk)
        return chunk

    def data(self, y, x):
        chunk = self._chunk_at(y, x)
        return chunk.data[y - chunk.off[0]][x - chunk.off[1]]

    def header(self, axis, x, level=0):
        return self._data.fields[x]

    def chunk_size(self):
        return self._chunk_size


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
        return self._data.iat[y, x]

    def header(self, axis, x, level=0):
        ax = self._axis(axis)
        return ax.values[x] if not hasattr(ax, 'levels') \
            else ax.values[x][level]

    def name(self, axis, level):
        ax = self._axis(axis)
        if hasattr(ax, 'levels'):
            return ax.names[level]
        if ax.name:
            return ax.name
        return super(ExtFrameModel, self).name(axis, level)


def _data_lower(data):
    # TODO: add specific data models to reduce overhead
    if data.__class__.__name__ in ['Series', 'Panel']:
        return data.to_frame()
    return data


def as_model(data, hdr_rows=0, idx_cols=0, transpose=False):
    model = None
    if isinstance(data, ExtDataModel):
        model = data
    else:
        data = _data_lower(data)

        if hasattr(data, '__array__') and hasattr(data, 'iat') and \
           hasattr(data, 'index') and hasattr(data, 'columns'):
            model = ExtFrameModel(data)
        elif hasattr(data, '__array__') and hasattr(data, 'dshape') and \
             hasattr(data, 'nrows') and hasattr(data, 'fields'):
            model = ExtBlazeModel(data)
        elif hasattr(data, '__array__') and len(data.shape) >= 2:
            model = ExtMatrixModel(data)
        elif hasattr(data, '__getitem__') and hasattr(data, '__len__') and \
             hasattr(data, 'keys') and hasattr(data, 'values'):
            model = ExtMapModel(data)
        elif hasattr(data, '__getitem__') and hasattr(data, '__len__') and \
             hasattr(data[0], '__getitem__') and hasattr(data[0], '__len__'):
            model = ExtListModel(data, hdr_rows=hdr_rows, idx_cols=idx_cols)
        elif hasattr(data, '__getitem__') and hasattr(data, '__len__'):
            model = ExtVectorModel(data)

    if transpose and model:
        model = model.transpose()
    return model
