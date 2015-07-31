# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import

from . import *
from gtabview.dataio import read_table


def test_skip_empty_line_1():
    data, _ = read_table(os.path.join(TDATA_ROOT, 'empty-line-1.txt'), None, None, 1)
    assert(data == [['a', 'b', 'c'], ['1', '2', '3']])

def test_skip_empty_line_2():
    data, _ = read_table(os.path.join(TDATA_ROOT, 'empty-line-2.txt'), None, None, 1)
    assert(data == [['a', 'b', 'c'], ['1', '2', '3']])

def test_hash_headers():
    data, _ = read_table(os.path.join(TDATA_ROOT, 'hash-headers.txt'), None, None, 1)
    assert(data == [['a', 'b', 'c'], ['1', '2', '3']])

def test_xls_fallback():
    data, _ = read_table(os.path.join(TDATA_ROOT, 'not-xls.xls'), None, None, 1)
    assert(data == [['a', 'b', 'c'], ['1', '2', '3'], ['4', '5', '6']])

@require('xlrd')
def test_xls_read():
    data, _ = read_table(os.path.join(TDATA_ROOT, 'simple.xls'), None, None, 1)
    assert(data == [['a', 'b', 'c'], [1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
