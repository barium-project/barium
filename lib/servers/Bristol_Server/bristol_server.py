"""
### BEGIN NODE INFO
[info]
name = BristolServer
version = 1.0
description =
instancename = BristolServer

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

from labrad.server import LabradServer, setting, Signal
from twisted.internet.defer import inlineCallbacks, returnValue, Deferred
from twisted.internet.task import LoopingCall
from twisted.internet import reactor
import telnetlib
import socket
import os
import time
from labrad.units import WithUnit as U
from twisted.internet.task import LoopingCall
from twisted.internet import reactor
FREQSIGNAL = 123133
AMPSIGNAL = 122333


class BristolServer(LabradServer):

    name = 'BristolServer'

    freq_changed = Signal(FREQSIGNAL, 'signal: frequency changed', 'v')
    amp_changed = Signal(AMPSIGNAL, 'signal: amplitude changed', 'v')
    
    def initServer(self):
        self.password = os.environ['LABRADPASSWORD']
        self.name = socket.gethostname() + 'Bristol Server'
        self.ip = '10.97.111.50'
        #self.ip = '10.97.111.231'
        self.port = 23
        self.timeout = 3 #s
        self.freq = 0
        self.connect()

    def connect(self):

        """
        Creates a connection to the Bristol 671A-MIR
        Bristol is a Telnet server
        """

        self.wm = telnetlib.Telnet(self.ip, self.port, self.timeout)
        time.sleep(2)
        print self.wm.read_very_eager() #clears connection message
        self.measure_chan()

    @setting(1, "get_frequency", returns = 'v')
    def get_frequency(self, c):
        """
        Gets the current frequency
        """

        yield self.wm.write(":READ:FREQ?\r\n")
        freq = yield self.wm.read_very_eager()
        if freq != '':
            freq = float(freq)
            self.freq_changed((freq))
            self.freq = freq
            self.freq_changed(freq)
            returnValue(self.freq)

        else:
            returnValue(self.freq)

    def get_amp(self, c):
        """
        Gets the current power
        """

        yield self.wm.write(":READ:POW?\r\n")
        amp = yield self.wm.read_very_eager()
        if amp != '':
            amp = float(freq)
            self.amp_changed((amp))
            self.amp = amp
            self.amp_changed(amp)
            returnValue(self.amp)

        else:
            returnValue(self.amp)
            
    def measure_chan(self):
        reactor.callLater(0.1, self.measure_chan)
        self.get_frequency(self)
        self.get_amp(self)

    def stopServer(self):
        self.wm.close()


if __name__ == "__main__":
    from labrad import util
    util.runServer(BristolServer())
