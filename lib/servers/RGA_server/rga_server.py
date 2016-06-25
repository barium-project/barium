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
name = RGA Server
version = 1.0.0
description = RGA Server
instancename = %LABRADNODE% RGA Server

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""

'''
Created May 22, 2016
@author: Calvin He
'''

from common.lib.servers.serialdeviceserver import SerialDeviceServer, setting, inlineCallbacks, SerialDeviceError, SerialConnectionError, PortRegError
from labrad.types import Error
from twisted.internet import reactor
from labrad.server import Signal
from labrad import types as T
from twisted.internet.task import LoopingCall
from twisted.internet.defer import returnValue
from labrad.support import getNodeName
import time

SERVERNAME = 'RGA Server'
TIMEOUT = 1.0
BAUDRATE = 28800

class RGA_Server( SerialDeviceServer ):
    name = SERVERNAME
    regKey = 'SRSRGA'
    port = None
    serNode = getNodeName()
    timeout = T.Value(TIMEOUT,'s')

    @inlineCallbacks
    def initServer( self ):
        if not self.regKey or not self.serNode: raise SerialDeviceError( 'Must define regKey and serNode attributes' )
        port = yield self.getPortFromReg( self.regKey )
        self.port = port
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

    @setting(1, returns='s')
    def identify(self, c):
        '''
        Returns the RGA's IDN. RGACOM command: 'id?'
        '''
        yield self.ser.write_line('id?')
        idn = yield self.ser.read_line()
        returnValue(idn)

    @setting(2, value='w',returns='s')
    def filament(self, c, value=None):
        '''
        Sets the filament on/off mode, or read its value.
        ".filament(0)" shuts off the filament.  RGACOM command: "fl0"
        ".filament(1)" turns on the filament.  RGACOM command: "fl1"
        ".filament()" returns the filament mode.  RGACOM command: "fl?"
        '''
        if value > 1:
            message = 'Input out of range. Acceptable inputs: 0 and 1.'
        elif value==1:
            yield self.ser.write_line('fl1')
            message = 'Filament on command sent.'
        elif value==0:
            yield self.ser.write_line('fl0')
            message = 'Filament off command sent.'
        elif value==None:
            yield self.ser.write_line('fl?')
            message = yield self.ser.read_line()
        returnValue(message)

    @setting(3, value='w', returns='s')
    def mass_lock(self, c, value):
        '''
        Sets the mass lock for the RGA.  Acceptable range: [1,200].  RGACOM command:  "mlx"
        ".mass_lock(x)" sets the mass filter to x (positive integer representing amu).
        '''
        if value<1 or value>200:
            message = 'Mass out of range.  Acceptable range: [1,200]'
        else:
            yield self.ser.write_line('ml'+str(value))
            message = 'Mass lock for '+str(value)+' amu command sent.'
        returnValue(message)

    @setting(4, value='w', returns='s')
    def high_voltage(self, c, value=None):
        '''
        Sets the electron multiplier voltage.  Acceptable range: [0,2500]
        ".high_voltage()" queries the electron multiplier voltage.  RGACOM command: "hv?"
        ".high_voltage(x)" sets the electron multiplier voltage to x (positive integer representing volts).  RGA COM command: "hvx"
        '''
        if value==None:
            yield self.ser.write_line('hv?')
            message = yield self.ser.read_line()
        elif value > 2500:
            message = 'Voltage out of range.  Acceptable range: [0,2500]'
        else:
            yield self.ser.write_line('hv'+str(value))
            message = 'High voltage (electron multiplier) command sent.'
        returnValue(message)

__server__ = RGA_Server()

if __name__ == "__main__":
    from labrad import util
    util.runServer(__server__)
