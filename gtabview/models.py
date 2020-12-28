# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import, generators, division

from .compat import *


def getitem(lst, idx, default=None):
    return lst[idx] if idx < len(lst) else default

def getitem2(lst, y, x, default=None):
    return getitem(getitem(lst, y, []), x, default)


class ExtDataModel(object):
    @property
    def shape(self):
        raise Exception()

    @property
    def header_shape(self):
        raise Exception()

    def data(self, y, x):
        raise Exception()

    def header(self, axis, x, level):
        raise Exception()

    def name(self, axis, level):
        return 'L' + str(level)

    @property
    def chunk_size(self):
        return max(*self.shape())

    def transpose(self):
        # TODO: remove from base model
        return TransposedExtDataModel(self)


class TransposedExtDataModel(ExtDataModel):
    def __init__(self, model):
        super(TransposedExtDataModel, self).__init__()
        self._model = model

    @property
    def shape(self):
        x, y = self._model.shape
        return (y, x)

    @property
    def header_shape(self):
        x, y = self._model.header_shape
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

    @property
    def shape(self):
        return self._shape

    @property
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
    def __init__(self, data, sort=False):
        super(ExtMapModel, self).__init__()
        self._data = data
        self._keys = list(sorted(data.keys()) if sort else data.keys())
        h = max([len(x) for x in data.values()]) if self._keys else 0
        self._shape = (h, len(self._keys))

    @property
    def shape(self):
        return self._shape

    @property
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

    @property
    def shape(self):
        return (len(self._data), 1)

    @property
    def header_shape(self):
        return (0, 0)

    def data(self, y, x):
        return self._data[y]


class ExtMatrixModel(ExtDataModel):
    def __init__(self, data):
        super(ExtMatrixModel, self).__init__()
        self._data = data

    @property
    def shape(self):
        return self._data.shape

    @property
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

    @property
    def shape(self):
        return self._data.shape

    @property
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


def _data_lower(data, sort):
    if data.__class__.__name__ in ['Series', 'Panel']:
        # handle panels and series as frames
        return data.to_frame()
    if not hasattr(data, '__array__') and not hasattr(data, '__getitem__') and \
       hasattr(data, '__iter__') and hasattr(data, '__len__'):
        # flatten iterables but non-indexables to lists (ie: sets)
        if sort and isinstance(data, (set, frozenset)):
            data = sorted(data)
        return list(data)

    return data


def as_model(data, hdr_rows=0, idx_cols=0, transpose=False, sort=False):
    model = None
    if isinstance(data, ExtDataModel):
        model = data
    else:
        data = _data_lower(data, sort)

        if hasattr(data, '__array__') and hasattr(data, 'iat') and \
           hasattr(data, 'index') and hasattr(data, 'columns'):
            model = ExtFrameModel(data)
        elif hasattr(data, '__array__') and len(data.shape) >= 2:
            model = ExtMatrixModel(data)
        elif hasattr(data, '__getitem__') and hasattr(data, '__len__') and \
             hasattr(data, 'keys') and hasattr(data, 'values'):
            model = ExtMapModel(data, sort)
        elif hasattr(data, '__getitem__') and hasattr(data, '__len__') and len(data) and \
             hasattr(data[0], '__getitem__') and hasattr(data[0], '__len__') and \
             not isinstance(data[0], (bytes, str)):
            model = ExtListModel(data, hdr_rows=hdr_rows, idx_cols=idx_cols)
        elif hasattr(data, '__getitem__') and hasattr(data, '__len__'):
            model = ExtVectorModel(data)

    if transpose and model:
        model = model.transpose()
    return model
