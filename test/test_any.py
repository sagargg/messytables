# -*- coding: utf-8 -*-
import unittest

from . import horror_fobj
from nose.tools import assert_equal
from messytables import (any_tableset, XLSTableSet, ZIPTableSet, PDFTableSet,
                         CSVTableSet, ODSTableSet, ABBYYTableSet,
                         ReadError)
import messytables.any

suite = [{'filename': 'simple.csv', 'tableset': CSVTableSet},
         {'filename': 'simple.xls', 'tableset': XLSTableSet},
         {'filename': 'simple.xlsx', 'tableset': XLSTableSet},
         {'filename': 'simple.zip', 'tableset': ZIPTableSet},
         {'filename': 'simple.ods', 'tableset': ODSTableSet},
         {'filename': 'simple.pdf', 'tableset': PDFTableSet},
         {'filename': 'bian-anal-mca-2005-dols-eng-1011-0312-tab3.xlsm', 'tableset': XLSTableSet},
         ]


def test_simple():
    for d in suite:
        yield check_no_filename, d
        yield check_filename, d


def check_no_filename(d):
    fh = horror_fobj(d['filename'])
    table_set = any_tableset(fh)
    assert isinstance(table_set, d['tableset']), type(table_set)


def check_filename(d):
    fh = horror_fobj(d['filename'])
    table_set = any_tableset(fh, extension=d['filename'], auto_detect=False)
    assert isinstance(table_set, d['tableset']), type(table_set)


def test_override():
    fh = horror_fobj('simple.pdf')
    old_parse = messytables.any.parsers
    messytables.any.parsers['PDF'] = messytables.abbyy.ABBYYTableSet
    try:
        table_set = any_tableset(fh)
    except ABBYYTableSet.ABBYYAuthError:
        return  # Failed due to authentication; means right function was called!
    assert isinstance(table_set, messytables.abbyy.ABBYYTableSet)


class TestAny(unittest.TestCase):
    def test_xlsm(self):
        fh = horror_fobj('bian-anal-mca-2005-dols-eng-1011-0312-tab3.xlsm')
        table_set = any_tableset(fh, extension='xls')
        row_set = table_set.tables[0]
        data = list(row_set)
        assert_equal(62, len(data))

    def test_unknown(self):
        fh = horror_fobj('simple.unknown')
        self.assertRaises(ReadError, lambda: any_tableset(fh, extension='unknown'))
