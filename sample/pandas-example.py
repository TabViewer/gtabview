#!/usr/bin/env python
import pandas as pd
import numpy as np
import gtabview

c_arr = [['bar', 'bar', 'baz', 'baz', 'foo', 'foo', 'qux', 'qux'],
          ['one', 'two', 'one', 'two', 'one', 'two', 'one', 'two']]
columns = pd.MultiIndex.from_tuples(list(zip(*c_arr)), names=['V1', 'V2'])

i_arr = [['bar', 'bar', 'bar', 'bar', 'baz', 'baz', 'baz', 'baz'],
         ['foo', 'foo', 'qux', 'qux', 'foo', 'foo', 'qux', 'qux'],
         ['one', 'two', 'one', 'two', 'one', 'two', 'one', 'two']]
index = pd.MultiIndex.from_tuples(list(zip(*i_arr)), names=['H1', 'H2', 'H3'])

df = pd.DataFrame(np.random.randn(8, 8), columns=columns, index=index)
gtabview.view(df)
