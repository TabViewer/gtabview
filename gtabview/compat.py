# -*- coding: utf-8 -*-
import io, sys

if sys.version_info.major < 3:
    # Python 2.7 shim
    str = unicode
else:
    basestring = str
    file = io.FileIO
