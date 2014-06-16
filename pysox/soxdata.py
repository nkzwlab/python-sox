#!/usr/bin/python
# -*- coding: utf-8 -*-
from lxml import etree
import datetime
import dateutil.tz
import soxtimestamp

from bs4 import BeautifulSoup


class SensorData(object):
    @staticmethod
    def parse(packet_str):
        # TODO: not debugged
        soup = BeautifulSoup(packet_str, 'xml')

        data = soup.find('data')
        if not data:
            raise StandardError('data tag not found')

        sd = SensorData()

        for tv_tag in data.find_all('transducerValue'):
            attrs = tv_tag.attrs
            tv = TransducerValue(id=attrs['id'], typed_value=attrs['typedValue'], timestamp=attrs['timestamp'])
            sd.add_value(tv)

        return sd

    def __init__(self):
        self.values = []

    def add_value(self, value):
        self.values.append(value)

    def to_xml(self):
        data_tag = etree.Element('data', xmlns='http://jabber.org/protocol/sox')
        for value in self.values:
            data_tag.append(value.to_xml())
        return data_tag

    def __repr__(self):
        xml = self.to_xml()
        return etree.tostring(xml)

    def __str__(self):
        return self.to_string()

    def to_string(self, pretty=True):
        xml = self.to_xml()
        return etree.tostring(xml, pretty_print=pretty)


class TransducerValue(object):
    def __init__(self, id, typed_value, timestamp=None, timezone=None):
        assert isinstance(id, (str, unicode))
        assert isinstance(typed_value, (str, unicode))
        if timestamp and isinstance(timestamp, (str, unicode)):
            assert soxtimestamp.is_sox_timestamp_format(timestamp), 'timestamp %s is not XEP-0082 format' % timestamp
        self.id = id
        self.typed_value = typed_value
        if timestamp and type(timestamp) is datetime.datetime:
            tz = timezone or timestamp.tzinfo or dateutil.tz.tzlocal()
        else:
            tz = timezone or dateutil.tz.tzlocal()
        self.timestamp = timestamp or datetime.datetime.now(tz)
        self.timezone = tz

    def to_xml(self):
        ts = self.timestamp
        if type(ts) is datetime.datetime:
            ts = soxtimestamp.timestamp(ts, tz=self.timezone)

        attributes = dict(id=self.id, typedValue=self.typed_value, timestamp=ts)
        transducer_tag = etree.Element('transducerValue', **attributes)
        return transducer_tag

    def __repr__(self):
        xml = self.to_xml()
        return etree.tostring(xml)

    def __str__(self):
        return self.to_string()

    def to_string(self, pretty=True):
        xml = self.to_xml()
        return etree.tostring(xml, pretty_print=pretty)


class SensorMeta(object):
    def __init__(self, name, id, type, timestamp, description, serialNumber, timezone=None):
        self.transducers = []

        self.name = name
        self.id = id
        self.type = type
        self.description = description
        self.serialNumber = serialNumber

        if timestamp and type(timestamp) is datetime.datetime:
            tz = timezone or timestamp.tzinfo or dateutil.tz.tzlocal()
        else:
            tz = timezone or dateutil.tz.tzlocal()
        self.timestamp = timestamp or datetime.datetime.now(tz)
        self.timezone = timezone

    def add_transducer(self, tdr):
        self.transducers.append(tdr)

    def to_xml(self):
        ts = self.timestamp
        if type(ts) is datetime.datetime:
            ts = soxtimestamp.timestamp(ts, tz=self.timezone)

        attributes = dict(timestamp=ts, xmlns='http://jabber.org/protocol/sox')
        for attrname in ('name', 'id', 'type', 'description', 'serialNumber'):
            attributes[attrname] = getattr(self, attrname)

        device_tag = etree.Element('device', attributes)
        for tdr in self.transducers:
            device_tag.append(tdr.to_xml())

        return device_tag

    def __repr__(self):
        xml = self.to_xml()
        return etree.tostring(xml)

    def __str__(self):
        return self.to_string()

    def to_string(self, pretty=True):
        xml = self.to_xml()
        return etree.tostring(xml, pretty_print=pretty)


class MetaTransducer(object):
    def __init__(self, *args, **kwargs):
        self.attributes = {}
        self.attr_names = (
            'name', 'id', 'units', 'unitScalar', 'canActuate',
            'hasOwnNode', 'transducerTypeName', 'manufacturer',
            'partNumber', 'serialNumber', 'minValue', 'maxValue',
            'resolution', 'precision', 'accuracy'
        )

        for attr in self.attr_names:
            self[attr] = kwargs[attr] if attr in kwargs else None

    def __getitem__(self, attrname):
        return self.attributes[attrname]

    def __setitem__(self, attrname, value):
        self.attributes[attrname] = value

    def to_xml(self):
        tmp_attrs = dict()
        required = ('name', 'id')
        for r_attr in required:
            assert r_attr in self.attributes, 'attribute is required: %s' % r_attr
            assert self.attributes[r_attr] is not None, 'attribute is required: %s' % r_attr
            tmp_attrs[r_attr]  = self.attributes[r_attr]

        for attr in self.attr_names:
            if attr in required:
                continue
            elif attr in self.attributes and self.attributes[attr] is not None:
                tmp_attrs[attr] = self.attributes[attr]

        # transducer_tag = etree.Element('transducer', self.attributes)
        transducer_tag = etree.Element('transducer', tmp_attrs)
        return transducer_tag

    def __repr__(self):
        xml = self.to_xml()
        return etree.tostring(xml)

    def __str__(self):
        return self.to_string()

    def to_string(self, pretty=True):
        xml = self.to_xml()
        return etree.tostring(xml, pretty_print=pretty)

