"""
### BEGIN NODE INFO
[info]
name = ProtectionBeamServer
version = 1.0
description =
instancename = ProtectionBeamServer

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

from labrad.server import LabradServer, setting
from twisted.internet.defer import inlineCallbacks, returnValue, Deferred
from twisted.internet.task import LoopingCall
from twisted.internet import reactor
import os
import socket
import time
from labrad.units import WithUnit as U
from config.shutter_client_config import shutter_config

SIGNALID = 874193


class ProtectionBeamServer(LabradServer):

    name = 'ProtectionBeamServer'

    def initServer(self):
        self.password = os.environ['LABRADPASSWORD']
        self.name = socket.gethostname() + ' Protection Beam Server'
        self.threshold = 2 #kcounts/sec
        self.enable_protection = False
        self.protection_state = False
        self.enable_shutter = True
        self.shutter_config = shutter_config.info['Protection Beam']
        self.port = self.shutter_config[0]
        self.inverted = self.shutter_config[2]
        self.enable = self.shutter_config[3]
        self.connect()

    @inlineCallbacks
    def connect(self):
        """
        Creates an Asynchronous connection labrad
        """
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync(name='Protection_Beam_Server')
        self.arduino = self.cxn.arduinottl
        self.pmt = self.cxn.normalpmtflow
        self.enable_protection_shutter(self, self.enable_shutter)
        self.setupListeners()

    @inlineCallbacks
    def setupListeners(self):
        yield self.pmt.signal__new_count(SIGNALID)
        yield self.pmt.addListener(listener=self.protection,
                                      source=None, ID=SIGNALID)


    def protection(self, signal, value):
        if value < self.threshold and self.enable_protection:
            self.change_shutter_state(self, True)
            self.protection_state = True



    @setting(1, "change_shutter_state", state = 'b')
    def change_shutter_state(self, c, state):
        """
        Open or close the protection beam shutter.
        """
        if self.inverted:
            state = not state
        yield self.arduino.ttl_output(self.port, state)

    @setting(2, "enable_protection_shutter", state = 'b')
    def enable_protection_shutter(self, c, state):
        """
        Allows current to run through the shutter
        """
        yield self.arduino.ttl_output(self.enable, state)

    @setting(3, "set_protection_enabled", state ='b')
    def set_protection_enabled(self, c, state):
        """
        Turn the monitoring of counts on/off. Opens protection beam when true
        and counts are below the threshold value
        """
        self.enable_protection = state

    @setting(4, "set_threshold",  value = 'v')
    def set_threshold(self, c, value):
        self.threshold = value

    @setting(5, "protection_off")
    def protection_off(self, c):
        """
        Close shutter to block protection beam
        """
        self.protection_state = False
        self.change_shutter_state(self, False)

    # Define get functions
    @setting(100, "get_protection_state",  returns='b')
    def get_protection_state(self, c):
        """
        Returns true if protection beam open, false if closed
        """
        return self.protection_state

    @setting(101, "get_threshold",  returns='v')
    def get_threshold(self, c):
        return self.threshold

    @setting(102, "get_protection_enabled",  returns='b')
    def get_protection_enabled(self, c):
        return self.enable_protection

    @setting(103, "get_shutter_enabled",  returns='b')
    def get_shutter_enabled(self, c):
        return self.enable_shutter

if __name__ == "__main__":
    from labrad import util
    util.runServer(ProtectionBeamServer())
