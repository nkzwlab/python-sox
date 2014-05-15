#!/usr/bin/python
# -*- coding: utf-8 -*-
import sleekxmpp
import pprint
import logging


class PubsubClient(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password):
        super(PubsubClient, self).__init__(jid, password)
        self.__my_own_jid = jid
        self.register_plugin('xep_0030')
        self.register_plugin('xep_0059')
        self.register_plugin('xep_0060')

        self.add_event_handler('session_start', self.start, threaded=True)

    def start(self, event):
        self.get_roster()
        self.send_presence()



        # def cb(*args, **kwargs):
        #     result = args[0]
        #     print 'result type = %s'  % type(result)

        #     print '_get_nodes_callback: args=%s, kwargs=%s' % (pprint.pformat(args), pprint.pformat(kwargs))
        #     self.disconnect()
        # print 'defined callback'

        # self['xep_0060'].get_nodes('pubsub.sox.ht.sfc.keio.ac.jp', callback=cb)
        # print 'requested'

        def cb(*args, **kwargs):
            print 'callback: args=%s, kwargs=%s' % (pprint.pformat(args), pprint.pformat(kwargs))
            self.disconnect()

        # self['xep_0060'].get_item_ids('pubsub.sox.ht.sfc.keio.ac.jp', 'genova5_meta', callback=cb)
        self['xep_0060'].get_items('pubsub.sox.ht.sfc.keio.ac.jp', 'sb-data1_data', callback=cb)



if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    jid = 'guest@sox.ht.sfc.keio.ac.jp'
    pw = 'miroguest'

    xmpp = PubsubClient(jid, pw)
    if xmpp.connect():
        print 'connected'
        xmpp.process(block=True)
    else:
        print 'could NOT connect'
