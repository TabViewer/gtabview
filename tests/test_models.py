# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import

from . import *
from gtabview.models import as_model


def test_model_vect():
    model = as_model([1, 2, 3])
    assert(model.header_shape() == (0, 0))
    assert(model.shape() == (3, 1))
    assert(materialize(model) == [[1], [2], [3]])

def test_model_dict():
    model = as_model({'a': [1, 2, 3], 'b': [1, 2, 3]})
    assert(model.header_shape() == (1, 0))
    assert(model.shape() == (3, 2))
    assert(materialize(model) == [[1, 1], [2, 2], [3, 3]])
    assert(materialize_header(model, 0) == [['a', 'b']])
    assert(materialize_header(model, 1) == [])

def test_model_list():
    model = as_model([[1, 2, 3], [1, 2, 3]])
    assert(model.header_shape() == (0, 0))
    assert(model.shape() == (2, 3))
    assert(materialize(model) == [[1, 2, 3], [1, 2, 3]])

@require('pandas')
def test_model_frame():
    import pandas as pd
    model = as_model(pd.DataFrame([[1, 2, 3], [1, 2, 3]],
                                  columns=['a', 'b', 'c'],
                                  index=['x', 'y']))
    assert(model.header_shape() == (1, 1))
    assert(model.shape() == (2, 3))
    assert(materialize(model) == [[1, 2, 3], [1, 2, 3]])
    assert(materialize_header(model, 0) == [['a', 'b', 'c']])
    assert(materialize_header(model, 1) == [['x', 'y']])

@require('pandas')
def test_model_series():
    import pandas as pd
    model = as_model(pd.Series([1, 2, 3], name='serie', index=['x', 'y', 'z']))
    assert(model.header_shape() == (1, 1))
    assert(model.shape() == (3, 1))
    assert(materialize(model) == [[1], [2], [3]])
    assert(materialize_header(model, 0) == [['serie']])
    assert(materialize_header(model, 1) == [['x', 'y', 'z']])
