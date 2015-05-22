#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import json
import pprint
import logging


import sleekxmpp
from bs4 import BeautifulSoup


class PubsubClient(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password, mitsui_nodes):
        super(PubsubClient, self).__init__(jid, password)
        self.__my_own_jid = jid
        self._mitsui_nodes = mitsui_nodes
        self.register_plugin('xep_0030')
        self.register_plugin('xep_0059')
        self.register_plugin('xep_0060')

        self._comp_count = 0

        self.add_event_handler('session_start', self.start, threaded=True)

    def start(self, event):
        print 'start'
        self.get_roster()
        print 'got roster'
        self.send_presence()
        print 'sent presence'

        def cb(*args, **kwargs):
            result = args[0]
            xml_str = '%s' % result

            soup = BeautifulSoup(xml_str)
            items = soup.find_all('item')
            nodes = []

            for item in items:
                nodes.append(item.attrs['node'])

            nodes.sort()
            # for item in nodes:
            #     print item

            nodes_to_add = [ node for node in self._mitsui_nodes if node not in nodes ]
            complete_n = len(nodes_to_add)

            def _cb_create_node(*args, **kwargs):
                self._comp_count += 1
                if self._comp_count == complete_n:
                    self.disconnect()

            for node in nodes_to_add:
                self['xep_0060'].create_node('pubsub.sox.ht.sfc.keio.ac.jp', node, callback=_cb_create_node)
                print 'requested %s' % node

            # self.disconnect()
        # print 'defined callback'

        self['xep_0060'].get_nodes('pubsub.sox.ht.sfc.keio.ac.jp', callback=cb)
        print 'requested'


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    if len(sys.argv) < 2:
        print 'USAGE: python ./create_mitsui_nodes.py MITSUI_FILE'
        sys.exit(-1)

    mitsui_file = sys.argv[1]
    mitsui_data = []
    for line in open(mitsui_file, 'rb'):
        mitsui_data.append(json.loads(line))

    mitsui_nodes = []
    for item in mitsui_data:
        node = item['node_name']
        mitsui_nodes.append('%s_meta' % node)
        mitsui_nodes.append('%s_data' % nodes)

    jid = 'guest@sox.ht.sfc.keio.ac.jp'
    pw = 'miroguest'

    xmpp = PubsubClient(jid, pw, mitsui_nodes)
    if xmpp.connect():
        print 'connected'
        xmpp.process(block=True)
    else:
        print 'could NOT connect'
