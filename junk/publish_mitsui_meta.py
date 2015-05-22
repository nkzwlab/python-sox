#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import json
import uuid
import logging
import sleekxmpp
from pysox.soxdata import SensorMeta, MetaTransducer
from sleekxmpp.xmlstream import ET


# def gen_genova_meta_tags():
#     genova_meta_tags = []
#     gid = 5
#     while gid <= 32:
#         device = SensorMeta(
#             'genova%d' % gid,  # name
#             'genova%d' % gid,  # id
#             'outdoor weather', # type
#             None,              # timestamp
#             'genova sensor',   # description
#             'genova%d' % gid   # serialNumber
#         )

#         # latitude, float
#         t1 = MetaTransducer(name='latitude', id='latitude')
#         device.add_transducer(t1)

#         # longitude, float
#         t2 = MetaTransducer(name='longitude', id='longitude')
#         device.add_transducer(t2)

#         # name, string
#         t3 = MetaTransducer(name='name', id='name')
#         device.add_transducer(t3)

#         # id, int
#         t4 = MetaTransducer(name='id', id='id')
#         device.add_transducer(t4)

#         # height, int
#         t5 = MetaTransducer(name='height', id='height', units='meter')
#         device.add_transducer(t5)

#         # temperature, float, celsius
#         t6 = MetaTransducer(name='temperature', id='temperature', units='celsius')
#         device.add_transducer(t6)

#         # wind_chill, float, celsius
#         t7 = MetaTransducer(name='wind_chill', id='wind_chill', units='celsius')
#         device.add_transducer(t7)

#         # humidity, float
#         t8 = MetaTransducer(name='humidity', id='humidity', units='percent')
#         device.add_transducer(t8)

#         # wind_speed, float, kmh
#         t9 = MetaTransducer(name='wind_speed', id='wind_speed', units='km/h')
#         device.add_transducer(t9)

#         # wind_dir, string
#         t10 = MetaTransducer(name='wind_dir', id='wind_dir')
#         device.add_transducer(t10)

#         # wind_dir_deg, float, degree
#         t11 = MetaTransducer(name='wind_dir_deg', id='wind_dir_deg', units='degree')
#         device.add_transducer(t11)
        
#         # atomospheric_pressure, float, hpa
#         t12 = MetaTransducer(name='atomospheric_pressure', id='atomospheric_pressure', units='hpa')
#         device.add_transducer(t12)
        
#         # rain, float, mm/h
#         t13 = MetaTransducer(name='rain', id='rain', units='mm/h')
#         device.add_transducer(t13)
        
#         # dew_point, float, celsius
#         t14 = MetaTransducer(name='dew_point', id='dew_point', units='celsius')
#         device.add_transducer(t14)

#         # last_update, string(date), iso0861
#         t15 = MetaTransducer(name='last_update', id='last_update')
#         device.add_transducer(t15)

#         genova_meta_tags.append(device)

#         gid += 1
#     return genova_meta_tags


def build_mitsui_devices(mitsui_data):
    ret = []
    for item in mitsui_data:
        node = item['node_name']

        device = SensorMeta(
            node,  # name
            node,  # id
            'other', # type
            None,              # timestamp
            'mitsui repark %s' % node,   # description
            node   # serialNumber
        )

        meta_transducer_names = (
            'latitude', 'longitude', 'state', 'url', 'limit', 'address', 'capacity', 'time'
        )

        for tdr_name in meta_transducer_names:
            meta_tdr = MetaTransducer(name=tdr_name, id=tdr_name)
            device.add_transducer(meta_tdr)

        ret.append(device)

    return ret


class MyClient(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password, node2device_map):
        super(MyClient, self).__init__(jid, password)

        self.node2device_map = node2device_map
        self.register_plugin('xep_0030')
        self.register_plugin('xep_0059')
        self.register_plugin('xep_0060')

        self.add_event_handler('session_start', self.start, threaded=False)
        print '__init__ ok'

    def start(self, event):
        try:
            print 'start() starting'
            for node_name, device in self.node2device_map.iteritems():
                print 'going to publish for \'%s\'' % node_name
                xml_string = str(device)
                payload = ET.fromstring(xml_string)

                self['xep_0060'].publish(
                    'pubsub.sox.ht.sfc.keio.ac.jp',
                    node_name,
                    id=self.gen_item_id(),
                    payload=payload
                )

                print 'published: %s' % node_name

            print 'finished'
        except:
            logging.exception('something bad happened')
        finally:
            print 'disconnecting'
            self.disconnect()


    def gen_item_id(self):
        return uuid.uuid1().hex


if __name__ == '__main__':
    jid = 'guest@sox.ht.sfc.keio.ac.jp'
    pw = 'miroguest'

    mitsui_file = sys.argv[1]
    mitsui_data = []
    with open(mitsui_file, 'rb') as fh:
        # mitsui_data = json.loads(fh.read())
        for line in fh:
            mitsui_data.append(json.loads(line))

    mitsui_devices = build_mitsui_devices(mitsui_data)
    node2device_map = {}
    for device in mitsui_devices:
        node_name = '%s_meta' % device.name
        node2device_map[node_name] = device

    xmpp = MyClient(jid, pw, node2device_map)
    if xmpp.connect():
        print 'connected'
        xmpp.process(block=True)
    else:
        print 'ERROR: could not connect'
