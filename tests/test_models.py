# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import

from tests import *
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
    assert(materialize_header(model, 1) == [[], [], []])

def test_model_list():
    model = as_model([[1, 2, 3], [1, 2, 3]])
    assert(model.header_shape() == (0, 0))
    assert(model.shape() == (2, 3))
    assert(materialize(model) == [[1, 2, 3], [1, 2, 3]])
