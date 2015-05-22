#!/usr/bin/python
# -*- coding: utf-8 -*-
import sleekxmpp
import pprint
import logging
import sys
import json



class PubsubClient(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password, nodes_to_remove):
        super(PubsubClient, self).__init__(jid, password)
        self.__my_own_jid = jid
        self.nodes_to_remove = nodes_to_remove
        self.register_plugin('xep_0030')
        self.register_plugin('xep_0059')
        self.register_plugin('xep_0060')

        self._complete = len(nodes_to_remove)
        self._count = 0

        self.add_event_handler('session_start', self.start, threaded=True)

        # self.add_event_handler('pubsub_publish', self._publish)

    def start(self, event):
        print 'start'
        self.get_roster()
        self.send_presence()
        # self._start_receiving()

        def _remove_callback(*args, **kwargs):
            # print '_remove_callback: args=%s, kwargs=%s' % (pprint.pformat(args), pprint.pformat(kwargs))
            print 'removed'
            self._count += 1
            if self._count == self._complete:
                self.disconnect()

        for node in self.nodes_to_remove:
            self['xep_0060'].delete_node(
                'pubsub.sox.ht.sfc.keio.ac.jp',
                node,
                callback=_remove_callback
            )
            print 'requested removal of %s' % node

    # def _start_receiving(self):
    #     print 'start receiving!'
    #     self._subscribe('pubsub.ps.ht.sfc.keio.ac.jp', 'sample_data')

    # def _subscribe(self, server, node):
    #     try:
    #         ifrom = self.__my_own_jid
    #         result = self['xep_0060'].subscribe(server, node, ifrom=ifrom, callback=self._subscribe_callback)
    #         print 'subscribe ok result=%s' % pprint.pformat(result)
    #     except:
    #         print 'subscribe ERROR'

    # def _subscribe_callback(self, *args, **kwargs):
    #     print 'got something'
    #     print 'args=%s, kwargs=%s' % (pprint.pformat(args), pprint.pformat(kwargs))

    # def _publish(self, msg):
    #     print 'got! %s' % msg


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'USAGE: python ./remove_mitsui_nodes.py MITSUI_FILE'
        sys.exit(-1)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # node_name = sys.argv[1]
    # print 'node name to remove: %s' % node_name

    mitsui_file = sys.argv[1]
    mitsui_data = []
    for line in open(mitsui_file, 'rb'):
        mitsui_data.append(json.loads(line))

    mitsui_nodes = []
    for item in mitsui_data:
        node = item['node_name']
        mitsui_nodes.append('%s_meta' % node)
        mitsui_nodes.append('%s_data' % node)

    # jid = 'guest@ps.ht.sfc.keio.ac.jp'
    jid = 'guest@sox.ht.sfc.keio.ac.jp'
    pw = 'miroguest'

    xmpp = PubsubClient(jid, pw, mitsui_nodes)
    if xmpp.connect():
        print 'connected'
        xmpp.process(block=True)
    else:
        print 'could NOT connect'





