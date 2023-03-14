# Copyright (C) 2022 Sam Vizvary
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
name = Windfreak Server
version = 1.0
description = Server to control Synth HD 

[startup]
cmdline = %PYTHON% %FILE%
timeout = 10

[shutdown]
message = 987654322
timeout = 5
### END NODE INFO
"""

from common.lib.servers.serialdeviceserver import SerialDeviceServer, setting,\
inlineCallbacks, SerialDeviceError, SerialConnectionError
from labrad import types as T
from twisted.internet.defer import returnValue
from labrad.support import getNodeName

SERVERNAME = 'Windfreak Server'
TIMEOUT = 1.0
BAUDRATE = 9600


class Windfreak_Server( SerialDeviceServer ):
    name = SERVERNAME
    regKey = 'Windfreak'
    port = None
    serNode = getNodeName()
    timeout = T.Value(TIMEOUT,'s')

    @inlineCallbacks
    def initServer( self ):
        if not self.regKey or not self.serNode: raise \
        SerialDeviceError( 'Must define regKey and serNode attributes' )
        port = yield self.getPortFromReg( self.regKey )
        self.port = port
        try:
            serStr = yield self.findSerial( self.serNode )
            self.initSerial( serStr, port, baudrate = BAUDRATE )
        except SerialConnectionError, e:
            self.ser = None
            if e.code == 0:
                print 'Could not find serial server for node: %s' % \
                self.serNode
                print 'Please start correct serial server'
            elif e.code == 1:
                print 'Error opening serial connection'
                print 'Check set up and restart serial server'
            else: raise

    @inlineCallbacks
    def connect(self):
        """
        Creates an Asynchronous connection labrad
        """
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync(name='Windfreak_Server')


    @setting(1)#, channel1 = 'w')
    def set_channel(self, c, channel1):
        """
        Switch between output channels on windfreak (0 is Channel A and
        1 is channel B
        """
        
        if channel1 < 0 or channel1 >1:
            returnValue('Channel number needs to be either 0(Channel A) or 1(Channel B)')

        else:
            yield self.ser.write_line('C' + str(channel1))

    @setting(100)#, returns = 'w')
    def get_channel(self, c):
        """
        Return the current output channel for Windfreak.
        """
        yield self.ser.write_line('C?')
        message = yield self.ser.read_line()

        try:
            returnValue(message)
        except:
            yield self.ser.write_line('C?')
            

            message = yield self.ser.read_line()
            returnValue(message)
        else:
            returnValue("Something went wrong, cannot get current channel")

    @setting(101)#, returns = 'w')
    def set_freq(self,c, freq):
        """
        Set freqeuency of output of set channel in MHz
        """
        
        if freq < 53 or freq >1400:
            returnValue('Freq must be between 53 and 1400 MHz')

        else:
            yield self.ser.write_line('f' + str(freq))
        
    @setting(102)#, returns = 'w') #maybe needs to be @inlineCallbacks
    def get_freq(self, c):
        """
        Return the current freq value for Windfreak output.
        """
        yield self.ser.write_line('f?')
        message = yield self.ser.read_line()
        try:
            returnValue(message)
        except:
            yield self.ser.write_line('f?')
            message = yield self.ser.read_line()
            returnValue(message)
        else:
            returnValue("Something went wrong, cannot get current frequency")

    @setting(103)#, returns = 'w')
    def set_power(self, c, p):
        """
        Set power of output of set channel in dbm
        """
        
        if p < -60 or p >20:
            returnValue('Power must be between -60 and 20 db')

        else:
            yield self.ser.write_line('W' + str(p))

    @setting(104)#, returns = 'w') #maybe needs to be @inlineCallbacks
    def get_power(self, c):
        """
        Return the current power value for Windfreak output.
        """
        yield self.ser.write_line('W?')
        message = yield self.ser.read_line()
        returnValue(message)
        try:
            returnValue(message)
        except:
            yield self.ser.write_line('W?')
            message = yield self.ser.read_line()
            #returnValue(message)
        else:
            returnValue("Something went wrong, cannot get current power")
    @setting(105)#, returns = 'w')
    def turn_on_RF(self, c):
        """
        Turns on output of selected channel of Windfreak
        """
        
        yield self.ser.write_line("E1")

    @setting(106)#, returns = 'w')
    def turn_off_RF(self, c):
        """
        Turns off output of selected channel of Windfreak
        """
        
        yield self.ser.write_line("E0")


    @setting(107)#, returns = 'w')
    def is_rf_on(self, c):
        """
        Turns off output of selected channel of Windfreak
        """
        yield self.ser.write_line('E?')
        message = yield self.ser.read_line()

        if message=="1":
            returnValue(True)
        elif message=="0":
            returnValue(False)
            




                        
__server__ = Windfreak_Server()

if __name__ == "__main__":
    from labrad import util
    util.runServer(__server__)

