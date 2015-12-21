#!/usr/bin/python
# -*- coding: utf-8 -*-
import signal
import uuid
import logging
import simplejson
import grequests
import re
import datetime
import dateutil.tz
import time

import sleekxmpp
from sleekxmpp.exceptions import IqTimeout
from sleekxmpp.xmlstream import ET

# from pysox import soxtimestamp
from pysox.soxdata import SensorData, TransducerValue

def get_santander_data(id):
    url = 'http://slem.smartsantander.eu/CLOUT/GetLastTempByNode/%d' % id
    async_req = grequests.get(url)
    results = grequests.map([async_req])  # wait for response
    result = results[0]
    data = simplejson.loads(result.text)[0]

    # apply_funcs = dict(nodeId=int, longitude=float, latitude=float, temperature=float)
    # for key, func in apply_funcs.iteritems():
    #     data[key] = func(data[key])

    data['nodeId'] = int(data['nodeId'])

    return data


def get_santander_timezone():
    # CET(Central European Timezone)
    return dateutil.tz.tzoffset('CET', 1 * 3600)  # FIXME: consider summer time


def santander2sensor(sdata):
    sd = SensorData()

    # set timestamp as 'date' field
    raw_date = sdata['date']
    # print 'raw_date=%s' % raw_date
    pat = re.compile(r'[\:\- ]')
    year, mon, day, hour, min, sec = map(lambda s: int(s), re.split(pat, raw_date))
    santander_timezone = get_santander_timezone()
    datetime_value = datetime.datetime(year, mon, day, hour, min, sec, 0)

    for key, value in sdata.iteritems():
        if key == 'date':
            continue
        tv = TransducerValue(
            id=key, typed_value='%s' % value, timestamp=datetime_value, timezone=santander_timezone)
        sd.add_value(tv)

    return sd


class SantanderProxy(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password, santander_ids):
        super(SantanderProxy, self).__init__(jid, password)
        self.santander_ids = santander_ids
        self.register_plugin('xep_0030')
        self.register_plugin('xep_0059')
        self.register_plugin('xep_0060')
        self.add_event_handler('session_start', self.start, threaded=False)

    def start(self, event):
        self.running = True
        try:
            # print 'starting!'
            err_count = 0
            err_threshold = 5
            while self.running and err_count < err_threshold:
                try:
                    for sid in self.santander_ids:
                        if not self.running:
                            break
                        node_name = 'santander%d_data' % sid

                        # print 'fetching for santander sensor id=%d' % sid
                        sdata = get_santander_data(sid)
                        # print 'fetched for santander sensor id=%d' % sid
                        sd = santander2sensor(sdata)
                        xml_string = sd.to_string()
                        payload = ET.fromstring(xml_string)

                        try:
                            self['xep_0060'].publish(
                                'pubsub.sox.ht.sfc.keio.ac.jp',
                                node_name,
                                id=self.gen_item_id(),
                                payload=payload
                            )
                        except IqTimeout:
                            # print 'caught IqTimeout, but ignoring'
                            err_count += 1
                            if err_threshold <= err_count:
                                break
                        # print 'published for node \'%s\'' % node_name

                    time.sleep(30)
                except:
                    logging.exception('something bad happened!')
                    err_count += 1
        finally:
            self.disconnect()

    def gen_item_id(self):
        return uuid.uuid1().hex


def main():
    logger = logging.getLogger()
    # logger.setLevel(logging.DEBUG)
    logger.setLevel(logging.INFO)
    jid = 'guest@sox.ht.sfc.keio.ac.jp'
    pw = 'miroguest'
    santander_ids = (173, 181, 193, 199)

    # for debug
    # for sid in santander_ids:
    #     sdata = get_santander_data(sid)
    #     sd = santander2sensor(sdata)
    #     print sd.to_string()
    #     print '\n\n\n'

    xmpp = SantanderProxy(jid, pw, santander_ids)

    def _signal_handler(signum, frame):
        print 'got signal! disconnecting'
        xmpp.running = False
        xmpp.disconnect()
    signal.signal(signal.SIGINT, _signal_handler)

    # print 'connecting...'
    if xmpp.connect():
        # print 'connected'
        xmpp.process(block=True)
        # print 'unexpected death!'
    else:
        # print 'could NOT connect'
        pass

if __name__ == '__main__':
    main()
