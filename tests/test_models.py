# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import

from . import *
from gtabview.models import as_model


def test_model_id():
    model = as_model([1, 2, 3])
    assert(as_model(model) is model)

def test_model_vect():
    model = as_model([1, 2, 3])
    assert(model.header_shape == (0, 0))
    assert(model.shape == (3, 1))
    assert(materialize(model) == [[1], [2], [3]])

def test_model_vect_str():
    model = as_model(['aaa', 'bbb', 'ccc'])
    assert(model.header_shape == (0, 0))
    assert(model.shape == (3, 1))
    assert(materialize(model) == [['aaa'], ['bbb'], ['ccc']])

def test_model_set():
    model = as_model({'a', 'b', 'c'})
    assert(model.header_shape == (0, 0))
    assert(model.shape == (3, 1))
    assert(sorted(materialize(model)) == [['a'], ['b'], ['c']])

def test_model_iterable():
    model = as_model(sorted(['c', 'b', 'a']))
    assert(model.header_shape == (0, 0))
    assert(model.shape == (3, 1))
    assert(materialize(model) == [['a'], ['b'], ['c']])

def test_model_dict():
    model = as_model({'a': [1, 2, 3], 'b': [1, 2, 3]})
    assert(model.header_shape == (1, 0))
    assert(model.shape == (3, 2))
    assert(materialize(model) == [[1, 1], [2, 2], [3, 3]])
    assert(sorted(materialize_header(model, 0)) == [['a', 'b']])
    assert(materialize_header(model, 1) == [])

def test_model_ordered_dict():
    from collections import OrderedDict
    model = as_model(OrderedDict([('b', [1, 2, 3]), ('a', [1, 2, 3])]))
    assert(model.header_shape == (1, 0))
    assert(model.shape == (3, 2))
    assert(materialize(model) == [[1, 1], [2, 2], [3, 3]])
    assert(materialize_header(model, 0) == [['b', 'a']])
    assert(materialize_header(model, 1) == [])

def test_model_ordered_dict_sort():
    from collections import OrderedDict
    model = as_model(OrderedDict([('b', [1, 2, 3]), ('a', [1, 2, 3])]), sort=True)
    assert(model.header_shape == (1, 0))
    assert(model.shape == (3, 2))
    assert(materialize(model) == [[1, 1], [2, 2], [3, 3]])
    assert(materialize_header(model, 0) == [['a', 'b']])
    assert(materialize_header(model, 1) == [])

def test_model_dict_ragged():
    model = as_model({'a': [1, 2], 'b': [1, 2, 3]})
    assert(model.header_shape == (1, 0))
    assert(model.shape == (3, 2))
    assert(materialize(model) == [[1, 1], [2, 2], [None, 3]])
    assert(materialize_header(model, 0) == [['a', 'b']])
    assert(materialize_header(model, 1) == [])

def test_model_list():
    model = as_model([[1, 2, 3], [1, 2, 3]])
    assert(model.header_shape == (0, 0))
    assert(model.shape == (2, 3))
    assert(materialize(model) == [[1, 2, 3], [1, 2, 3]])

def test_model_list_hdr_idx():
    model = as_model([[None, 'a', 'b', 'c'], ['x', 1, 2, 3], ['y', 1, 2, 3]], hdr_rows=1, idx_cols=1)
    assert(model.header_shape == (1, 1))
    assert(model.shape == (2, 3))
    assert(materialize(model) == [[1, 2, 3], [1, 2, 3]])
    assert(materialize_header(model, 0) == [['a', 'b', 'c']])
    assert(materialize_header(model, 1) == [['x', 'y']])

def test_model_list_ragged():
    model = as_model([[1, 2], [1, 2, 3]])
    assert(model.header_shape == (0, 0))
    assert(model.shape == (2, 3))
    assert(materialize(model) == [[1, 2, None], [1, 2, 3]])

@require('pandas')
def test_model_frame():
    import pandas as pd
    model = as_model(pd.DataFrame([[1, 2, 3], [1, 2, 3]],
                                  columns=['a', 'b', 'c'],
                                  index=['x', 'y']))
    assert(model.header_shape == (1, 1))
    assert(model.shape == (2, 3))
    assert(materialize(model) == [[1, 2, 3], [1, 2, 3]])
    assert(materialize_header(model, 0) == [['a', 'b', 'c']])
    assert(materialize_header(model, 1) == [['x', 'y']])

@require('pandas')
def test_model_frame_multiindex():
    import pandas as pd
    col_index = pd.MultiIndex.from_tuples(
        list(zip(['A', 'B', 'C'], ['a', 'b', 'c'])),
        names=['CL0', 'CL1'])
    row_index = pd.MultiIndex.from_tuples(
        list(zip(['X', 'Y'], ['x', 'y'])),
        names=['RL0', 'RL1'])
    model = as_model(pd.DataFrame([[1, 2, 3], [1, 2, 3]],
                                  columns=col_index,
                                  index=row_index))
    assert(model.header_shape == (2, 2))
    assert(model.shape == (2, 3))
    assert(materialize(model) == [[1, 2, 3], [1, 2, 3]])
    assert(materialize_header(model, 0) == [['A', 'B', 'C'], ['a', 'b', 'c']])
    assert(materialize_header(model, 1) == [['X', 'Y'], ['x', 'y']])
    assert(materialize_names(model, 0) == ['CL0', 'CL1'])
    assert(materialize_names(model, 1) == ['RL0', 'RL1'])

@require('pandas')
def test_model_transpose():
    import pandas as pd
    col_index = pd.MultiIndex.from_tuples(
        list(zip(['A', 'B', 'C'], ['a', 'b', 'c'])),
        names=['CL0', 'CL1'])
    row_index = pd.MultiIndex.from_tuples(
        list(zip(['X', 'Y'], ['x', 'y'])),
        names=['RL0', 'RL1'])
    model = as_model(pd.DataFrame([[1, 2, 3], [1, 2, 3]],
                                  columns=col_index,
                                  index=row_index),
                     transpose=True)
    assert(model.header_shape == (2, 2))
    assert(model.shape == (3, 2))
    assert(materialize(model) == [[1, 1], [2, 2], [3, 3]])
    assert(materialize_header(model, 0) == [['X', 'Y'], ['x', 'y']])
    assert(materialize_header(model, 1) == [['A', 'B', 'C'], ['a', 'b', 'c']])
    assert(materialize_names(model, 0) == ['RL0', 'RL1'])
    assert(materialize_names(model, 1) == ['CL0', 'CL1'])

@require('pandas')
def test_model_series():
    import pandas as pd
    model = as_model(pd.Series([1, 2, 3], name='serie', index=['x', 'y', 'z']))
    assert(model.header_shape == (1, 1))
    assert(model.shape == (3, 1))
    assert(materialize(model) == [[1], [2], [3]])
    assert(materialize_header(model, 0) == [['serie']])
    assert(materialize_header(model, 1) == [['x', 'y', 'z']])

@require('numpy')
def test_model_array():
    import numpy as np
    model = as_model(np.array([[1, 2, 3], [1, 2, 3]]))
    assert(model.header_shape == (0, 0))
    assert(model.shape == (2, 3))
    assert(materialize(model) == [[1, 2, 3], [1, 2, 3]])

@require('numpy')
def test_model_matrix():
    import numpy as np
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', PendingDeprecationWarning)
        model = as_model(np.matrix([[1, 2, 3], [1, 2, 3]]))
    assert(model.header_shape == (0, 0))
    assert(model.shape == (2, 3))
    assert(materialize(model) == [[1, 2, 3], [1, 2, 3]])
