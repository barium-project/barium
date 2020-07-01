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
        self.amp = 0
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
        yield self.wm.write(":READ:POW?\r\n")
        yield self.wm.write(":READ:FREQ?\r\n")
        freq = yield self.wm.read_very_eager()
        if freq != '':

            temp = freq.split()
            temp = map(float,temp)
            temp.sort()
            if temp[len(temp)-1] >40.0:
               freq = temp[len(temp)-1]
               self.freq_changed((freq))
               self.freq = freq
            if temp[0] < 40.0:
               amp = temp[0]
               self.amp_changed((amp))
               self.amp = amp
        returnValue(self.freq)
 
    def measure_chan(self):
        reactor.callLater(0.1, self.measure_chan)
        self.get_frequency(self)

    def stopServer(self):
        self.wm.close()


if __name__ == "__main__":
    from labrad import util
    util.runServer(BristolServer())
