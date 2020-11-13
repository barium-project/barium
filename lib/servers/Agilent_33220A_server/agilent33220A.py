# Copyright (C) 2011 Anthony Ransford
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
name = Agilent 33220A Server
version = 1.3
description = 
instancename = Agilent 33220A Server


[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""

from labrad.server import setting
from labrad.gpib import GPIBManagedServer, GPIBDeviceWrapper
from twisted.internet.defer import inlineCallbacks, returnValue

class AgilentWrapper(GPIBDeviceWrapper):
    
    def initialize(self):
        '''
        Provides a lookup table for waveform to GPIB lingo
        '''
        self.lookup = {'sine':'SIN', 'square':'SQU', 'ramp':'RAMP', 'pulse':'PULS', 'noise':'NOIS', 'DC' : 'DC', 'USER':'USER'}
        

    
    @inlineCallbacks
    def Output(self, output = None):
        '''
        Turns on or off the rigol output of specified channel
        '''

        if output == True:
            yield self.write("OUTP" + " ON")
        elif output == False:
            yield self.write("OUTP" + " OFF")
        else:
            yield self.write("OUTP" + "?")
            state = yield self.read()
            returnValue(state)
            
            
    @inlineCallbacks
    def applyWaveForm(self, function, frequency, amplitude, offset):
        '''
        Applys given waveform:'sine', 'square', 'ramp', 'pulse', 'noise', 'DC' , 'USER' 
        '''
        output = "APPL:" + self.lookup[function]  + ' ' + str(int(frequency['Hz'])) + ',' + str(amplitude['V']) + ',' + str(offset['V'])
        yield self.write(output)
     
    @inlineCallbacks    
    def WaveFunction(self, function = None):
        '''
        Changes wave form
        '''
        if function == None:
            output = "FUNC" + "?"
            yield self.write(output)
            func = yield self.read()
            returnValue(func)
        else:
            output = "FUNC"  + " " + self.lookup[function]
            yield self.write(output)

        
    @inlineCallbacks
    def Frequency(self, frequency = None):
        '''
        Sets frequency
        '''
        if frequency == None:
            output = "FREQ" +"?"
            yield self.write(output)
            freq = yield  self.read()
            returnValue(freq)
        else:
            output = "FREQ " + str(int(frequency['Hz']))
            yield self.write(output)

    @inlineCallbacks
    def setDC(self, voltage = None):
        '''
        sets DC output value
        '''
        if voltage == None:
            output = "VOLT:OFFS" 
            yield self.write(output)
            volts = self.read()
            returnValue(volts)
        else:
            output = 'APPL:DC' + ' DEF,DEF,' + str(voltage['V'])
            yield self.write(output)
        
        
    @inlineCallbacks
    def Amplitude(self, voltage = None):
        '''
        sets amp
        '''
        if voltage == None:
            output = "VOLT"  + "?"
            yield self.write(output)
            volts = yield self.read()
            returnValue(volts)
        else:
            output = "VOLT"  + " " + str(voltage['V'])
            yield self.write(output)

    @inlineCallbacks
    def AMSource(self, source):
        '''
        Select internal or external modulation source, the default is INT
        '''
        output = "AM:SOUR " + source
        yield self.write(output)
        
    @inlineCallbacks
    def AMFunction(self, function):
        '''
        Select the internal modulating wave of AM
        In internal modulation mode, the modulating wave could be sine,
        square, ramp, negative ramp, triangle, noise or arbitrary wave, the
        default is sine.
        '''
        output = "AM:INT:FUNC " + self.lookup[function]
        yield self.write(output)
        
    @inlineCallbacks
    def AMFrequency(self, frequency):
        '''
        Set the frequency of AM internal modulation in Hz
        Frequency range: 2mHz to 20kHz
        '''
        output = "AM:INT:FREQ " + str(frequency['Hz'])
        yield self.write(output)
        
    @inlineCallbacks
    def AMDepth(self, depth):
        '''
        Set the depth of AM internal modulation in percent
        Depth range: 0% to 120%
        '''
        output = "AM:DEPT " + str(depth)
        yield self.write(output)
        
    @inlineCallbacks
    def AMState(self, state):
        '''
        Disable or enable AM function
        '''
        if state:
            state = 'ON'
        else:
            state = 'OFF'
            
        output = "AM:STAT " + state
        yield self.write(output)

    @inlineCallbacks
    def FMSource(self, source):
        '''
        Select internal or external modulation source, the default is INT
        '''
        output = "FM:SOUR " + source
        yield self.write(output)
        
    @inlineCallbacks
    def FMFunction(self, function):
        '''
        In internal modulation mode, the modulating wave could be sine,
        square, ramp, negative ramp, triangle, noise or arbitrary wave, the
        default is sine
        '''
        output = "FM:INT:FUNC " + self.lookup[function]
        yield self.write(output)
        
    @inlineCallbacks
    def FMFrequency(self, frequency):
        '''
        Set the frequency of FM internal modulation in Hz
        Frequency range: 2mHz to 20kHz
        '''
        output = "FM:INT:FREQ " + str(frequency['Hz'])
        yield self.write(output)
        
    @inlineCallbacks
    def FMDeviation(self, deviation):
        '''
        Set the frequency deviation of FM in Hz.
        '''
        output = "FM:DEV " + str(deviation)
        yield self.write(output)
        
    @inlineCallbacks
    def FMState(self, state):
        '''
        Disable or enable FM function
        '''
        if state:
            state = 'ON'
        else:
            state = 'OFF'
            
        output = "FM:STAT " + state
        yield self.write(output)
        
        
        
    @inlineCallbacks
    def FSweepFrequencyCenter(self, frequency):
        '''
        Set the center frequency of Frequency Sweep modulation in Hz
        '''
        output = "FREQ:CENT " + str(frequency['Hz'])
        yield self.write(output)
        
        
    @inlineCallbacks
    def FSweepFrequencySpan(self, frequency):
        '''
        Set the frequency span of Frequency Sweep modulation in Hz
        '''
        output = "FREQ:SPAN " + str(frequency['Hz'])
        yield self.write(output)     
        
        
    @inlineCallbacks
    def FSweepTime(self, sweep_time):
        '''
        Set the time for a whole frequency sweep in s
        '''
        output = "SWE:TIME " + str(sweep_time['s'])
        yield self.write(output)        
                
        
    @inlineCallbacks
    def FSweepON(self):
        '''
        Turn on frequency sweep
        '''
        output = "SWE:STAT ON"
        yield self.write(output)        
        
        
    @inlineCallbacks
    def FSweepOFF(self):
        '''
        Turn off frequency sweep
        '''
        output = "SWE:STAT OFF"
        yield self.write(output)        
        
        
        


class AgilentServer(GPIBManagedServer):
    name = 'Agilent 33220A Server' # Server name
    deviceName = 'Agilent Technologies,33220A,MY44047452,2.07-2.06-22-2' # Model string returned from *IDN?
    deviceWrapper = AgilentWrapper


    @setting(10, 'Output', output = 'b')
    def deviceOutput(self, c,  output): # uses passed context "c" to address specific device
        dev = self.selectedDevice(c)
        yield dev.Output(output)
    
    @setting(69, 'Apply Waveform', function = 's', frequency = ['v[Hz]'], amplitude = ['v[V]'], offset = ['v[V]']  )
    def applyDeviceWaveform(self, c, function, frequency, amplitude, offset):
        '''
        Applys given waveform:'sine', 'square', 'ramp', 'pulse', 'noise', 'DC' , 'USER' \n
        arguments: waveform, frequency, amplitude, offset
        '''
        dev = self.selectedDevice(c)
        yield dev.applyWaveForm(function, frequency, amplitude, offset)
        
    @setting(707, 'Wave Function', function = 's')
    def deviceFunction(self, c, function = None):
        dev = self.selectedDevice(c)
        func = yield dev.WaveFunction(function)
        returnValue(func)

    @setting(131, 'Amplitude', value = 'v[V]')
    def Amplitude(self, c, value = None):
        dev = self.selectedDevice(c)
        volts = yield dev.Amplitude(value)
        returnValue(volts)

    @setting(92, 'Frequency', value = 'v[Hz]')
    def Frequency(self, c, value = None):
        dev = self.selectedDevice(c)
        freq = yield dev.Frequency(value)
        returnValue(freq)

    @setting(9, 'Apply DC', value = 'v[V]')
    def setDC(self, c, value = None):
        dev = self.selectedDevice(c)
        volts = yield dev.setDC(value)
        returnValue(volts)
        
        
    @setting(109, 'freq_sweep', freq_center = 'v[Hz]', freq_span = 'v[Hz]', amplitude = 'v[V]', sweep_time = 'v[s]')
    def FrequencySweep(self, c, freq_center, freq_span, amplitude, sweep_time):
        dev = self.selectedDevice(c)
        yield dev.write("SWE:SPAC LIN")
        yield dev.write("TRIG:SOUR IMM")
        yield dev.FSweepFrequencyCenter(freq_center)
        yield dev.FSweepFrequencySpan(freq_span) 
        yield dev.Amplitude(amplitude)
        yield dev.FSweepTime(sweep_time)
        yield dev.FSweepON()
        
        

    @setting(123, 'freq_sweep_off')
    def FrequencySweepOFF(self, c, value = None):
        dev = self.selectedDevice(c)
        yield dev.FSweepOFF()



__server__ = AgilentServer()

if __name__ == '__main__':
    from labrad import util
    util.runServer(__server__)
