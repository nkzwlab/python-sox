#!/usr/bin/python
# -*- coding: utf-8 -*-
import sleekxmpp
import pprint
import logging
import sys



class PubsubClient(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password, node_name=None):
        super(PubsubClient, self).__init__(jid, password)
        self.__my_own_jid = jid
        self.node_name = node_name or 'sample_data'
        self.register_plugin('xep_0030')
        self.register_plugin('xep_0059')
        self.register_plugin('xep_0060')

        self.add_event_handler('session_start', self.start, threaded=True)

        self.add_event_handler('pubsub_publish', self._publish)

    def start(self, event):
        print 'start'
        self.get_roster()
        self.send_presence()
        self._start_receiving()

    def _start_receiving(self):
        print 'start receiving!'
        self._subscribe('pubsub.ps.ht.sfc.keio.ac.jp', self.node_name)

    def _subscribe(self, server, node):
        try:
            ifrom = self.__my_own_jid
            result = self['xep_0060'].subscribe(server, node, ifrom=ifrom, callback=self._subscribe_callback)
            print 'subscribe ok result=%s' % pprint.pformat(result)
        except:
            print 'subscribe ERROR'

    def _subscribe_callback(self, *args, **kwargs):
        print 'got something'
        print 'args=%s, kwargs=%s' % (pprint.pformat(args), pprint.pformat(kwargs))

    def _publish(self, msg):
        print 'got! %s' % msg


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    node = 'sample_data' if len(sys.argv) == 1 else sys.argv[1]
    print '@@@ node=%s' % node

    jid = 'guest@ps.ht.sfc.keio.ac.jp'
    pw = 'miroguest'

    xmpp = PubsubClient(jid, pw, node)
    if xmpp.connect():
        print 'connected'
        xmpp.process(block=True)
    else:
        print 'could NOT connect'





