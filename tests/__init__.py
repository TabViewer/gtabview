# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import

import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
SAMPLE_ROOT = os.path.join(PROJECT_ROOT, "sample")

import gtabview
from gtabview import view


def materialize(model):
    shape = model.shape()
    return [[model.data(y, x) for x in range(shape[1])] for y in range(shape[0])]

def materialize_header(model, axis):
    shape = model.shape()
    header_shape = model.header_shape()
    if axis == 0:
        return [[model.header(axis, x, level) for x in range(shape[1])] for level in range(header_shape[0])]
    else:
        return [[model.header(axis, x, level) for x in range(header_shape[1])] for level in range(shape[0])]
