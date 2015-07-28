# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import

import gtabview
from gtabview import view

import importlib
import nose
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
SAMPLE_ROOT = os.path.join(PROJECT_ROOT, "sample")
TDATA_ROOT = os.path.join(PROJECT_ROOT, os.path.dirname(__file__), "data")


class require(object):
    def __init__(self, module):
        self.module = module

    def __call__(self, func):
        def wrapper():
            try:
                importlib.import_module(self.module)
            except ImportError:
                raise nose.SkipTest("requires {}".format(self.module))
            return func()
        wrapper.__name__ = func.__name__
        return wrapper


def materialize(model):
    shape = model.shape()
    return [[model.data(y, x) for x in range(shape[1])] for y in range(shape[0])]

def materialize_header(model, axis):
    shape = model.shape()
    header_shape = model.header_shape()
    if axis == 0:
        return [[model.header(axis, x, level) for x in range(shape[1])] for level in range(header_shape[0])]
    else:
        return [[model.header(axis, x, level) for x in range(shape[0])] for level in range(header_shape[1])]

def materialize_names(model, axis):
    shape = model.header_shape()
    return [model.name(axis, x) for x in range(shape[axis])]
