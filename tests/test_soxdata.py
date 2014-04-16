#!/usr/bin/python
# -*- coding: utf-8 -*-
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
        eq_(sd.values, [])

        sd.add_value(tv1)
        eq_(sd.values, [tv1])

        tv2 = TransducerValue(id='moga', typed_value='mogavalue')
        sd.add_value(tv2)
        eq_(sd.values, [tv1, tv2])

    def test_to_xml(self):
        sd1 = SensorData()
        xml1 = sd1.to_xml()
        eq_(xml1.tag, 'data')

        attr1 = _node_attr(xml1)
        ok_('xmlns' in attr1)
        eq_(attr1['xmlns'], 'http://jabber.org/protocol/sox')

        children1 = xml1.getchildren()
        eq_(children1, [])

        tv1 = TransducerValue(id='hoge', typed_value='123')
        sd1.add_value(tv1)
        xml2 = sd1.to_xml()
        eq_(len(xml2.getchildren()), 1)

        tv2 = TransducerValue(id='moga', typed_value='mogavalue')
        sd1.add_value(tv2)
        xml3 = sd1.to_xml()
        eq_(len(xml3.getchildren()), 2)

    def test_to_string(self):
        sd1 = SensorData()
        eq_(sd1.to_string(), '<data xmlns="http://jabber.org/protocol/sox"/>\n')
        eq_(sd1.to_string(pretty=True), '<data xmlns="http://jabber.org/protocol/sox"/>\n')
        eq_(sd1.to_string(pretty=False), '<data xmlns="http://jabber.org/protocol/sox"/>')

        tz_jst = tz.tzoffset('JST', 3600 * 9)
        ts1 = datetime.datetime(2014, 4, 15, 12, 23, 34, 123, tz_jst)
        ts2 = datetime.datetime(2014, 4, 15, 12, 23, 41, 223, tz_jst)

        tv1 = TransducerValue(id='hoge', typed_value='123', timestamp=ts1)
        sd1.add_value(tv1)
        eq_(sd1.to_string(), '<data xmlns="http://jabber.org/protocol/sox">\n  <transducerValue id="hoge" timestamp="2014-04-15T12:23:34.123+09:00" typedValue="123"/>\n</data>\n')
        eq_(sd1.to_string(pretty=True), '<data xmlns="http://jabber.org/protocol/sox">\n  <transducerValue id="hoge" timestamp="2014-04-15T12:23:34.123+09:00" typedValue="123"/>\n</data>\n')
        eq_(sd1.to_string(pretty=False), '<data xmlns="http://jabber.org/protocol/sox"><transducerValue id="hoge" timestamp="2014-04-15T12:23:34.123+09:00" typedValue="123"/></data>')

        tv2 = TransducerValue(id='moga', typed_value='mogavalue', timestamp=ts2)
        sd1.add_value(tv2)
        eq_(sd1.to_string(), '<data xmlns="http://jabber.org/protocol/sox">\n  <transducerValue id="hoge" timestamp="2014-04-15T12:23:34.123+09:00" typedValue="123"/>\n  <transducerValue id="moga" timestamp="2014-04-15T12:23:41.223+09:00" typedValue="mogavalue"/>\n</data>\n')
        eq_(sd1.to_string(pretty=True), '<data xmlns="http://jabber.org/protocol/sox">\n  <transducerValue id="hoge" timestamp="2014-04-15T12:23:34.123+09:00" typedValue="123"/>\n  <transducerValue id="moga" timestamp="2014-04-15T12:23:41.223+09:00" typedValue="mogavalue"/>\n</data>\n')
        eq_(sd1.to_string(pretty=False), '<data xmlns="http://jabber.org/protocol/sox"><transducerValue id="hoge" timestamp="2014-04-15T12:23:34.123+09:00" typedValue="123"/><transducerValue id="moga" timestamp="2014-04-15T12:23:41.223+09:00" typedValue="mogavalue"/></data>')


class TransducerValueTestCase(TestCase):
    def test_init(self):
        tv1 = TransducerValue('idname1', 'value1')
        eq_(tv1.id, 'idname1')
        eq_(tv1.typed_value, 'value1')
        ok_(tv1.timestamp is not None)
        ok_(tv1.timezone is not None)

    def test_to_xml(self):
        tv1 = TransducerValue('idname1', 'value1')
        xml1 = tv1.to_xml()
        attr1 = _node_attr(xml1)

        eq_(len(xml1.getchildren()), 0)
        eq_(attr1['id'], 'idname1')
        eq_(attr1['typedValue'], 'value1')
        ok_('timestamp' in attr1)
        ok_(19 <= len(attr1['timestamp']))

    def test_to_string(self):
        tz_jst = tz.tzoffset('JST', 3600 * 9)
        ts1 = datetime.datetime(2014, 4, 15, 12, 23, 34, 123, tz_jst)
        ts2 = datetime.datetime(2014, 4, 15, 12, 23, 41, 223, tz_jst)

        tv1 = TransducerValue(id='hoge', typed_value='123', timestamp=ts1)
        eq_(tv1.to_string(), '<transducerValue id="hoge" timestamp="2014-04-15T12:23:34.123+09:00" typedValue="123"/>\n')
        eq_(tv1.to_string(pretty=True), '<transducerValue id="hoge" timestamp="2014-04-15T12:23:34.123+09:00" typedValue="123"/>\n')
        eq_(tv1.to_string(pretty=False), '<transducerValue id="hoge" timestamp="2014-04-15T12:23:34.123+09:00" typedValue="123"/>')

        tv2 = TransducerValue(id='moga', typed_value='mogavalue', timestamp=ts2)
        eq_(tv2.to_string(), '<transducerValue id="moga" timestamp="2014-04-15T12:23:41.223+09:00" typedValue="mogavalue"/>\n')
        eq_(tv2.to_string(pretty=True), '<transducerValue id="moga" timestamp="2014-04-15T12:23:41.223+09:00" typedValue="mogavalue"/>\n')
        eq_(tv2.to_string(pretty=False), '<transducerValue id="moga" timestamp="2014-04-15T12:23:41.223+09:00" typedValue="mogavalue"/>')
