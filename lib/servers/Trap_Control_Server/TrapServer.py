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
name = TrapServer
version = 1.0
description =
instancename = TrapServer

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

SERVERNAME = 'TrapServer'
TIMEOUT = 1.0
BAUDRATE = 38400

class TrapServer( SerialDeviceServer ):
    name = 'TrapServer'
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
        self.max_frequency = 500.e6 # Hz
        self.max_amplitude = 1233. #V
        self.max_phase = 360. # degrees
        self.max_hv = 1600. # V
        self.max_dc = 52.9 # V
        self.frequency_steps = 2**32-1
        self.amplitude_steps = 2**10-1
        self.phase_steps = 2**14-1
        self.dc_steps = 2**12-1
        self.hv_steps = 2**12-1

        # Set the state of the rf map
        self.use_RFMap = False

        # Set the state of RF
        self.enable_RF = True

        # Set the battery charging
        self.bat_charging = False


    @setting(1, returns = 's')
    def command_list(self, c):
        ''' Returns a string with the list of commands.
            print the result to see the list.'''
        yield self.ser.write('help \n')
        commands = yield self.ser.read()
        returnValue(commands)

    # Declare all set functions

    @setting(2,'update_rf')
    def update_rf(self,c):
        ''' Updates changes to the DDS values amplitude, frequency, and phase.
            Must be done every change'''
        yield self.ser.write('i \n')


    @setting(3,'set_frequency',frequency = ['v[]: frequency [Hz]'], channel = ['w: channel number']
             , returns = [''])
    def set_frequency(self, c, frequency, channel):
        '''Set the frequency of a channel in Hz using 4 byte hexidecimal rep.
           32 LSBs'''
        if frequency > self.max_frequency:
            returnValue('Frequency cannot exceed ' + str(self.max_frequency))
        step = int(self.frequency_steps/self.max_frequency*frequency)
        # Create a hex number without "0x" and pad with leading zeros if necessary
        hex_num = "{0:0{1}x}".format(step,8)
        yield self.ser.write('fx ' + str(channel) + ' ' + hex_num +' \n')

    @setting(4,'set_amplitude',amplitude = 'v[]', channel = 'w')
    def set_amplitude(self, c, amplitude, channel):
        '''Set the amplitude of a channel in v using 2 byte hexidecimal rep. 10 LSBs'''
        if amplitude > self.max_amplitude:
            returnValue('Amplitude cannot exceed ' + str(self.max_ampltude))
        step = int(self.amplitude_steps*amplitude/self.max_amplitude)
        # Create a hex number without "0x" and pad with leading zeros if necessary
        hex_num = "{0:0{1}x}".format(step,4)
        yield self.ser.write('ax ' + str(channel) + ' ' + hex_num +' \n')

    @setting(5,'set_phase', phase = 'v[]', channel = 'w')
    def set_phase(self, c, phase, channel):
        '''Set the phase of a channel in degrees using 2 byte hexidecimal rep. 14 LSBs'''
        if phase > self.max_phase:
            returnValue('Phase cannot exceed ' + str(self.max_phase))
        step = int(self.phase_steps*phase/self.max_phase)
        # Create a hex number without "0x" and pad with leading zeros if necessary
        hex_num = "{0:0{1}x}".format(step,4)
        yield self.ser.write('px ' + str(channel) + ' ' + hex_num +' \n')

    @setting(6,'set_dc', dc = 'v[]', channel = 'w')
    def set_dc(self, c, dc, channel):
        '''Set the dc of a channel in degrees using 2 byte hexidecimal rep. 12 LSBs
           Range 0-54V'''
        if dc > self.max_dc:
            returnValue('Voltage cannot exceed ' + str(self.max_dc))
        step = int((self.dc_steps)*dc/self.max_dc)
        # Create a hex number without "0x" and pad with leading zeros if necessary
        hex_num = "{0:0{1}x}".format(step,4)
        yield self.ser.write('dcx ' + str(channel) + ' ' + hex_num + ' \n')

    @setting(7,'set_dc_rod', dc = 'v[]', channel = 'w')
    def set_dc_rod(self, c, dc, channel):
        '''Set the dc rod of a channel in volts using 2 byte hexidecimal rep. 12 LSBs
           Amplifier circuit puts out half the value of the DC box. Rod voltage 0-27V'''
        if dc > self.max_dc/2.:
            returnValue('Voltage cannot exceed ' + str(self.max_dc/2.))
        step = int(self.dc_steps*dc*2/self.max_dc) # Extra factor of 2 for amplifier reduction by 1/2
        # Create a hex number without "0x" and pad with leading zeros if necessary
        hex_num = "{0:0{1}x}".format(step,4)
        yield self.ser.write('dcx ' + str(channel) + ' ' + hex_num +' \n')

    @setting(8,'set_hv', hv = 'v[]', channel = 'w')
    def set_hv(self, c, hv, channel):
        '''Set the  hv dc of a channel in volts using 2 byte hexidecimal rep.
           12 LSBs'''
        if hv > self.max_hv:
            returnValue('Voltage cannot exceed ' + str(self.max_hv))
        step = int(self.hv_steps*hv/self.max_hv)
        # Create a hex number without "0x" and pad with leading zeros if necessary
        hex_num = "{0:0{1}x}".format(step,4)
        yield self.ser.write('hvx ' + str(channel) + ' ' + hex_num +' \n')

    @setting(9,'set_rf_state', state = 'b')
    def set_rf_state(self, c, state):
        '''Turns on or off all rf outputs'''
        if state == True:
            self.enable_RF = True
            yield self.ser.write('o 1 \n')
        elif state== False:
            self.enable_RF = False
            yield self.ser.write('o 0 \n')

    @setting(11,'update_dc')
    def update_dc(self, c):
        '''Update the dc values on all rods'''
        yield self.ser.write('dci \n')

    @setting(12,'update_hv')
    def update_hv(self, c):
        '''Update the hv values on all rods'''
        yield self.ser.write('hvi \n')

    @setting(13,'clear_phase_accumulator')
    def clear_phase_accumulator(self, c):
        '''Reset the phase difference to the stored values'''
        self.set_rf_state(c, False)
        yield self.ser.write('c \n')
        self.set_rf_state(c, True)

    @setting(14,'clear_dc')
    def clear_dc(self, c):
        '''clear all dc values'''
        yield self.ser.write('dcc \n')

    @setting(15,'clear_hv')
    def clear_hv(self, c):
        '''clear all hv values'''
        yield self.ser.write('hvc \n')

    @setting(16,'set_loading_time', t1 = 'w', t2 = 'w')
    def set_loading_time(self, c, t1, t2):
        '''Set the trap loading sequence in usec. t1 = q-switch wait,
           t2 = rf off delay after q-switch wait'''
        yield self.ser.write('t ' + str(t1) + ' ' + str(t2) +' \n')

    @setting(17,'trigger_loading')
    def trigger_loading(self, c):
        '''Trigger the loading sequence upon next q-switch TTL'''
        yield self.ser.write('l \n')

    @setting(18,'trigger_hv_pulse')
    def trigger_hv_pulse(self, c):
        '''Trigger the HV pulse'''
        yield self.ser.write('h \n')

    @setting(19,'set_dc_state', state = 'b')
    def set_dc_state(self, c, state):
        '''Turns on or off all dc outputs'''
        if state == True:
            yield self.ser.write('dco 1 \n')
        if state == False:
            yield self.ser.write('dco 0 \n')

    @setting(20,'set_hv_state', state = 'b')
    def set_hv_state(self, c, state):
        '''Turns on or off all hv outputs'''
        if state == True:
            yield self.ser.write('hvo 1 \n')
        if state == False:
            yield self.ser.write('hvo 0 \n')

    @setting(21,'set_battery_charging', state = 'b')
    def set_battery_charging(self, c, state):
        '''Turns on or off battery charging'''
        if state == True:
            self.bat_charging = True
            yield self.ser.write('b 1 \n')
        if state == False:
            self.bat_charging = False
            yield self.ser.write('b 0 \n')

    @setting(22,'reset_DDS')
    def reset_DDS(self, c):
        '''Resets the DDS chips and sets all values to zero'''
        yield self.ser.write('x \n')

    @setting(23,'set_rf_map_state', state = 'b')
    def set_rf_map_state(self,c, state):
        self.use_RFMap = state


    @setting(24,'reset_DC')
    def reset_DC(self, c):
        '''Resets the DC set all values to zero'''
        yield self.ser.write('dcr \n')

# Define all get functions

    @setting(50,'get_frequency', channel = 'w')
    def get_frequency(self, c, channel):
        '''Get the  frequency of a given channel'''
        yield self.ser.write('fg ' + str(channel) +' \n')
        hex_string = yield self.ser.read_line()
        hex_string = hex_string.replace(' ','')
        freq_steps = int(hex_string,16)
        frequency = freq_steps*self.max_frequency/self.frequency_steps
        returnValue(frequency)

    @setting(51,'get_amplitude', channel = 'w')
    def get_amplitude(self, c, channel):
        '''Get the  amplitude of a given channel'''
        yield self.ser.write('ag ' + str(channel) +' \n')
        hex_string = yield self.ser.read_line()
        hex_string = hex_string.replace(" ","")
        amp_steps = int(hex_string,16)
        amplitude = amp_steps*self.max_amplitude/(self.amplitude_steps)
        returnValue(amplitude)

    @setting(52,'get_phase', channel = 'w')
    def get_phase(self, c, channel):
        '''Get the phase of a given channel'''
        yield self.ser.write('pg ' + str(channel) +' \n')
        hex_string = yield self.ser.read_line()
        hex_string = hex_string.replace(' ','')
        phase_steps = int(hex_string,16)
        phase = phase_steps*self.max_phase/self.phase_steps
        returnValue(phase)

    @setting(53,'get_dc', channel = 'w')
    def get_dc(self, c, channel):
        '''Get the dc value of a given channel'''
        yield self.ser.write('dcg ' + str(channel) +' \n')
        hex_string = yield self.ser.read_line()
        hex_string = hex_string.replace(' ','')
        dc_steps = int(hex_string,16)
        dc = dc_steps*self.max_dc/self.dc_steps
        returnValue(dc)


    @setting(54,'get_dc_rod', channel = 'w')
    def get_dc_rod(self, c, channel):
        '''Get the dc value of a given rod'''
        yield self.ser.write('dcg ' + str(channel) +' \n')
        hex_string = yield self.ser.read_line()
        hex_string = hex_string.replace(' ','')
        dc_rod_steps = int(hex_string,16)
        dc_rod = dc_rod_steps*self.max_dc/self.dc_steps/2
        returnValue(dc_rod)

    @setting(55,'get_hv', channel = 'w')
    def get_hv(self, c, channel):
        yield self.ser.write('hvg ' + str(channel) +' \n')
        hex_string = yield self.ser.read_line()
        hex_string = hex_string.replace(' ','')
        hv_steps = int(hex_string,16)
        hv = hv_steps*self.max_hv/self.hv_steps
        returnValue(hv)

    @setting(56,'read_buffer')
    def read_buffer(self, c):
        '''Reads the buffer if you want to check for errors'''
        string = yield self.ser.read_line()
        returnValue(string)

    @setting(57,'get_rf_map_state', returns = 'b')
    def get_rf_map_state(self,c):
        return(self.use_RFMap)

    @setting(58,'get_rf_state', returns = 'b')
    def get_rf_state(self,c):
        return(self.enable_RF)

    @setting(59,'get_battery_charging', returns = 'b')
    def get_battery_charging(self, c):
        return(self.bat_charging)

if __name__ == "__main__":
    from labrad import util
    util.runServer( TrapServer() )
