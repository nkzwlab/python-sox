# -*- coding: utf-8 -*-
from lxml import etree
import datetime
import tzlocal
import dateutil.parser
from . import soxtimestamp

from bs4 import BeautifulSoup
        
SENSOR_META_ATTRS = ('name', 'id', 'type', 'description', 'serialNumber')
        
META_TRANSDUCER_ATTRS = (
    'name', 'id', 'units', 'unitScalar', 'canActuate',
    'hasOwnNode', 'transducerTypeName', 'manufacturer',
    'partNumber', 'serialNumber', 'minValue', 'maxValue',
    'resolution', 'precision', 'accuracy'
)


def build_soxdata(typed_values, raw_values=None):
    assert isinstance(typed_values, dict)

    if raw_values is None:
        raw_values = typed_values
    else:
        assert isinstance(raw_values, dict)

    local_tz = tzlocal.get_localzone()
    timestamp = datetime.datetime.now(local_tz)
    
    sd = SensorData()

    t_keys = set(typed_values.keys())
    r_keys = set(raw_values.keys())
    both_keys = t_keys | r_keys

    for k in both_keys:
        typed_v = typed_values.get(k, raw_values.get(k))
        raw_v = raw_values.get(k, typed_values.get(k))

        tdr_v = TransducerValue(
            id=k,
            typed_value=typed_v,
            timestamp=timestamp,
            raw_value=raw_v
        )
        sd.add_value(tdr_v)

    return sd


class SensorData(object):

    @staticmethod
    def from_dict(item):
        sd = SensorData()
        dict_values = item['values']
        for dval in dict_values:
            transducer_val = TransducerValue.from_dict(dval)
            sd.add_value(transducer_val)
        return sd

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
        return etree.tostring(xml, pretty_print=pretty).decode()
    
    def to_dict(self):
        dict_values = [ v.to_dict() for v in self.values ]
        return dict(values=dict_values)


class TransducerValue(object):

    @staticmethod
    def from_dict(item):
        timestamp = dateutil.parser.parse(item['timestamp'])
        return TransducerValue(
            item['id'],
            item['typed_value'],
            timestamp,
            raw_value=item['raw_value']
        )

    def __init__(self, id, typed_value, timestamp=None, timezone=None, raw_value=None):
        # NOTE: accept timezone parameter for backward compatibility,
        #       but current implementation expect timezone is set within the timestamp
        assert isinstance(id, (str, ))
        assert isinstance(typed_value, (str, ))
        if timestamp and isinstance(timestamp, (str, )):
            assert soxtimestamp.is_sox_timestamp_format(timestamp), 'timestamp %s is not XEP-0082 format' % timestamp
        self.id = id
        self.typed_value = typed_value
        self.raw_value = raw_value
        local_tz = tzlocal.get_localzone()
        self.timestamp = timestamp or datetime.datetime.now(local_tz)
        if self.timestamp.tzinfo is None:
            self.timestamp = local_tz.localize(self.timestamp)

    def to_xml(self):
        ts = self.timestamp
        if type(ts) is datetime.datetime:
            ts = soxtimestamp.timestamp(ts)

        attributes = dict(
            id=self.id,
            typedValue=self.typed_value,
            timestamp=ts,
            rawValue=self.raw_value or self.typed_value
        )

        transducer_tag = etree.Element('transducerValue', **attributes)
        return transducer_tag

    def __repr__(self):
        xml = self.to_xml()
        return etree.tostring(xml)

    def __str__(self):
        return self.to_string()

    def to_string(self, pretty=True):
        xml = self.to_xml()
        return etree.tostring(xml, pretty_print=pretty).decode()
    
    def to_dict(self):
        return dict(
            id=self.id,
            typed_value=self.typed_value,
            timestamp=self.timestamp.isoformat(),
            raw_value=self.raw_value
        )


class SensorMeta(object):
    def __init__(self, name, id, type, timestamp, description, serialNumber):
        self.transducers = []

        self.name = name
        self.id = id
        self.type = type
        self.description = description
        self.serialNumber = serialNumber

        local_tz = tzlocal.get_localzone()
        self.timestamp = timestamp or datetime.datetime.now(tz)
        if self.timestamp.tzinfo is None:
            self.timestamp = local_tz.localize(self.timestamp)

    def add_transducer(self, tdr):
        self.transducers.append(tdr)

    def to_xml(self):
        ts = self.timestamp
        if type(ts) is datetime.datetime:
            ts = soxtimestamp.timestamp(ts)

        attributes = dict(timestamp=ts, xmlns='http://jabber.org/protocol/sox')
        for attrname in SENSOR_META_ATTRS:
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
        return etree.tostring(xml, pretty_print=pretty).decode()


class MetaTransducer(object):
    def __init__(self, *args, **kwargs):
        self.attributes = {}

        for attr in META_TRANSDUCER_ATTRS:
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

        for attr in META_TRANSDUCER_ATTRS:
            if attr in required:
                continue
            elif attr in self.attributes and self.attributes[attr] is not None:
                tmp_attrs[attr] = self.attributes[attr]

        transducer_tag = etree.Element('transducer', tmp_attrs)
        return transducer_tag

    def __repr__(self):
        xml = self.to_xml()
        return etree.tostring(xml)

    def __str__(self):
        return self.to_string()

    def to_string(self, pretty=True):
        xml = self.to_xml()
        return etree.tostring(xml, pretty_print=pretty).decode()

