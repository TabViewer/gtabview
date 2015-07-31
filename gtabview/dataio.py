# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import

import os
import sys
import warnings

from .compat import *


def _detect_encoding(data=None):
    """Return the default system encoding. If data is passed, try
    to decode the data with the default system encoding or from a short
    list of encoding types to test.

    Args:
        data - list of lists
    Returns:
        enc - system encoding
    """
    import locale
    enc_list = ['utf-8', 'latin-1', 'iso8859-1', 'iso8859-2',
                'utf-16', 'cp720']
    code = locale.getpreferredencoding(False)
    if data is None:
        return code
    if code.lower() not in enc_list:
        enc_list.insert(0, code.lower())
    for c in enc_list:
        try:
            for line in data:
                line.decode(c)
        except (UnicodeDecodeError, UnicodeError, AttributeError):
            continue
        return c
    print("Encoding not detected. Please pass encoding value manually")


def _parse_lines(data, enc=None, delimiter=None):
    import csv
    if enc is None:
        enc = _detect_encoding(data)
    if delimiter is None:
        delimiter = csv.Sniffer().sniff(data[0].decode(enc)).delimiter
    csv_data = []
    if sys.version_info.major < 3:
        csv_obj = csv.reader(data, delimiter=delimiter.encode(enc))
        for row in csv_obj:
            row = [x.decode(enc) for x in row]
            csv_data.append(row)
    else:
        data = [i.decode(enc) for i in data]
        csv_obj = csv.reader(data, delimiter=delimiter)
        for row in csv_obj:
            csv_data.append(row)
    return csv_data



def read_csv(fd_or_path, enc, delimiter, hdr_rows):
    if isinstance(fd_or_path, basestring):
        fd_or_path = open(fd_or_path, 'rb')
    return _parse_lines(fd_or_path.readlines(), enc, delimiter)


def read_xlrd(path, sheet_index):
    import xlrd
    wb = xlrd.open_workbook(path, on_demand=True, ragged_rows=True)
    sheet = wb.sheet_by_index(sheet_index)
    return [sheet.row_values(row) for row in range(sheet.nrows)]


def read_table(fd_or_path, enc, delimiter, hdr_rows, sheet_index=0):
    data = None

    # read into a list of lists
    if isinstance(fd_or_path, basestring):
        _, ext = os.path.splitext(fd_or_path)
        if ext.lower() in ['.xls', '.xlsx']:
            try:
                import xlrd
                data = read_xlrd(fd_or_path, sheet_index)
            except ImportError:
                warnings.warn("xlrd module not installed")
            except xlrd.XLRDError:
                pass
    if data is None:
        data = read_csv(fd_or_path, enc, delimiter, hdr_rows)

    if hdr_rows is None and len(data) > 1:
        hdr_rows = 1

    # chop a leading '#' in the headers
    if hdr_rows and len(data) >= hdr_rows:
        for row in range(hdr_rows):
            if len(data[row]) \
               and isinstance(data[row][0], basestring) \
               and len(data[row][0]) > 1 \
               and data[row][0][0] == '#':
                data[0][0] = data[0][0][1:]

    # skip an empty line after the header
    if hdr_rows and len(data) > hdr_rows + 1:
        empty = True
        for col in data[hdr_rows]:
            if col is not None and len(str(col)):
                empty = False
                break
        if empty:
            del data[hdr_rows]

    return data, hdr_rows
