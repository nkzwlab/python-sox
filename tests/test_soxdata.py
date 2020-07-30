# -*- coding: utf-8 -*-
import pytest

import datetime
import dateutil.tz as tz
from unittest import TestCase
from nose.tools import ok_, eq_

from pysox.soxdata import (
    SensorData,
    TransducerValue,
    SensorMeta,
    MetaTransducer
)


def _node_attr(node):
    ret = {}
    for k, v in node.items():
        ret[k] = v
    return ret


class SensorDataTestCase(TestCase):

    def test_from_dict(self):
        in1 = {'values': []}
        r1 = SensorData.from_dict(in1)
        assert isinstance(r1, SensorData)
        assert len(r1.values) == 0

        tz_jst = tz.tzoffset('JST', 3600 * 9)
        ts1 = datetime.datetime(2020, 1, 2, 11, 22, 33, tzinfo=tz_jst)
        in2 = {'values': [{'id': 'hoge', 'typed_value': '123', 'raw_value': None, 'timestamp': ts1.isoformat()}]}
        r2 = SensorData.from_dict(in2)
        assert isinstance(r2, SensorData)
        assert len(r2.values) == 1
        assert r2.values[0].id == "hoge"
        assert r2.values[0].typed_value == "123"
        assert r2.values[0].raw_value is None
        assert r2.values[0].timestamp == ts1
        
        ts2 = datetime.datetime(2020, 2, 3, 11, 22, 33, tzinfo=tz_jst)
        tv2 = TransducerValue(id='moge', typed_value='123', raw_value='raw123', timestamp=ts2)
        in3 = {
            'values': [
                {'id': 'hoge', 'typed_value': '123', 'raw_value': None, 'timestamp': ts1.isoformat()},
                {'id': 'moge', 'typed_value': '123', 'raw_value': 'raw123', 'timestamp': ts2.isoformat()}
            ]
        }
        r3 = SensorData.from_dict(in3)
        assert isinstance(r3, SensorData)
        assert len(r3.values) == 2
        assert r3.values[0].id == "hoge"
        assert r3.values[0].typed_value == "123"
        assert r3.values[0].raw_value is None
        assert r3.values[0].timestamp == ts1
        assert r3.values[1].id == "moge"
        assert r3.values[1].typed_value == "123"
        assert r3.values[1].raw_value == "raw123"
        assert r3.values[1].timestamp == ts2
    
    def test_to_dict(self):
        sd = SensorData()
        assert sd.to_dict() == {'values': []}

        tz_jst = tz.tzoffset('JST', 3600 * 9)
        ts1 = datetime.datetime(2020, 1, 2, 11, 22, 33, tzinfo=tz_jst)
        tv1 = TransducerValue(id='hoge', typed_value='123', timestamp=ts1)
        sd.add_value(tv1)
        assert sd.to_dict() == {'values': [{'id': 'hoge', 'typed_value': '123', 'raw_value': None, 'timestamp': ts1.isoformat()}]}


        ts2 = datetime.datetime(2020, 2, 3, 11, 22, 33, tzinfo=tz_jst)
        tv2 = TransducerValue(id='moge', typed_value='123', raw_value='raw123', timestamp=ts2)
        sd.add_value(tv2)
        assert sd.to_dict() == {
            'values': [
                {'id': 'hoge', 'typed_value': '123', 'raw_value': None, 'timestamp': ts1.isoformat()},
                {'id': 'moge', 'typed_value': '123', 'raw_value': 'raw123', 'timestamp': ts2.isoformat()}
            ]
        }

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
        assert sd1.to_string(pretty=True) == '<data xmlns="http://jabber.org/protocol/sox">\n  <transducerValue id="hoge" typedValue="123" timestamp="2014-04-15T12:23:34.123+09:00" rawValue="123"/>\n</data>\n'
        assert sd1.to_string(pretty=False) == '<data xmlns="http://jabber.org/protocol/sox"><transducerValue id="hoge" typedValue="123" timestamp="2014-04-15T12:23:34.123+09:00" rawValue="123"/></data>'

        tv2 = TransducerValue(id='moga', typed_value='mogavalue', timestamp=ts2)
        sd1.add_value(tv2)
        assert sd1.to_string() == '<data xmlns="http://jabber.org/protocol/sox">\n  <transducerValue id="hoge" typedValue="123" timestamp="2014-04-15T12:23:34.123+09:00" rawValue="123"/>\n  <transducerValue id="moga" typedValue="mogavalue" timestamp="2014-04-15T12:23:41.223+09:00" rawValue="mogavalue"/>\n</data>\n'
        assert sd1.to_string(pretty=True) == '<data xmlns="http://jabber.org/protocol/sox">\n  <transducerValue id="hoge" typedValue="123" timestamp="2014-04-15T12:23:34.123+09:00" rawValue="123"/>\n  <transducerValue id="moga" typedValue="mogavalue" timestamp="2014-04-15T12:23:41.223+09:00" rawValue="mogavalue"/>\n</data>\n'
        assert sd1.to_string(pretty=False) == '<data xmlns="http://jabber.org/protocol/sox"><transducerValue id="hoge" typedValue="123" timestamp="2014-04-15T12:23:34.123+09:00" rawValue="123"/><transducerValue id="moga" typedValue="mogavalue" timestamp="2014-04-15T12:23:41.223+09:00" rawValue="mogavalue"/></data>'


class TransducerValueTestCase(TestCase):
    def test_to_dict(self):
        tz_jst = tz.tzoffset('JST', 3600 * 9)
        ts1 = datetime.datetime(2020, 1, 2, 11, 22, 33, tzinfo=tz_jst)
        tv1 = TransducerValue(id='hoge', typed_value='123', timestamp=ts1)
        assert tv1.to_dict() == {'id': 'hoge', 'typed_value': '123', 'raw_value': None, 'timestamp': ts1.isoformat()}

        ts2 = datetime.datetime(2020, 2, 3, 11, 22, 33, tzinfo=tz_jst)
        tv2 = TransducerValue(id='moge', typed_value='123', raw_value='raw123', timestamp=ts2)
        assert tv2.to_dict() == {'id': 'moge', 'typed_value': '123', 'raw_value': 'raw123', 'timestamp': ts2.isoformat()}
    
    def test_from_dict(self):
        tz_jst = tz.tzoffset('JST', 3600 * 9)
        ts1 = datetime.datetime(2020, 1, 2, 11, 22, 33, tzinfo=tz_jst)
        in1 = {'id': 'hoge', 'typed_value': '123', 'raw_value': None, 'timestamp': ts1.isoformat()}
        tv1 = TransducerValue.from_dict(in1)
        assert isinstance(tv1, TransducerValue)
        assert tv1.id == "hoge"
        assert tv1.typed_value == "123"
        assert tv1.raw_value is None
        assert tv1.timestamp == ts1
        
        ts2 = datetime.datetime(2020, 2, 3, 11, 22, 33, tzinfo=tz_jst)
        tv2 = TransducerValue.from_dict({'id': 'moge', 'typed_value': '123', 'raw_value': 'raw123', 'timestamp': ts2.isoformat()})
        assert isinstance(tv2, TransducerValue)
        assert tv2.id == "moge"
        assert tv2.typed_value == "123"
        assert tv2.raw_value == "raw123"
        assert tv2.timestamp == ts2

    def test_init(self):
        tv1 = TransducerValue('idname1', 'value1')
        assert tv1.id == 'idname1'
        assert tv1.typed_value == 'value1'
        assert tv1.timestamp is not None

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


class SensorMetaTestCase(TestCase):
    def test_to_string(self):
        mt1 = MetaTransducer(
            id='hoge',
            name='hoge',
            units='celcius',
            minValue='-10',
            maxValue='50'
        )

        ts = datetime.datetime(2020, 5, 1, 12, 34, 56)
        sm1 = SensorMeta(
            'moge',
            'mogeid',
            'mogetype',
            ts,
            'mogedesc',
            's1234'
        )
        sm1.add_transducer(mt1)

        assert sm1.to_string() == '<device timestamp="2020-05-01T12:34:56+09:00" xmlns="http://jabber.org/protocol/sox" name="moge" id="mogeid" type="mogetype" description="mogedesc" serialNumber="s1234">\n  <transducer name="hoge" id="hoge" units="celcius" minValue="-10" maxValue="50"/>\n</device>\n'


class MetaTransducerTestCase(TestCase):
    def test_accessor(self):
        mt1 = MetaTransducer(
            id='hoge',
            name='hoge',
            units='celcius',
            minValue='-10',
            maxValue='50'
        )

        assert mt1['id'] == 'hoge'
        assert mt1['name'] == 'hoge'
        assert mt1['units'] == 'celcius'
        assert mt1['minValue'] == '-10'
        assert mt1['maxValue'] == '50'
    
    def test_to_xml(self):
        mt1 = MetaTransducer(
            name='hoge',
            id='hoge',
            units='celcius',
            minValue='-10',
            maxValue='50'
        )

        xml1 = mt1.to_xml()

        attr1 = _node_attr(xml1)

        assert len(xml1.getchildren()) == 0
        assert attr1['id'] == 'hoge'
        assert attr1['name'] == 'hoge'
        assert attr1['units'] == 'celcius'
        assert attr1['minValue'] == '-10'
        assert attr1['maxValue'] == '50'
    
    def test_to_string(self):
        mt1 = MetaTransducer(
            name='hoge',
            id='hoge',
            units='celcius',
            minValue='-10',
            maxValue='50'
        )

        assert mt1.to_string() == '<transducer name="hoge" id="hoge" units="celcius" minValue="-10" maxValue="50"/>\n'
        assert mt1.to_string(pretty=True) == '<transducer name="hoge" id="hoge" units="celcius" minValue="-10" maxValue="50"/>\n'
        assert mt1.to_string(pretty=False) == '<transducer name="hoge" id="hoge" units="celcius" minValue="-10" maxValue="50"/>'

