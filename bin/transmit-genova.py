#!/usr/bin/python
# -*- coding: utf-8 -*-
import gevent.monkey
gevent.monkey.patch_all()

import gevent


import re
import sys
import signal
import uuid
import sleekxmpp
import pprint
import logging
import dateutil.tz
import datetime
import math
import gevent
import traceback
import os.path
import base64
import random
import grequests
import simplejson

from sleekxmpp.xmlstream import ET
from sleekxmpp.exceptions import IqTimeout

from pysox import soxtimestamp
from pysox.soxdata import SensorData, TransducerValue


def get_genova_data(id):
    assert 5 <= id <= 32
    url = 'http://www.iononrischioclout.comune.genova.it/back_end/meteo_json.php?single=%d' % id
    async_req = grequests.get(url)
    results = grequests.map([async_req])  # wait for response
    result = results[0]
    return simplejson.loads(result.text)[0]


def genova2sensor(gdata):
    sd = SensorData()

    for key in gdata:
        value = gdata[key]
        tv = TransducerValue(id=key, typed_value=value)
        sd.add_value(tv)

    return sd


class GenovaDataSendingClient(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password, genova_id):
        super(GenovaDataSendingClient, self).__init__(jid, password)
        self.__my_own_jid = jid

        node_name = 'genova%d' % genova_id

        self.node_name = node_name
        self.genova_id = genova_id
        self.running = False
        self.register_plugin('xep_0030')
        self.register_plugin('xep_0059')
        self.register_plugin('xep_0060')

        self.add_event_handler('session_start', self.start, threaded=True)
        # self.add_event_handler('pubsub_publish', self._publish)

    def debug(self, msg):
        print '[%s] %s' % (self.node_name, msg)

    def start(self, event):
        self.debug('start')
        self.get_roster()
        self.debug('got roster')
        self.send_presence()
        self.debug('sent presence')
        # self._start_receiving()

        self.start_sending_data()

    def start_sending_data(self):
        self.running = True
        self.debug('start_sending_data() starting')

        while self.running:
            gevent.sleep(1.0 + 0.1 * random.randint(1, 30))
            try:
                genova_data = get_genova_data(self.genova_id)
                self.debug('got genova data: %s' % simplejson.dumps(genova_data))
                genova_sensor_data = genova2sensor(genova_data)
                xml_string = genova_sensor_data.to_string()
                payload = ET.fromstring(xml_string)
                self.debug('built payload: %s' % xml_string)

                try:
                    self['xep_0060'].publish(
                        'pubsub.sox.ht.sfc.keio.ac.jp',
                        self.node_name + '_data',
                        id=self.gen_item_id(),
                        payload=payload
                    )
                except IqTimeout:
                    self.debug('IGNORE IqTimeout')

                self.debug('published')

            except:
                self.debug('except!')
                traceback.print_exc()
                raise


        self.disconnect()
        self.debug('disconnected')

    def stop_genova_pub(self):
        self.running = False

    def gen_item_id(self):
        return uuid.uuid1().hex


def main():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    threads = []
    clients = []

    def _signal_handler(signum, frame):
        print ''
        print ''
        print '@@@@@@@@@@@@@ got signal!! @@@@@@@@@@@@@@@'
        print ''
        print ''
        for i, thread in enumerate(threads):
            clients[i].stop_genova_pub()
            # thread.join()
        sys.exit(0)
    signal.signal(signal.SIGINT, _signal_handler)

    # jid = 'guest@ps.ht.sfc.keio.ac.jp'
    jid = 'guest@sox.ht.sfc.keio.ac.jp'
    pw = 'miroguest'


    id_list = [5, 10, 15, 20, 25, 30]
    # i = 5
    # while i <= 32:
    # while i <= 5:
    for i in id_list:
        def _thread(client):
            if client.connect():
                client.process(block=True)

        client = GenovaDataSendingClient(jid, pw, i)
        clients.append(client)

        gthread = gevent.spawn(_thread, client)
        threads.append(gthread)
        print 'thread for genova-%d started' % i
        i += 1

    while True:
        gevent.sleep(1.0)

    # node_name = 'sb-graph1_data'

    # xmpp = PubsubClient(jid, pw, node_name)
    # if xmpp.connect():
    #     print 'connected'
    #     xmpp.process(block=True)
    # else:
    #     print 'could NOT connect'

if __name__ == '__main__':
    main_thread = gevent.spawn(main)
    main_thread.join()

