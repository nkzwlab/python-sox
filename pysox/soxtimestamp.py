#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import datetime
import dateutil.tz


_sox_ts_pat = re.compile(r'\A(\d{4})-(\d\d)-(\d\d)T(\d\d):(\d\d):(\d\d)((?:\.\d+)?)(Z|[+\-]\d\d:\d\d)\Z')


def _total_second(td):
    # python 2.6 does not support total_seconds() method for timedelta object!
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6 


def timestamp(datetime_value=None, tz=None):
    """
    build XEP-0082 timestamp string

    datetime_value => None means to use datetime.datetime.now()
    tz => None means to use datetime_value.tzinfo or dateutil.tz.tzlocal()
    """
    tz = tz or (datetime_value and datetime_value.tzinfo) or dateutil.tz.tzlocal()
    d = datetime_value or datetime.datetime.now(tz)

    tz_offset = _total_second(tz.utcoffset(d))

    if 0 < abs(tz_offset):
        if tz_offset < 0:
            tz_sign = '-'
        else:
            tz_sign = '+'

        tz_o_hour = abs(tz_offset) / 3600
        tz_o_min = abs(tz_offset) % 3600

        tz_str = '%s%02d:%02d' % (tz_sign, tz_o_hour, tz_o_min)
    else:
        tz_str = 'Z'

    return '%04d-%02d-%02dT%02d:%02d:%02d%s%s' % (
        d.year,
        d.month,
        d.day,
        d.hour,
        d.minute,
        d.second,
        '.%d' % d.microsecond if 0 < d.microsecond else '',
        tz_str
    )


def parse_sox_timestamp(soxtimestamp):
    global _sox_ts_pat

    m = _sox_ts_pat.match(soxtimestamp)
    if not m:
        return None

    parts = m.groups()
    y, mon, d, h, min, sec = [int(n) for n in parts[0:6]]
    microsec, tz= parts[6:9]
    microsec = 0 if microsec == '' else int(microsec[1:])
    tzinfo = _parse_timezone(tz)

    return datetime.datetime(y, mon, d, h, min, sec, microsec, tzinfo)


def _parse_timezone(tz):
    if tz == 'Z':
        tz_offset = 0
    else:
        sign = 1 if tz[0] == '+' else -1
        tz_td_hour = int(tz[1:3])
        tz_td_min = int(tz[4:6])
        tz_td_min_total = tz_td_hour * 60 + tz_td_min
        tz_offset = sign * tz_td_min_total * 60

    return dateutil.tz.tzoffset(None, tz_offset)


def is_sox_timestamp_format(ts):
    global _sox_ts_pat
    return _sox_ts_pat.match(ts)
