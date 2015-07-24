# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import

import sys
import csv

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


def read_table(fd_or_path, enc, delimiter, hdr_rows):
    # read into a list of lists
    if isinstance(fd_or_path, basestring):
        with open(fd_or_path, 'rb') as fd:
            data = _parse_lines(fd.readlines(), enc, delimiter)
    else:
        data = _parse_lines(fd_or_path.readlines(), enc, delimiter)

    if hdr_rows is None and len(data) > 1:
        hdr_rows = 1

    # chop a leading '#' in the headers
    if hdr_rows and len(data) >= hdr_rows:
        for row in range(hdr_rows):
            if len(data[row]) and len(data[row][0]) and data[row][0][0] == '#':
                data[0][0] = data[0][0][1:]

    # skip an empty line after the header
    if hdr_rows and len(data) > hdr_rows + 1:
        empty = True
        for col in data[hdr_rows]:
            if len(col):
                empty = False
                break
        if empty:
            del data[hdr_rows]

    return data
