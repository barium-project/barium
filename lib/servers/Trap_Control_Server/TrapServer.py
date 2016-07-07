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
name = Trap Server
version = 1.0
description =
instancename = %LABRADNODE% Trap Server

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

SERVERNAME = 'Trap Server'
TIMEOUT = 1.0
BAUDRATE = 38400

class TrapServer( SerialDeviceServer ):
    name = SERVERNAME
    regKey = 'TrapControl'
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

        # Define the trap electronics parameters
        self.max_frequency = 500e6 # Hz
        self.max_amplitude = 500 #V
        self.max_phase = 360 # degrees
        self.max_hv = 1600 # V
        self.max_dc = 54 # V

    @setting(1, returns = 's')
    def command_list(self, c):
        ''' Returns a string with the list of commands.
            print the result to see the list.'''
        yield self.ser.write('help \n')
        commands = yield self.ser.read()
        returnValue(commands)

    # Declare all set functions

    @setting(2,'update_DDS')
    def update_DDS(self,c):
        ''' Updates changes to the DDS values amplitude, frequency, and phase.
            Must be done every change'''
        yield self.ser.write('i \n')


    @setting(3,'set_frequency',frequency = 'w', channel = 'w')
    def set_frequency(self, c, frequency, channel):
        '''Set the frequency of a channel in Hz using 4 byte hexidecimal rep.
           32 LSBs'''
        if frequency > self.max_frequency:
            returnValue('Frequency cannot exceed ' str(self.max_frequency))
        step = int(2**32/self.max_frequency*frequency)
        hex_num = hex(step)
        hex_num = hex_num[2:] # Eliminate the 0x from the number
        yield self.ser.write('fx ' + str(channel) + ' ' + str(hex_num[2:]) +' \n')

    @setting(4,'set_amplitude',amplitude = 'w', channel = 'w')
    def set_amplitude(self, c, amplitude, channel):
        '''Set the amplitude of a channel in v using 2 byte hexidecimal rep. 10 LSBs'''
        if amplitude > self.max_amplitude:
            returnValue('Amplitude cannot exceed ' + str(self.max_ampltude))
        step = int(2**10/self.max_amplitude*amplitude)
        hex_num = hex(step)
        hex_num = hex_num[2:] # Eliminate the 0x from the number
        yield self.ser.write('ax ' + str(channel) + ' ' + str(hex_num[2:]) +' \n')

    @setting(5,'set_phase', phase = 'w', channel = 'w')
    def set_phase(self, c, phase, channel):
        '''Set the phase of a channel in degrees using 2 byte hexidecimal rep. 14 LSBs'''
        if phase > self.max_phase:
            returnValue('Phase cannot exceed ' + str(self.max_phase))
        step = int(2**14/self.max_phase*phase)
        hex_num = hex(step)
        hex_num = hex_num[2:] # Eliminate the 0x from the number
        yield self.ser.write('px ' + str(channel) + ' ' + str(hex_num[2:]) +' \n')

    @setting(6,'set_dc', dc = 'w', channel = 'w')
    def set_dc(self, c, dc, channel):
        '''Set the dc of a channel in degrees using 2 byte hexidecimal rep. 12 LSBs
           Range 0-54V'''
        if dc > self.max_dc:
            returnValue('Voltage cannot exceed ' + str(self.max_dc))
        step = int(2**12/self.max_dc*dc)
        hex_num = hex(step)
        hex_num = hex_num[2:] # Eliminate the 0x from the number
        yield self.ser.write('dcx ' + str(channel) + ' ' + str(hex_num[2:]) + ' \n')

    @setting(7,'set_dc_rod', dc = 'w', channel = 'w')
    def set_dc_rod(self, c, dc, channel):
        '''Set the dc rod of a channel in volts using 2 byte hexidecimal rep. 12 LSBs
           Amplifier circuit puts out half the value of the DC box. Rod voltage 0-27V'''
        if dc > self.max_dc/2.:
            returnValue('Voltage cannot exceed ' + str(self.max_dc/2.))
        step = int(2**12/self.max_dc*dc*2) # Extra factor of 2 for amplifier reduction by 1/2
        hex_num = hex(step)
        hex_num = hex_num[2:] # Eliminate the 0x from the number
        yield self.ser.write('dcx ' + str(channel) + ' ' + str(hex_num[2:]) +' \n')

    @setting(8,'set_hv', hv = 'w', channel = 'w')
    def set_hv(self, c, hv, channel):
        '''Set the  hv dc of a channel in volts using 2 byte hexidecimal rep.
           12 LSBs'''
        if dc > self.max_hv:
            returnValue('Voltage cannot exceed ' + str(self.max_hv))
        step = int(2**12/max_hv*dc)
        hex_num = hex(step)
        hex_num = hex_num[2:] # Eliminate the 0x from the number
        yield self.ser.write('hvx ' + str(channel) + ' ' + str(hex_num[2:]) +' \n')

# Define all get functions

    @setting(9,'get_frequency', frequency = 'w', channel = 'w')
    def get_frequency(self, c, hv, channel):
        '''Set the  frequency of a given channel'''
        yield self.ser.write('fg ' + str(channel) +' \n')
        yield hex_string = self.ser.read()



if __name__ == "__main__":
    from labrad import util
    util.runServer( TrapServer() )