# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import

from . import *
from gtabview.dataio import read_table


def test_skip_empty_line_1():
    data = read_table(os.path.join(TDATA_ROOT, 'empty-line-1.txt'), None, None, 1)
    assert(data == [['a', 'b', 'c'], ['1', '2', '3']])

def test_skip_empty_line_2():
    data = read_table(os.path.join(TDATA_ROOT, 'empty-line-2.txt'), None, None, 1)
    assert(data == [['a', 'b', 'c'], ['1', '2', '3']])

def test_hash_headers():
    data = read_table(os.path.join(TDATA_ROOT, 'hash-headers.txt'), None, None, 1)
    assert(data == [['a', 'b', 'c'], ['1', '2', '3']])
