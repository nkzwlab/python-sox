#!/usr/bin/python
# -*- coding: utf-8 -*-
import uuid
import logging
import sleekxmpp
from pysox.soxdata import SensorMeta, MetaTransducer
from sleekxmpp.xmlstream import ET


def gen_santander_meta_tags():
    santander_meta_tags = []

    santander_ids = (173, 181, 193, 199)

    for sid in santander_ids:
        common_name = 'santander%d' % sid
        desc = 'santander sensor #%d' % sid

        device = SensorMeta(
            common_name,        # name
            common_name,        # id
            'outdoor weather',  # type
            None,               # timestamp
            desc,               # description
            common_name         # serialNumber
        )

        # date, time
        t1 = MetaTransducer(name='date', id='date', units='second')
        device.add_transducer(t1)

        # longitude, float
        t2 = MetaTransducer(name='longitude', id='longitude')
        device.add_transducer(t2)

        # latitude, float
        t3 = MetaTransducer(name='latitude', id='latitude')
        device.add_transducer(t3)

        # nodeId, int
        t4 = MetaTransducer(name='nodeId', id='nodeId')
        device.add_transducer(t4)

        # temperature, float, celsius
        t5 = MetaTransducer(name='temperature', id='temperature', units='celcius')
        device.add_transducer(t5)

        santander_meta_tags.append(device)

    return santander_meta_tags


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


def main():
    jid = 'guest@sox.ht.sfc.keio.ac.jp'
    pw = 'miroguest'
    santander_meta_tags = gen_santander_meta_tags()
    node2device_map = {}
    for device in santander_meta_tags:
        # print device.to_string()
        # print '\n\n\n'
        node_name = '%s_meta' % device.name
        node2device_map[node_name] = device

    xmpp = MyClient(jid, pw, node2device_map)
    if xmpp.connect():
        print 'connected'
        xmpp.process(block=True)
    else:
        print 'ERROR: could not connect'


if __name__ == '__main__':
    main()
