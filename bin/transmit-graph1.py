#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import uuid
import sleekxmpp
import pprint
import logging
import dateutil.tz
from sleekxmpp.xmlstream import ET
import datetime
import math
import gevent
import traceback

from pysox import soxtimestamp
from pysox.soxdata import SensorData, TransducerValue



class PubsubClient(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password, node_name):
        super(PubsubClient, self).__init__(jid, password)
        self.__my_own_jid = jid
        self.node_name = node_name
        self.register_plugin('xep_0030')
        self.register_plugin('xep_0059')
        self.register_plugin('xep_0060')

        self.add_event_handler('session_start', self.start, threaded=True)
        # self.add_event_handler('pubsub_publish', self._publish)

    def start(self, event):
        print 'start'
        self.get_roster()
        self.send_presence()
        # self._start_receiving()

        self.start_sending_data()

    def start_sending_data(self):

        # just for test: send 1 message
        while True:

            t = datetime.datetime.now(dateutil.tz.tzlocal())
            # scale = math.sin( math.pi * t.second / 60 ) * 100
            # value = t.second
            value = 20 + math.sin(math.pi * (t.second / 60.0 * 4.0)) * 5

            print 'starting sending data'
            try:
                ts = soxtimestamp.timestamp()
                print 'ts=%s' % ts
                # payload = ET.fromstring('<data><transducerValue id="trans1" typedValue="%f" timestamp="%s"/></data>' % (value, ts))

                sd = SensorData()
                tv1 = TransducerValue(id='trans1', typed_value='%s' % value, timestamp=ts)
                sd.add_value(tv1)
                payload = ET.fromstring(sd.to_string(pretty=False))

                print 'payload built'

                self['xep_0060'].publish(
                    'pubsub.ps.ht.sfc.keio.ac.jp',
                    self.node_name,
                    id=self.gen_item_id(),
                    payload=payload
                )
            except:
                print 'except!'
                traceback.print_exc()
                etype, value, etraceback = sys.exc_info()
                raise etype, value, etraceback
            print 'requested'

            gevent.sleep(1.2)

        self.disconnect()
        print 'disconnected'

    def gen_item_id(self):
        return uuid.uuid1().hex


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    jid = 'guest@ps.ht.sfc.keio.ac.jp'
    pw = 'miroguest'
    node_name = 'sb-graph1_data'

    xmpp = PubsubClient(jid, pw, node_name)
    if xmpp.connect():
        print 'connected'
        xmpp.process(block=True)
    else:
        print 'could NOT connect'
