#!/usr/bin/python
# -*- coding: utf-8 -*-
import gevent.monkey
gevent.monkey.patch_all()

import sys
import os
import os.path
import logging
import random
import signal
import json
import uuid

import gevent
import sleekxmpp
import grequests
import lxml.html
from sleekxmpp.xmlstream import ET
from sleekxmpp.exceptions import IqTimeout

from pysox.soxdata import SensorData, TransducerValue

BASE_CRAWL_INTERVAL = 300  # 300=5min
JITTER = 5
START_DELAY = 1

node2clients = dict()
node2stop_flag = dict()
client_threads = []


def scrape_mitsui_repark(url):
    logging.debug('fetching %s' % url)
    async_req = grequests.get(url)
    async_results = grequests.map([async_req])
    logging.debug('fetched %s' % url)
    response = async_results[0]
    if response.status_code != 200:
        raise ValueError('status_code was bad: %s' % response.status_code)

    html = response.content.decode('utf-8')
    return parse(html, origin=url)


def parse(html, origin='unknown'):
    logging.debug('parsing HTML start: %s' % origin)
    dom = lxml.html.fromstring(html)

    xpaths = [
        ('state', "//DIV[@id='contents-bg03']/DIV/DIV[1]/DIV[1]/DIV/SPAN/IMG/@alt"),
        ('address', "//DIV[@id='contents-bg03']/DIV/DIV[3]/DIV[2]/TABLE/TBODY/TR[1]/TD/SPAN"),
        ('time', "//DIV[@id='contents-bg03']/DIV/DIV[3]/DIV[2]/TABLE/TBODY/TR[2]/TD[1]/SPAN"),
        ('capacity', "//DIV[@id='contents-bg03']/DIV/DIV[3]/DIV[2]/TABLE/TBODY/TR[2]/TD[2]/SPAN"),
        ('limit', "//DIV[@id='contents-bg03']/DIV/DIV[3]/DIV[2]/TABLE/TBODY/TR[2]/TD[3]/SPAN")
    ]

    result = []

    for tdr_name, xpath in xpaths:
        xpath = xpath.lower()
        r = dom.body.xpath(xpath)

        if 0 < len(r):
            item = r[0]
            if not isinstance(item, (str, unicode)):
                item = item.text
            result.append((tdr_name, item))
        else:
            logging.debug(' missing \'%s\' value on parsing HTML of %s' % (tdr_name, origin))

    logging.debug('parsing HTML finished: %s' % origin)
    return result


class MitsuiReparkSendingClient(sleekxmpp.ClientXMPP):

    def __init__(self, jid, password, pubsub_name, mitsui_data):
        super(MitsuiReparkSendingClient, self).__init__(jid, password)

        self._pubsub_name = pubsub_name
        self._mitsui_data = mitsui_data

        self.running = False
        self.register_plugin('xep_0030')
        self.register_plugin('xep_0059')
        self.register_plugin('xep_0060')

        self.add_event_handler('session_start', self.start, threaded=False)

    def start(self, event):
        self.running = True

        mitsui = self._mitsui_data
        sox_node_name = mitsui['node_name']
        data_node_name = sox_node_name + '_data'

        self.get_roster()
        logging.debug('got roster: %s' % sox_node_name)
        self.send_presence()
        logging.debug('sent presence: %s' % sox_node_name)

        url = mitsui['simple_url']
        longitude = mitsui['longitude']
        latitude = mitsui['latitude']

        try:
            while self.running:
                # sleep
                sleep_time = (BASE_CRAWL_INTERVAL - JITTER) + random.random() * (JITTER * 2.0)
                logging.debug('sleeping %fsec... (node=%s)' % (sleep_time, sox_node_name))

                while 0 < sleep_time:
                    sleep_unit = 55.0 + 1.0 * random.randint(0, 10) 
                    next_sleep_sec = sleep_unit if sleep_unit < sleep_time else sleep_time
                    logging.debug('sleeping %fsec then send presence (node=%s)' % (next_sleep_sec, sox_node_name))
                    gevent.sleep(next_sleep_sec)
                    self.send_presence()
                    logging.debug('slept, sent presence (node=%s)' % sox_node_name)
                    sleep_time -= next_sleep_sec

                logging.debug('finished sleeping. (node=%s)' % sox_node_name)

                try:
                    web_page_data = scrape_mitsui_repark(url)  # fetch and parse HTML
                except:
                    logging.exception('web page scrape error: %s' % sox_node_name)
                else:
                    logging.debug('HTTP fetch and parse ok: %s' % sox_node_name)
                    # build sensor data
                    value_map = dict()
                    value_map['url'] = url
                    value_map['longitude'] = longitude
                    value_map['latitude'] = latitude
                    for tdr_id, item in web_page_data:
                        value_map[tdr_id] = item
                    sd = SensorData()
                    for tdr_id, value in value_map.iteritems():
                        tv = TransducerValue(id=tdr_id, typed_value=value, raw_value=value)
                        sd.add_value(tv)

                    xml_string = sd.to_string()
                    logging.debug('xml payload for node[%s]: %s' % (sox_node_name, xml_string))
                    xml_payload = ET.fromstring(xml_string)
                    logging.debug('packet build ok: %s' % sox_node_name)

                    if not self.running:  # just check before pub
                        break

                    try:
                        self['xep_0060'].publish(
                            self._pubsub_name,
                            data_node_name,
                            id=uuid.uuid1().hex,
                            payload=xml_payload
                        )
                    except IqTimeout:
                        logging.warn('IqTimeout! %s' % sox_node_name)
                    else:
                        logging.debug('published: %s' % sox_node_name)

            logging.debug('received stop singal, disconnecting... (node=%s)' % sox_node_name)

        finally:
            self.disconnect()
            logging.debug('disconnected: %s' % sox_node_name)

    def stop_mitsui(self):
        self.running = False


def mitsui_process(jid, pw, pubsub_name, mitsui_data):
    global node2clients, node2stop_flag
    node = mitsui_data['node_name']

    while not node2stop_flag[node]:
        client = MitsuiReparkSendingClient(jid, pw, pubsub_name, mitsui_data)
        node2clients[node] = client

        if client.connect():
            client.process(block=True)
        else:
            print 'could not connect ERROR: %s' % node


def my_signal_handler(signum, frame):
    global node2clients, node2stop_flag, client_threads
    for node, client in node2clients.iteritems():
        node2stop_flag[node] = True  # make thread loop break
        client.stop_mitsui()  # make client publish loop break
    gevent.joinall(client_threads)  # all thre
    sys.exit(0)


def main():
    global node2stop_flag

    # logger = logging.getLogger()
    # logger.setLevel(logging.DEBUG)

    if len(sys.argv) < 2:
        print 'USAGE: python transmit-mitsui.py MITSUI_FILE'
        sys.exit(-1)

    mitsui_file = sys.argv[1]
    if not os.path.exists(mitsui_file):
        print 'mitsui file not found: %s' % mitsui_file
        sys.exit(-1)

    # parse mitsui data
    mitsui_data = []
    with open(mitsui_file, 'rb') as fh:
        for line in fh:
            mitsui_data.append(json.loads(line))

    # register signal handler
    signal.signal(signal.SIGINT, my_signal_handler)

    threads = []

    jid = 'guest@sox.ht.sfc.keio.ac.jp'
    pw = 'miroguest'
    pubsub_name = 'pubsub.' + jid.split('@')[1]

    for item in mitsui_data:
        node2stop_flag[item['node_name']] = False
        thread = gevent.spawn(mitsui_process, jid, pw, pubsub_name, item)
        threads.append(thread)

        gevent.sleep(START_DELAY)

    logging.debug('started %d threads' % len(threads))
    gevent.joinall(threads)


if __name__ == '__main__':
    gevent.spawn(main).join()


