# -*- coding: utf-8 -*-
import pytest

import datetime
import dateutil.tz as tz
from unittest import TestCase
from nose.tools import ok_, eq_

from pysox.soxdata import SensorData, TransducerValue


def _node_attr(node):
    ret = {}
    for k, v in node.items():
        ret[k] = v
    return ret

class SensorDataTestCase(TestCase):

    def test_add_value(self):
        tv1 = TransducerValue(id='hoge', typed_value='123')

        sd = SensorData()
        assert sd.values == []

        sd.add_value(tv1)
        assert sd.values == [tv1]

        tv2 = TransducerValue(id='moga', typed_value='mogavalue')
        sd.add_value(tv2)
        assert sd.values == [tv1, tv2]

    def test_to_xml(self):
        sd1 = SensorData()
        xml1 = sd1.to_xml()
        assert xml1.tag == 'data'

        attr1 = _node_attr(xml1)
        ok_('xmlns' in attr1)
        assert attr1['xmlns'] == 'http://jabber.org/protocol/sox'

        children1 = xml1.getchildren()
        assert children1 == []

        tv1 = TransducerValue(id='hoge', typed_value='123')
        sd1.add_value(tv1)
        xml2 = sd1.to_xml()
        assert len(xml2.getchildren()) == 1

        tv2 = TransducerValue(id='moga', typed_value='mogavalue')
        sd1.add_value(tv2)
        xml3 = sd1.to_xml()
        assert len(xml3.getchildren()) == 2

    def test_to_string(self):
        sd1 = SensorData()
        assert sd1.to_string() == '<data xmlns="http://jabber.org/protocol/sox"/>\n'
        assert sd1.to_string(pretty=True) == '<data xmlns="http://jabber.org/protocol/sox"/>\n'
        assert sd1.to_string(pretty=False) == '<data xmlns="http://jabber.org/protocol/sox"/>'

        tz_jst = tz.tzoffset('JST', 3600 * 9)
        ts1 = datetime.datetime(2014, 4, 15, 12, 23, 34, 123, tz_jst)
        ts2 = datetime.datetime(2014, 4, 15, 12, 23, 41, 223, tz_jst)

        tv1 = TransducerValue(id='hoge', typed_value='123', timestamp=ts1)
        sd1.add_value(tv1)
        assert sd1.to_string() == '<data xmlns="http://jabber.org/protocol/sox">\n  <transducerValue id="hoge" typedValue="123" timestamp="2014-04-15T12:23:34.123+09:00" rawValue="123"/>\n</data>\n'
        # assert sd1.to_string(pretty=True) == '<data xmlns="http://jabber.org/protocol/sox">\n  <transducerValue id="hoge" timestamp="2014-04-15T12:23:34.123+09:00" typedValue="123"/>\n</data>\n'
        assert sd1.to_string(pretty=True) == '<data xmlns="http://jabber.org/protocol/sox">\n  <transducerValue id="hoge" typedValue="123" timestamp="2014-04-15T12:23:34.123+09:00" rawValue="123"/>\n</data>\n'
        assert sd1.to_string(pretty=False) == '<data xmlns="http://jabber.org/protocol/sox"><transducerValue id="hoge" typedValue="123" timestamp="2014-04-15T12:23:34.123+09:00" rawValue="123"/></data>'

        tv2 = TransducerValue(id='moga', typed_value='mogavalue', timestamp=ts2)
        sd1.add_value(tv2)
        assert sd1.to_string() == '<data xmlns="http://jabber.org/protocol/sox">\n  <transducerValue id="hoge" typedValue="123" timestamp="2014-04-15T12:23:34.123+09:00" rawValue="123"/>\n  <transducerValue id="moga" typedValue="mogavalue" timestamp="2014-04-15T12:23:41.223+09:00" rawValue="mogavalue"/>\n</data>\n'
        assert sd1.to_string(pretty=True) == '<data xmlns="http://jabber.org/protocol/sox">\n  <transducerValue id="hoge" typedValue="123" timestamp="2014-04-15T12:23:34.123+09:00" rawValue="123"/>\n  <transducerValue id="moga" typedValue="mogavalue" timestamp="2014-04-15T12:23:41.223+09:00" rawValue="mogavalue"/>\n</data>\n'
        # assert sd1.to_string(pretty=True) == '<data xmlns="http://jabber.org/protocol/sox">\n  <transducerValue id="hoge" timestamp="2014-04-15T12:23:34.123+09:00" typedValue="123"/>\n  <transducerValue id="moga" timestamp="2014-04-15T12:23:41.223+09:00" typedValue="mogavalue"/>\n</data>\n'
        assert sd1.to_string(pretty=False) == '<data xmlns="http://jabber.org/protocol/sox"><transducerValue id="hoge" typedValue="123" timestamp="2014-04-15T12:23:34.123+09:00" rawValue="123"/><transducerValue id="moga" typedValue="mogavalue" timestamp="2014-04-15T12:23:41.223+09:00" rawValue="mogavalue"/></data>'


class TransducerValueTestCase(TestCase):
    def test_init(self):
        tv1 = TransducerValue('idname1', 'value1')
        assert tv1.id == 'idname1'
        assert tv1.typed_value == 'value1'
        assert tv1.timestamp is not None
        assert tv1.timezone is not None

    def test_to_xml(self):
        tv1 = TransducerValue('idname1', 'value1')
        xml1 = tv1.to_xml()
        attr1 = _node_attr(xml1)

        assert len(xml1.getchildren()) == 0
        assert attr1['id'] == 'idname1'
        assert attr1['typedValue'] == 'value1'
        assert 'timestamp' in attr1
        assert 19 <= len(attr1['timestamp'])

    def test_to_string(self):
        tz_jst = tz.tzoffset('JST', 3600 * 9)
        ts1 = datetime.datetime(2014, 4, 15, 12, 23, 34, 123, tz_jst)
        ts2 = datetime.datetime(2014, 4, 15, 12, 23, 41, 223, tz_jst)

        tv1 = TransducerValue(id='hoge', typed_value='123', timestamp=ts1)
        assert tv1.to_string() == '<transducerValue id="hoge" typedValue="123" timestamp="2014-04-15T12:23:34.123+09:00" rawValue="123"/>\n'
        assert tv1.to_string(pretty=True) == '<transducerValue id="hoge" typedValue="123" timestamp="2014-04-15T12:23:34.123+09:00" rawValue="123"/>\n'
        assert tv1.to_string(pretty=False) == '<transducerValue id="hoge" typedValue="123" timestamp="2014-04-15T12:23:34.123+09:00" rawValue="123"/>'

        tv2 = TransducerValue(id='moga', typed_value='mogavalue', timestamp=ts2)
        assert tv2.to_string() == '<transducerValue id="moga" typedValue="mogavalue" timestamp="2014-04-15T12:23:41.223+09:00" rawValue="mogavalue"/>\n'
        assert tv2.to_string(pretty=True) == '<transducerValue id="moga" typedValue="mogavalue" timestamp="2014-04-15T12:23:41.223+09:00" rawValue="mogavalue"/>\n'
        assert tv2.to_string(pretty=False) == '<transducerValue id="moga" typedValue="mogavalue" timestamp="2014-04-15T12:23:41.223+09:00" rawValue="mogavalue"/>'
