#!/usr/bin/env python
import blaze as bz
import gtabview

data = bz.Data('data_ohlcv.csv')
gtabview.view(data)
