# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import

import gtabview
from gtabview import view

gtabview.WAIT=False
gtabview.DETACH=True

def test_view_vect():
    view([1, 2, 3])

def test_view_dict():
    view({'a': [1, 2, 3], 'b': [1, 2, 3]})

def test_view_list():
    view([[1, 2, 3], [1, 2, 3]])
