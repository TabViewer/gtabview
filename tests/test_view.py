# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import

from . import *
gtabview.WAIT=False
gtabview.DETACH=True


def test_view_vect():
    view([1, 2, 3])

def test_view_dict():
    view({'a': [1, 2, 3], 'b': [1, 2, 3]})

def test_view_list():
    view([[1, 2, 3], [1, 2, 3]])

def test_view_csv_latin1():
    view(os.path.join(SAMPLE_ROOT, "test_latin-1.csv"))

def test_view_csv_unicode():
    view(os.path.join(SAMPLE_ROOT, "unicode-example-utf8.txt"))

@require('pandas')
def test_view_frame():
    import pandas as pd
    view(pd.DataFrame([[1, 2, 3], [1, 2, 3]],
                      columns=['a', 'b', 'c'],
                      index=['x', 'y']))
