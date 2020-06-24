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
version = 1.3
description =

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

FILSIGNAL = 593201
MLSIGNAL = 953202
HVSIGNAL = 953203
BUFSIGNAL = 953204
QUESIGNAL = 953205

class RGA_Server( SerialDeviceServer ):
    name = SERVERNAME
    regKey = 'SRSRGA'
    port = None
    serNode = getNodeName()
    timeout = T.Value(TIMEOUT,'s')

    filsignal = Signal(FILSIGNAL, 'signal: filament changed', 'w')
    mlsignal = Signal(MLSIGNAL, 'signal: mass lock changed', 'v')
    hvsignal = Signal(HVSIGNAL, 'signal: high voltage changed', 'w')
    bufsignal = Signal(BUFSIGNAL, 'signal: buffer read', 's')
    quesignal = Signal(QUESIGNAL, 'signal: query sent', 's')

    listeners = set()

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
    def initContext(self, c):
        self.listeners.add(c.ID)
    def expireContext(self, c):        #Removes expired contexts from the listeners list?
        self.listeners.remove(c.ID)
    def getOtherListeners(self, c):    #Returns a list of listeners without the context itself.
        notified = self.listeners.copy()
        if c.ID in notified:
            notified.remove(c.ID)
        return notified

    @setting(1, returns='s')
    def identify(self, c):
        '''
        Returns the RGA's IDN. RGACOM command: 'id?'
        '''
        yield self.ser.write_line('id?')
        message = "id? command sent."
        self.quesignal(message, self.listeners.copy())
        returnValue(message)

    @setting(2, value='w',returns='s')
    def filament(self, c, value=None):
        '''
        Sets the filament on/off mode, or read its value.
        ".filament(0)" shuts off the filament.  RGACOM command: "fl0"
        ".filament(1)" turns on the filament.  RGACOM command: "fl1"
        ".filament()" asks for the filament mode.  RGACOM command: "fl?"
        '''
        notified = self.getOtherListeners(c)
        if value > 1:
            message = 'Input out of range. Acceptable inputs: 0 and 1.'
        elif value==1:
            yield self.ser.write_line('fl1')
            message = 'Filament on command sent.'
            self.filsignal(1, notified)
        elif value==0:
            yield self.ser.write_line('fl0')
            message = 'Filament off command sent.'
            self.filsignal(0, notified)
        elif value==None:
            yield self.ser.write_line('fl?')
            message = 'fl? command sent.'
            self.quesignal(message, self.listeners.copy())
        returnValue(message)

    @setting(3, value='v', returns='s')
    def mass_lock(self, c, value):
        '''
        Sets the mass lock for the RGA.  Acceptable range: [1,200].  RGACOM command:  "mlx"
        ".mass_lock(x)" sets the mass filter to x (positive integer representing amu).
        '''
        notified = self.getOtherListeners(c)
        if value<1 or value>200:
            message = 'Mass out of range.  Acceptable range: [1,200]'
        else:
            yield self.ser.write_line('ml'+str(value))
            message = 'Mass lock for '+str(value)+' amu command sent.'
            self.mlsignal(value, notified)
        returnValue(message)

    @setting(4, value='w', returns='s')
    def high_voltage(self, c, value=None):
        '''
        Sets the electron multiplier voltage.  Acceptable range: [0,2500]
        ".high_voltage()" asks for the electron multiplier voltage.  RGACOM command: "hv?"
        ".high_voltage(x)" sets the electron multiplier voltage to x (positive integer representing volts).  RGA COM command: "hvx"
        '''
        notified = self.getOtherListeners(c)
        if value==None:
            yield self.ser.write_line('hv?')
            message = 'hv? request sent.'
            self.quesignal(message, self.listeners.copy())
        elif value > 2500:
            message = 'Voltage out of range.  Acceptable range: [0,2500]'
        else:
            yield self.ser.write_line('hv'+str(value))
            message = 'High voltage (electron multiplier) command sent.'
            self.hvsignal(value, notified)
        returnValue(message)
    @setting(5, returns='s')
    def read_buffer(self, c):
        '''
        Reads the RGA buffer.  Equivalent to reading the serial line buffer.
        '''
        notified = self.getOtherListeners(c)
        message = yield self.ser.read_line()
        self.bufsignal(message, notified)
        returnValue(message)

__server__ = RGA_Server()

if __name__ == "__main__":
    from labrad import util
    util.runServer(__server__)
