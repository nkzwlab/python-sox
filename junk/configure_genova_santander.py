# -*- coding: utf-8 -*-
import sleekxmpp
import logging
from sleekxmpp.xmlstream import ET

class PubsubClient(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password, nodes):
        super(PubsubClient, self).__init__(jid, password)

        self._count = 0
        self._nodes = nodes

        self.register_plugin('xep_0030')
        self.register_plugin('xep_0059')
        self.register_plugin('xep_0060')

        self.add_event_handler('session_start', self.start, threaded=True)

    def start(self, event):
        print 'start'
        self.get_roster()
        self.send_presence()

        n_complete = len(self._nodes * 2)  # _meta + _data

        def cb(*args, **kwargs):
            self._count += 1
            print 'ack: %d/%d' % (self._count, n_complete)
            if self._count == n_complete:
                self.disconnect()
                print 'disconnected.'

        config_xml_data_str = """
<x xmlns='jabber:x:data' type='submit'>
<field var='pubsub#persist_items' type='boolean'><value>0</value></field>
</x>
        """

        config_xml_meta_str = """
<x xmlns='jabber:x:data' type='submit'>
<field var='pubsub#persist_items' type='boolean'><value>1</value></field>
</x>
        """

        config_xml_data = ET.fromstring(config_xml_data_str)
        config_xml_meta = ET.fromstring(config_xml_meta_str)

        pubsub_name = 'pubsub.sox.ht.sfc.keio.ac.jp'

        for node in self._nodes:
            meta_node_name = node + '_meta'
            data_node_name = node + '_data'

            # _data: persist item = false
            self['xep_0060'].set_node_config(
                pubsub_name,
                data_node_name,
                config_xml_data,
                callback=cb
            )

            # _meta: persist item = true
            self['xep_0060'].set_node_config(
                pubsub_name,
                meta_node_name,
                config_xml_meta,
                callback=cb
            )


def main():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # build genova nodes
    genova_nodes = []
    genova_id = 5
    while genova_id <= 32:
        genova_nodes.append('genova%d' % genova_id)
        genova_id += 1

    # build santander nodes
    santander_ids = (173, 181, 193, 199)
    santander_nodes = [ 'santander%d' % sid for sid in santander_ids ]

    # concat both nodes
    genova_santander_nodes = genova_nodes + santander_nodes

    jid = 'guest@sox.ht.sfc.keio.ac.jp'
    pw = 'miroguest'

    xmpp = PubsubClient(jid, pw, genova_santander_nodes)
    if xmpp.connect():
        print 'connected'
        xmpp.process(block=True)
    else:
        print 'could NOT connect'


if __name__ == '__main__':
    main()
