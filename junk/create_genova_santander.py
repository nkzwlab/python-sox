#!/usr/bin/python
# -*- coding: utf-8 -*-
import sleekxmpp
# import pprint
import logging
import sys



class NodeCreationClient(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password, nodes):
        super(NodeCreationClient, self).__init__(jid, password)
        self.__my_own_jid = jid
        self.nodes = nodes
        self.register_plugin('xep_0030')
        self.register_plugin('xep_0059')
        self.register_plugin('xep_0060')

        self.add_event_handler('session_start', self.start, threaded=False)

    def start(self, event):
        print 'start'
        self.count = 0

        def _create_callback(*args, **kwargs):
            self.count += 1
            if self.count == len(self.nodes):
                self.disconnect()

        for node in self.nodes:
            for suffix in ('_meta', '_data'):
                real_node = node + suffix
                self['xep_0060'].create_node('pubsub.sox.ht.sfc.keio.ac.jp', real_node, callback=_create_callback)
                print 'create %s' % real_node

if __name__ == '__main__':
    # if len(sys.argv) < 2:
    #     print 'USAGE: python ./create_node.py NODE_NAME_LIST'
    #     print ''
    #     print 'NODE_NAME_LIST is like: aa,bb,cc'
    #     print 'will creates: aa_data, aa_meta, bb_data, bb_meta, cc_data, cc_meta'
    #     sys.exit(0)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # node_list_str = sys.argv[1]
    # if node_list_str == '':
    #     print 'node list is empty. aborting.'
    #     sys.exit(-1)

    # nodes = sys.argv[1].split(',')
    # nodes = [node for node in nodes if node != '']  # reject empty name

    nodes = []

    # genova5 .. genova32
    genova_id = 5
    while genova_id <= 32:
        nodes.append('genova%d' % genova_id)
        genova_id += 1

    # santander
    santander_ids = (173, 181, 193, 199)
    for santander_id in santander_ids:
        nodes.append('santander%d' % santander_id)

    print '---nodes(will expand _data and _meta):'
    for node in nodes:
        print node

    check = raw_input('ok?[y/n] ')
    if check.lower() != 'y':
        print 'aborting.'
        sys.exit(-1)

    # print 'debug, aborting'
    # sys.exit(0)

    # auth info
    jid = 'guest@sox.ht.sfc.keio.ac.jp'
    pw = 'miroguest'

    xmpp = NodeCreationClient(jid, pw, nodes)
    if xmpp.connect():
        print 'connected'
        xmpp.process(block=True)
    else:
        print 'could NOT connect'
