# -*- coding: utf-8 -*-
# qtpy: wrapper to support PyQt5/PyQt4/PySide with either Python 2/3
# Similar in spirit to QtPy, minus the dependency (as long as we can)
import os, sys

# Use existing Qt when previously loaded
if 'QT_API' not in os.environ:
    if 'PyQt5' in sys.modules:
        os.environ['QT_API'] = 'pyqt5'
    elif 'PyQt4' in sys.modules:
        os.environ['QT_API'] = 'pyqt4'
    elif 'PySide' in sys.modules:
        os.environ['QT_API'] = 'pyside'

# Autodetect what's available
if 'QT_API' not in os.environ:
    try:
        import PyQt5
        os.environ['QT_API'] = 'pyqt5'
    except ImportError:
        pass
if 'QT_API' not in os.environ:
    try:
        import PyQt4
        os.environ['QT_API'] = 'pyqt4'
    except ImportError:
        pass
if 'QT_API' not in os.environ:
    try:
        import PySide
        os.environ['QT_API'] = 'pyside'
    except ImportError:
        pass

# Actual module import
if os.environ['QT_API'] == 'pyqt5':
    from PyQt5 import QtCore, QtGui, QtWidgets
elif os.environ['QT_API'] == 'pyside':
    from PySide import QtCore, QtGui
else:
    from PyQt4 import QtCore, QtGui

# Qt5 stubs
if os.environ['QT_API'] != 'pyqt5':
    QtWidgets = QtGui
    QtCore.QItemSelectionModel = QtGui.QItemSelectionModel
