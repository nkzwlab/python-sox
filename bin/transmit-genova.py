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

        self.add_event_handler('session_start', self.start, threaded=False)
        # self.add_event_handler('pubsub_publish', self._publish)

    def debug(self, msg):
        print '[%s] %s' % (self.node_name, msg)

    def start(self, event):
        self.debug('start')
        # self.get_roster()
        # self.debug('got roster')
        # self.send_presence()
        # self.debug('sent presence')
        # self._start_receiving()

        self.start_sending_data()

    def start_sending_data(self):
        self.running = True
        self.debug('start_sending_data() starting')

        err_count = 0
        err_threshold = 5

        try:
            while self.running and err_count < err_threshold:
                try:
                    # gevent.sleep(5.0 + 0.1 * random.randint(1, 30))
                    gevent.sleep(29.5 + random.random())
                    genova_data = get_genova_data(self.genova_id)
                    self.debug('got genova data: %s' % simplejson.dumps(genova_data))
                    # self.debug('got genova data')
                    genova_sensor_data = genova2sensor(genova_data)
                    xml_string = genova_sensor_data.to_string()
                    payload = ET.fromstring(xml_string)
                    self.debug('built payload: %s' % xml_string)
                    # self.debug('built payload')

                    try:
                        self['xep_0060'].publish(
                            'pubsub.sox.ht.sfc.keio.ac.jp',
                            self.node_name + '_data',
                            id=self.gen_item_id(),
                            payload=payload
                        )
                    except IqTimeout:
                        self.debug('caught IqTimeout')
                        err_count += 1

                    self.debug('published')

                except:
                    self.debug('except!')
                    traceback.print_exc()
                    err_count += 1
        finally:
            self.disconnect()
            self.debug('disconnected')

    def stop_genova_pub(self):
        self.running = False

    def gen_item_id(self):
        return uuid.uuid1().hex


def main():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    threads = set([])
    clients = set([])

    def _signal_handler(signum, frame):
        print ''
        print ''
        print '@@@@@@@@@@@@@ got signal!! @@@@@@@@@@@@@@@'
        print ''
        print ''
        # for i, thread in enumerate(threads):
        #     clients[i].stop_genova_pub()
            # thread.join()
        for client in clients:
            client.stop_genova_pub()
        sys.exit(0)
    signal.signal(signal.SIGINT, _signal_handler)

    # config
    jid = 'guest@sox.ht.sfc.keio.ac.jp'
    pw = 'miroguest'


    id_list = [5, 10, 15, 20, 25, 30]
    def _process_thread(client):
        if client.connect():
            client.process(block=True)

    for i in id_list:
        client = GenovaDataSendingClient(jid, pw, i)
        clients.add(client)

        gthread = gevent.spawn(_process_thread, client)
        gthread.client = client
        gthread.genova_id = i  # remember genova-id
        threads.add(gthread)
        print 'thread for genova-%d started' % i

    try:
        # finish means err occured too much
        finished_threads = gevent.wait(threads, count=1)
        finished_thread = finished_threads[0]
        finished_client = finished_thread.client
        clients.remove(finished_client)  # remove from active list
        genova_id = finished_thread.genova_id
        print '@@@ id %d died! respawning again' % genova_id
        threads.remove(finished_thread)  # remove from active list

        # connect and process again for the genova ID
        new_client = GenovaDataSendingClient(jid, pw, genova_id)
        clients.add(new_client)
        new_thread = gevent.spawn(_process_thread, new_client)
        new_thread.client = new_client
        new_thread.genova_id = genova_id
        threads.add(new_thread)
    except:
        logging.exception('something bad happened')
        raise


if __name__ == '__main__':
    main_thread = gevent.spawn(main)
    main_thread.join()

