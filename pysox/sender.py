"""
send sox data by using SleekXMPP
"""
import traceback
import uuid
import time
import logging

import sleekxmpp
from sleekxmpp.xmlstream import ET
from sleekxmpp.exceptions import IqTimeout



class SoxDataSenderXMPP(sleekxmpp.ClientXMPP):
    """
    usage sample:
    
    xmpp = SoxDataSenderXMPP(jid, pw, sox_host, sending_device, list_of_sox_data)
    if xmpp.connect():
        print 'connected'
        xmpp.process(block=True)
    else:
        print 'could NOT connect'
    """

    def __init__(self, sox_jid, sox_password, sox_server, sox_device, list_sensor_data):
        super(SoxDataSenderXMPP, self).__init__(sox_jid, sox_password)

        self.sox_server = sox_server
        self.sox_jid = sox_jid
        self.sox_password = sox_password
        self.sox_device = sox_device

        self.list_sensor_data = list_sensor_data  # iterable of SoxData objects

        self.completed = None
        self.requested = None

        self.logger = logging.getLogger(__name__)
        
        self.register_plugin('xep_0030')
        self.register_plugin('xep_0059')
        self.register_plugin('xep_0060')

        self.add_event_handler('session_start', self.start, threaded=False)
    
    def start(self, event):
        try:
            pubsub = 'pubsub.' + self.sox_server
            data_node = self.sox_device + '_data'
            self.requested = 0
            self.completed = 0
            self.all_requested = False

            def _callback(*args, **kwargs):
                try:
                    self.logger.debug("callback!! args=%s, kwargs=%s" % (args, kwargs))
                    self.completed += 1
                    self.logger.debug("callback: completed=%s" % self.completed)
                    if not self.all_requested:
                        self.logger.debug("callback: not all requested has done, r=%d, c=%d" % (
                            self.requested, self.completed
                        ))
                    else:
                        if self.requested <= self.completed:
                            self.logger.debug("callback: completed=%d, requested=%d, going to disconnect" % (
                                self.completed, self.requested
                            ))
                            self.disconnect()
                        else:
                            self.logger.debug("callback: completed=%d, requested=%d, not enough" % (
                                self.completed, self.requested
                            ))
                except:
                    traceback.print_exc()
                    raise
            
            for sd in self.list_sensor_data:
                xml_string = sd.to_string()
                payload = ET.fromstring(xml_string)
                try:
                    self['xep_0060'].publish(
                        pubsub,
                        data_node,
                        id=uuid.uuid1().hex,
                        payload=payload,
                        callback=_callback
                    )
                except IqTimeout as e:
                    self.logger.debug("got IqTimeout: %s" % (e,))
                    pass
                else:
                    self.requested += 1
                    self.logger.debug("requested: %s" % (self.requested,))
            self.all_requested = True

        except:
            traceback.print_exc()
            self.logger.debug("going to disconnect")
            self.disconnect()