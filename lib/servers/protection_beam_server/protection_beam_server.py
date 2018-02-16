"""
### BEGIN NODE INFO
[info]
name = Oven_Server
version = 1.0
description =
instancename = OvenServer

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


class ProtectionBeamServer(LabradServer):

    name = 'ProtectionBeamServer'

    def initServer(self):
        self.password = os.environ['LABRADPASSWORD']
        self.name = socket.gethostname() + ' Protection Beam Server'
        self.threshold = 2 #kcounts/sec
        self.protection_state = False
        self.connect()

    @inlineCallbacks
    def connect(self):
        """Creates an Asynchronous connection to arduinottl and
        connects incoming signals to relavent functions

        """
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync(name='Protection_Beam_Server')
        self.arduino = self.cxn.arduinottl
        self.pmt = self.cxn.normalpmtflow


    @inlineCallbacks
    def protectionLoop(self):
        running = yield self.pmt.isrunning()
        if self.protection_state and running:
            counts = yield self.pmt.get_next_counts('ON',1)
            if counts < self.threshold:
                if self.inverted:
                    self.widget.TTLswitch.setChecked(True)

                else:
                    #self.arduino.ttl_output(self.port,True)
                    self.widget.TTLswitch.setChecked(False)
            '''
            else:
                if self.inverted:
                    self.widget.TTLswitch.setChecked(False)
                else:
                    self.widget.TTLswitch.setChecked(True)
                    print 'greater'
            '''
        self.reactor.callLater(.1, self.protectionLoop)

    @setting(16, value='v[A]')
    def oven_current(self, c, value):
        if value <= self.max_current:
            yield self.server.current(3, value)
        else:
            returnValue('Current above max allowed')

    @setting(17, output='b')
    def oven_output(self, c, output):
        yield self.server.output(3, output)

    @setting(18, returns='v[A]')
    def get_current(self, c):
        current = yield self.server.output(3)
        returnValue(current)

    @inlineCallbacks
    def stopServer(self):
        yield self.server.output(3, False)

if __name__ == "__main__":
    from labrad import util
    util.runServer(OvenServer())
