#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import sys
import uuid
import sleekxmpp
import pprint
import logging
import dateutil.tz
import datetime
import math
# import gevent
import time
import traceback
import os.path
import base64
import random
import simplejson

from sleekxmpp.xmlstream import ET
from sleekxmpp.exceptions import IqTimeout

from pysox import soxtimestamp
from pysox.soxdata import SensorData, TransducerValue


class DummySensorDataGenerator(object):
    def generate(self):
        raise NotImplementedError('generate() should be implemented in subclass')

    @property
    def name(self):
        raise NotImplementedError('name property should be implemented in subclass')


class DummyGraphDataGenerator(object):
    def __init__(self):
        self.name = 'sb-graph1_data'
    def generate(self):
        t = datetime.datetime.now(dateutil.tz.tzlocal())
        # scale = math.sin( math.pi * t.second / 60 ) * 100
        # value = t.second
        value = 20 + math.sin(math.pi * (t.second / 60.0 * 4.0)) * 5
        value = '%s' % value

        sd = SensorData()
        tv = TransducerValue(id='graph', typed_value=value)
        sd.add_value(tv)
        return sd


class DummySimpleDataGenerator(object):
    def __init__(self):
        self.name = 'sb-data1_data'
        self.value_range = [1, 100]

    def generate(self):
        v_min, v_max = self.value_range
        random_value = '%s' % random.randint(v_min, v_max)

        sd = SensorData()
        tv = TransducerValue(id='simple', typed_value=random_value)
        sd.add_value(tv)
        return sd

class DummyTagCloudDataGenerator(object):
    def __init__(self):
        self.name = 'sb-tagcloud1_data'
        self.words = [
            u'江ノ島', u'テラスモール', # u'Keio University',
            u'湘南台', u'江の電', u'藤沢', u'辻堂', u'湘南ライフタウン',
            u'いすゞ', u'国道467号線', u'国道1号線',
            u'日大', u'文教', u'慶應', u'慶應SFC', u'鵠沼海岸', u'片瀬江ノ島', u'生しらす',
            u'湘南台高校', u'湘南高校'
        ]
        # self.words = [
        #     'Enoshima', 'Terrace Mall', 
        #     'Shonandai', 'Enoden', 'Fujisawa', 'Tsujidou', 'Shonan Life-Town',
        #     'Isuzu', 'Route 467', 'Route 1', 'Nippon Univ.', 'Bunkyo Univ.', 'Keio Univ.',
        #     'Keio SFC', 'Kugenuma Beach', 'Katase Enoshima Station',
        #     'Shonadai High', 'Shonan High'
        # ]

        self.value_range = [1, 100]

    def generate(self):
        sample_n = 5
        assert sample_n <= len(self.words)

        # sampled_words = []
        # while len(sampled_words) < sample_n:
        #     pick = random.choice(self.words)
        #     if pick in sampled_words:
        #         continue
        #     sampled_words.append(pick)
        # print 'sampled words: %s' % ', '.joini(sampled_words)

        sampled_words = random.sample(self.words, sample_n)
        tagcloud = dict()
        v_min, v_max = self.value_range
        for w in sampled_words:
            tagcloud[w] = '%s' % random.randint(v_min, v_max)
        json_serialized_tc = simplejson.dumps(tagcloud)

        sd = SensorData()
        tv = TransducerValue(id='tagcloud', typed_value=json_serialized_tc)
        sd.add_value(tv)
        return sd


class DummyImageDataGenerator(object):
    def __init__(self):
        self.name = 'sb-image1_data'
        self.dummy_img_dir = './dummy-images'
        self.file_list_cache = {}
        self.init_b64_images()

    def init_b64_images(self):
        images = []
        img_file_pat = re.compile(r'\.(jpg|jpeg|gif|png)\Z', re.IGNORECASE)

        here = os.path.dirname(__file__)
        real_dir_path = os.path.normpath(os.path.join(here, self.dummy_img_dir))

        if real_dir_path not in self.file_list_cache:
            file_list = os.listdir(real_dir_path)
            self.file_list_cache[real_dir_path] = file_list

        # for f in os.listdir(real_dir_path):
        for f in self.file_list_cache[real_dir_path]:
            if not img_file_pat.search(f):
                print 'not image: skipping %s' % f
                continue

            real_f_path = os.path.join(real_dir_path, f)
            data_uri_img = self._build_data_uri(real_f_path)
            images.append(data_uri_img)

        self.images = images

    def _build_data_uri(self, path):
        mime = self._get_mime(path)
        b64_content = self._get_b64_content(path)
        return 'data:%s;base64,%s' % (mime, b64_content)

    def _get_b64_content(self, path):
        with open(path, 'rb') as fh:
            content = fh.read()
        return base64.b64encode(content)

    def _get_mime(self, path):
        rest, ext = os.path.splitext(path.lower())

        if ext == '.png':
            return 'image/png'
        elif ext == '.gif':
            return 'image/gif'
        elif ext in ('.jpg', 'jpeg'):
            return 'image/jpeg'
        else:
            raise StandardError('failed to determine mime type: unknown ext: %s' % path)

    def generate(self):
        random_img = random.choice(self.images)
        tv = TransducerValue(id='image', typed_value=random_img)
        sd = SensorData()
        sd.add_value(tv)
        return sd


class PubsubClient(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password):
        super(PubsubClient, self).__init__(jid, password)
        self.__my_own_jid = jid
        # self.node_name = node_name
        self.register_plugin('xep_0030')
        self.register_plugin('xep_0059')
        self.register_plugin('xep_0060')

        self.add_event_handler('session_start', self.start, threaded=True)
        # self.add_event_handler('pubsub_publish', self._publish)

    def start(self, event):
        print 'start'
        # self.get_roster()
        # print 'got roster'
        # self.send_presence()
        # print 'sent presence'
        # self._start_receiving()

        self.start_sending_data()

    def start_sending_data(self):
        # prepare dummy data generators 
        print 'start_sending_data() starting'
        try:
            dummy_data_generators = [
                DummyGraphDataGenerator(),
                DummySimpleDataGenerator(),
                DummyTagCloudDataGenerator(),
                DummyImageDataGenerator()
            ]
        except:
            print 'except!(1)'
            traceback.print_exc()
            etype, value, etraceback = sys.exc_info()
            raise etype, value, etraceback
        print 'prepared generators'

        fire_timing = {
            'sb-graph1_data': 110,
            'sb-image1_data': 70,
            'sb-tagcloud1_data': 50,
            'sb-data1_data': 30
        }
        counter = {
            'sb-graph1_data': 0,
            'sb-image1_data': 0,
            'sb-tagcloud1_data': 0,
            'sb-data1_data': 0
        }

        err_count = 0
        err_threshold = 5

        # just for test: send 1 message
        while err_count < err_threshold:
            # print 'starting sending data'
            try:
                for dd_generator in dummy_data_generators:
                    node_name = dd_generator.name

                    counter[node_name] += 1
                    if counter[node_name] == fire_timing[node_name]:
                        dummy_data = dd_generator.generate()
                        dummy_payload_xml_string = dummy_data.to_string(pretty=False)
                        payload = ET.fromstring(dummy_payload_xml_string)
                        # print 'payload built'

                        print '[generator:%s] sending: %s' % (node_name, dummy_payload_xml_string)
                        try:
                            self['xep_0060'].publish(
                                'pubsub.sox.ht.sfc.keio.ac.jp',
                                node_name,
                                id=self.gen_item_id(),
                                payload=payload
                            )
                        except IqTimeout:
                            print '[geenrator:%s] IGNORE IqTimeout!' % node_name
                            err_count += 1
                            if err_threshold <= err_count:
                                break
                        print '[generator:%s] sent: %s' % (node_name, dummy_payload_xml_string)

                        counter[node_name] = 0
            except:
                print 'except!'
                traceback.print_exc()
                etype, value, etraceback = sys.exc_info()
                raise etype, value, etraceback
                err_count += 1
            # print 'requested'

            # gevent.sleep(1.2)
            # gevent.sleep(0.1)
            time.sleep(0.1)

        self.disconnect()
        print 'disconnected'

    def gen_item_id(self):
        return uuid.uuid1().hex


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    jid = 'guest@sox.ht.sfc.keio.ac.jp'
    pw = 'miroguest'

    while True:
        xmpp = PubsubClient(jid, pw)
        if xmpp.connect():
            print 'connected'
            xmpp.process(block=True)  # will stop if error counter reach threshold
        else:
            print 'could NOT connect'
