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
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.task import LoopingCall
import os
import socket
from labrad.units import WithUnit as U
from config.shutter_client_config import shutter_config

class ProtectionBeamServer(LabradServer):

    name = 'ProtectionBeamServer'

    def initServer(self):
        self.password = os.environ['LABRADPASSWORD']
        self.name = socket.gethostname() + ' Protection Beam Server'
        self.threshold = 2 #kcounts/sec
        self.enable_protection = False
        self.protection_state = False
        self.shutter_config = shutter_config.info['Protection Beam']
        self.port = self.shutter_config[0]
        self.inverted = self.shutter_config[2]
        self.enable = self.shutter_config[3]
        self.enable_protection_shutter()
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
        self.protection_loop()


    def protection_loop(self):
        self.reactor.callLater(.1, self.protection_loop)
        running = yield self.pmt.isrunning()
        if self.enable_protection and running:
            counts = yield self.pmt.get_next_counts('ON',1)
            if counts < self.threshold:
                self.change_shutter_state(True)
                self.protection_state = True


    @setting(1, "change_shutter_state")
    def change_shutter_state(self, c, state = 'b'):
        if self.inverted:
            state = not state
        yield self.arduino.ttl_output(self.port, state)

    @setting(2, "enable_shutter")
    def enable_protection_shutter(self, c):
        """
        Allows current to run through the shutter
        """
        yield self.arduino.ttl_output(self.enable, True)

    @setting(3, "disable_protection")
    def disable_protection(self, c, attempts = 'w', returns = 'b'):
        """
        Closes the shutter and then looks to see if it stays closed. Will try specified number
        of times and return true if successful or false if it failed.
        """
        for i in range(attempts):
            self.protection_state = False
            self.change_shutter_state(False)
            time.sleep(.2)
            if self.protection_state == False:
                returnValue(True)
                break
        returnValue(False)




if __name__ == "__main__":
    from labrad import util
    util.runServer(ProtectionBeamServer())
