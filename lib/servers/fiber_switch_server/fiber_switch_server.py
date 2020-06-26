# Copyright (C) 2020 Keqin Yan
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>

"""
### BEGIN NODE INFO
[info]
name = Fiber Switch Server
version = 1.0
description =

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
from labrad.server import Signal
from labrad import types as T
from twisted.internet.task import LoopingCall
from twisted.internet.defer import returnValue
from labrad.support import getNodeName
#import os

#import time

SERVERNAME = 'Fiber Switch Server'
TIMEOUT = 1.0
BAUDRATE = 9600


class Fiber_Switch_Server( SerialDeviceServer ):
    name = SERVERNAME
    regKey = 'FiberSwitch'
    port = None
    serNode = getNodeName()
    timeout = T.Value(TIMEOUT,'s')
    #password = os.environ['LABRADPASSWORD']

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


    @setting(1, channel1 = 'w')
    def set_channel(self, c, channel1):
        """
        Switch between input channels on the optical fiber switch. Acceptable Range: [01, 08]
        """
        yield self.ser.write_line('<OSW_OUT_0' + str(channel1) + '>')
        if channel1 > 8 or channel1 < 1:
            print 'Channel number needs to be from 1 to 8'


    @setting(100, returns = 'w')
    def get_channel(self, c):
        """
        Return the current input channel for the fiber switch.
        """
        yield self.ser.write_line('<OSW_OUT_?>')
        message = yield self.ser.read_line()
        try:
#            if message[10] != num:
#                raise except
            returnValue(int(message[10]))
        except:
            yield self.ser.write_line('<OSW_OUT_?>')
            message = yield self.ser.read_line()
            returnValue(int(message[10]))
        else:
            returnValue("Something went wrong, cannot get current channel")


__server__ = Fiber_Switch_Server()

if __name__ == "__main__":
    from labrad import util
    util.runServer(__server__)

