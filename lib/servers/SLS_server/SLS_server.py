# Copyright (C) 2016 Justin Christensen
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
### BEGIN NODE INFO
[info]
name = slsServer
version = 1.0
description =
instancename = slsServer

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""

from common.lib.servers.serialdeviceserver import SerialDeviceServer, setting, inlineCallbacks, SerialDeviceError, SerialConnectionError, PortRegError
from labrad.types import Error
from twisted.internet import reactor
from labrad.server import Signal
from labrad import types as T
from twisted.internet.task import LoopingCall
from twisted.internet.defer import returnValue
from labrad.support import getNodeName
import time
from labrad.units import WithUnit as U

SERVERNAME = 'slsServer'
TIMEOUT = 1.0
BAUDRATE = 115200

class slsServer( SerialDeviceServer ):
    name = 'slsServer'
    regKey = 'slsServer'
    port = None
    serNode = getNodeName()
    timeout = T.Value(TIMEOUT,'s')

    @inlineCallbacks
    def initServer( self ):
        if not self.regKey or not self.serNode: raise SerialDeviceError( 'Must define regKey and serNode attributes' )
        port = yield self.getPortFromReg( self.regKey )
        self.port = port
        self.max_frequency = U(725.0, 'MHz')
        self.min_frequency = U(20.0, 'MHz')
        try:
            serStr = yield self.findSerial( self.serNode )
            self.initSerial( serStr, port, baudrate = BAUDRATE )
        except SerialConnectionError, e:
            self.ser = None
            if e.code == 0:
                print 'Could not find serial server for node: %s' % self.serNode
                print 'Please start correct serial server'
            elif e.code == 1:
                print 'Error opening serial connection'
                print 'Check set up and restart serial server'
            else: raise

 


    @setting(3,'set_frequency',frequency = ['v[kHz]'])
    def set_frequency(self, c, frequency):
        '''Set the offset frequency of the SLS'''
        if frequency > self.max_frequency or frequency < self.min_frequency:
            returnValue('Frequency Range 20 MHz to 725 MHz')

        yield self.ser.write('set OffsetFrequency ' + str(frequency['Hz']) + \
         '\n\r')
        time.sleep(.2)
        freq = yield self.ser.read() 
        #freq= freq.split('\n')
        #freq= freq[1][16:].split('E')
        #freq= float(freq[0])*10**(float(freq[1][1:3]))
        #returnValue(freq)



# Define all get functions

    @setting(200,'get_frequency')
    def get_frequency(self, c):
        '''Set the offset frequency of the SLS'''
        yield self.ser.write('get OffsetFrequency\n\r')
        time.sleep(.2)
        freq = yield self.ser.read() 
        freq= freq.split('\n')
        freq= freq[1][16:].split('E')
        freq= float(freq[0])*10**(float(freq[1][1:3]))
        returnValue(freq)


if __name__ == "__main__":
    from labrad import util
    util.runServer( slsServer() )
