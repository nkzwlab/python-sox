#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import dateutil.tz as tz
from unittest import TestCase
from nose.tools import ok_, eq_

from pysox import soxtimestamp


class SoxTimestampTestCase(TestCase):
    """XEP-0082 http://xmpp.org/extensions/xep-0082.html"""

    def test_timestamp(self):
        tz_utc = tz.tzutc()
        tz_jst = tz.tzoffset('JST', 3600 * 9)
        tz_pst = tz.tzoffset('PST', 3600 * -8)

        def _total_second(td):
            return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6 

        tz_local = tz.tzlocal()
        tz_local_offset = _total_second(tz_local.utcoffset(datetime.datetime.now()))
        assert tz_local_offset == 3600 * 9, 'run test in JST'  # assume running test in JST locale machine

        d1 = datetime.datetime(1999, 1, 23, 14, 44, 53, 33451, tz_jst)
        ts1 = soxtimestamp.timestamp(d1)
        eq_(ts1, '1999-01-23T14:44:53.33451+09:00')

        d2 = datetime.datetime(2014, 4, 1, 12, 34, 56, 54243, tz_utc)
        ts2 = soxtimestamp.timestamp(d2)
        eq_(ts2, '2014-04-01T12:34:56.54243Z')

        d3 = datetime.datetime(1985, 5, 12, 0, 0, 0, 111, tz_pst)
        ts3 = soxtimestamp.timestamp(d3)
        eq_(ts3, '1985-05-12T00:00:00.111-08:00')

        d4 = datetime.datetime(2001, 12, 31, 1, 2, 3)
        ts4 = soxtimestamp.timestamp(d4)
        eq_(ts4, '2001-12-31T01:02:03+09:00')  # assuming system timezone is JST

        d5 = datetime.datetime(2002, 1, 2, 18, 22, 59, 1234)
        ts5 = soxtimestamp.timestamp(d5)
        eq_(ts5, '2002-01-02T18:22:59.1234+09:00')

    def test_is_sox_timestamp_format(self):
        valid_timestamps = [
            '2014-04-15T12:34:56.1Z',
            '2014-04-15T12:34:56.12Z',
            '2014-04-15T12:34:56.123Z',
            '2014-04-15T12:34:56.1234Z',
            '2014-04-15T12:34:56.1235Z',

            '2014-04-15T12:34:56.1+09:00',
            '2014-04-15T12:34:56.12+09:00',
            '2014-04-15T12:34:56.123+09:00',
            '2014-04-15T12:34:56.1234+09:00',
            '2014-04-15T12:34:56.12345+09:00',

            '2014-04-15T12:34:56.1-03:00',
            '2014-04-15T12:34:56.12-03:00',
            '2014-04-15T12:34:56.123-03:00',
            '2014-04-15T12:34:56.1234-03:00',
            '2014-04-15T12:34:56.12345-03:00',

            '2014-04-15T12:34:56Z',
            '2014-04-15T12:34:56+01:00',
            '2014-04-15T12:34:56+09:00',
            '2014-04-15T12:34:56+12:00',
            '2014-04-15T12:34:56+09:00',
            '2014-04-15T12:34:56-03:00',
            '2014-04-15T12:34:56-08:00',
            '2014-04-15T12:34:56-11:00'
        ]

        invalid_timestamps = [
            '',
            '20140416123456',
            '2014-04-15T12:34:56',
            '2014-04-15T12:34:56.123',
            '2014-04-15 12:34:56',
            '2014-04-15 12:34:56.123',
            '2014-04-15 12:34:56Z',
            '2014-04-15 12:34:56.123',
            '2014-04-15 12:34:56.123Z',
            '2014-04-15 12:34:56.123+09:00',
            '2014-04-15 12:34:56.123+0900',
            '2014-04-15 12:34:56.123-09:00',
            '2014-04-15 12:34:56.123-0900',
        ]

        invalid_timestamps = invalid_timestamps + \
                                ['%s ' % ts for ts in valid_timestamps] + \
                                [' %s' % ts for ts in valid_timestamps]

        for valid_ts in valid_timestamps:
            ok_(soxtimestamp.is_sox_timestamp_format(valid_ts))

        for invalid_ts in invalid_timestamps:
            ok_(not soxtimestamp.is_sox_timestamp_format(invalid_ts))
