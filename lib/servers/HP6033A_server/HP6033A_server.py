# Copyright (C) 2016 Calvin He
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
name = HP6033A_Server
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

from labrad.server import setting, Signal
from labrad.gpib import GPIBManagedServer, GPIBDeviceWrapper
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet import reactor
from labrad.units import WithUnit as U
from time import sleep

CURRSIGNAL = 186421
VOLTSIGNAL = 186422
MEASSIGNAL = 186423
OUTPSIGNAL = 186424
PULMSIGNAL = 186425

class HP6033A_Server(GPIBManagedServer):
    '''
    This server talks to the HP 6033A Power Supply.  Refer to the individual functions for their descriptions.

     Important:  Make sure the power supply's system language is set to TMSL or this server will not work!
     Write 'SYST:LANG TMSL' to change the language (i.e. gpib_write('SYST:LANG TMSL'))
     Then you will also need to set the secondary address to --- (null).  To do so [Operating Manual pg. 86],
         1) Press and hold the LCL button until the secondary address is displayed.
         2) Turn the RPG while the secondary address is being displayed to change the secondary address.
    '''
    name = 'HP6033A_Server'
    deviceName = 'HEWLETT-PACKARD 6033A'

    currsignal = Signal(CURRSIGNAL, 'signal: current changed', 'v[A]')
    voltsignal = Signal(VOLTSIGNAL, 'signal: voltage changed', 'v[V]')
    meassignal = Signal(MEASSIGNAL, 'signal: get measurements', '(v[V]v[A])')
    outpsignal = Signal(OUTPSIGNAL, 'signal: output changed', 'b')
    pulmsignal = Signal(PULMSIGNAL, 'signal: pulse mode changed', 'b')

    def __init__(self):
        super(HP6033A_Server, self).__init__()
        self.listeners = set()
        self.updating = False
    def initContext(self, c):          #Adds new contexts to the listeners list?
        self.listeners.add(c.ID)
        if self.updating == False:
            self.updating = True
            #self.update_settings(c)    #The server will initially get a "No devices has be selected" error, but this will pass once the client selects a device.
    def expireContext(self, c):        #Removes expired contexts from the listeners list?
        self.listeners.remove(c.ID)
        if 'device' in c:
            alias = c['device']
            try:
                dev = self.devices[alias]
                if dev.lockedInContext(c):
                    dev.unlock(c)
                dev.deselect(c)
            except KeyError:
                pass
    def getOtherListeners(self, c):    #Returns a list of listeners without the context itself.
        notified = self.listeners.copy()
        if c.ID in notified:
            notified.remove(c.ID)
        return notified

    @setting(96, 'Update Settings', returns = 's')
    def update_settings(self, c):
        '''
        This begins a self-calling loop which updates the power supply settings to the client.
        '''

        reactor.callLater(1, lambda c=c:self.update_settings(c))
        notified = self.listeners.copy()

        #output_state = yield self.output_state(c)
        #print output_state
        #self.outpsignal(int(output_state),notified)

        #set_voltage = yield self.get_set_voltage(c)
        #print set_voltage
        #self.voltsignal(set_voltage,notified)

        #set_current = yield self.get_set_current(c)
        #print set_current
        #self.currsignal(set_current,notified)

        measured_voltage = yield self.get_voltage(c)
        measured_current = yield self.get_current(c)
        self.meassignal([measured_voltage, measured_current],notified)


        returnValue('Nothing')
    @setting(10, 'Get VOLTage', returns = 'v[V]')
    def get_voltage(self, c):
        '''
        Measures the voltage on the power supply and returns a value with unit V.

         Equivalent to MEAS:VOLT?
        '''
        dev = self.selectedDevice(c)    #This line allows .read() and .write() to be called from the GPIBDeviceWrapper
        yield dev.write('MEAS:VOLT?')
        result = yield dev.read()      #dev.read() returns a string
        voltage = U(float(result),'V') #convert string to float with units
        self.clear_status(c)
        returnValue(voltage)

    @setting(11, 'Get CURRent', returns = 'v[A]')
    def get_current(self, c):
        '''
        Measures the current on the power supply and returns a value with unit A.

         Equivalent to MEAS:CURR?
        '''
        dev = self.selectedDevice(c)
        yield dev.write('MEAS:CURR?')
        result = yield dev.read()
        current = U(float(result),'A') #convert string to float with units
        self.clear_status(c)
        returnValue(current)

    @setting(103, 'Pulse Initialize', value = 'b')
    def pulse_initialize(self, c, value):
        '''
        Initializes the power supply for pulse mode by setting voltage and current to 0.
        '''
        notified = self.getOtherListeners(c)
        if value==True:
            yield self.set_voltage(U(0,'V'))
            yield self.set_current(U(0,'A'))
        self.pulmsignal(value, notified)


    @setting(101, 'Pulse Voltage', voltage = 'v[V]', current = 'v[A]', duration = 'v[s]', returns='s')
    def pulse_voltage(self, c, voltage, current, duration):
        '''
        Instructs the power supply to output a square pulse at a desired voltage [Volts] for a desired duration [seconds].

         Be sure to first initialize the voltage to 0 V.
        '''
        dev = self.selectedDevice(c)
        if voltage['V'] > 20 or voltage['V'] < 0:
            message = "Input voltage, "+str(voltage['V'])+" V, out of range.  (Range: 0-20 V)"
            returnValue(message)
        else:
            yield dev.write('CURR ' + str(current['A']) + ' A')
            yield dev.write('VOLT ' + str(voltage['V']) + ' V')    #sets the voltage to value
            print "Pulsing " + str(voltage['V']) + " V over " + str(duration['s']) + " s..."
            sleep(duration['s'])                   #waits for the duration
            yield dev.write('VOLT 0 V')                 #sets the voltage back to 0
            print "Finished pulsing."
            error = 'none'#yield self.error(c) #Calls the .error() method to read the error message register
            returnValue(error)          #Returns the message to the user. '+0, "No error"' means no error.

    @setting(102, 'Pulse Current', current = 'v[A]', voltage = 'v[V]', duration = 'v[s]', returns='s')
    def pulse_current(self, c, current, voltage, duration):
        '''
        Instructs the power supply to output a square pulse at a desired current [Amps] for a desired duration [seconds].

         Be sure to first initialize the current to 0 A.
        '''
        dev = self.selectedDevice(c)
        if current['A'] > 30 or current['A'] < 0:
            message = "Input current, "+str(current['A'])+" A, out of range.  (Range: 0-30 A)"
            returnValue(message)
        else:
            yield dev.write('VOLT ' + str(voltage['V']) + ' V')
            yield dev.write('CURR ' + str(current['A']) + ' A')
            print "Pulsing " + str(current['A']) + " A over " + str(duration['s']) + " s..."
            sleep(duration['s'])
            yield dev.write('CURR 0 A')
            print "Finished pulsing."
            error = 'none'#yield self.error(c)
            returnValue(error)

    @setting(13, 'Set Current', value = 'v[A]', returns='s')
    def set_current(self, c, value):
        '''
        Sets the immediate current on the power supply.

         The immediate current is the current programmed for the output terminals.
         Equivalent to CURR <value> <units>
        '''
        dev = self.selectedDevice(c)
        notified = self.getOtherListeners(c)
        if value['A'] > 30 or value['A'] < 0:
            message = "Input current, "+str(value['A'])+" A, out of range.  (Range: 0-30 A)"
            returnValue(message)
        else:
            yield dev.write('CURR '+str(value['A'])+' A')
            self.currsignal(value,notified)
            error = yield self.error(c)
            print error
            returnValue(error)

    @setting(14, 'Set Voltage', value = 'v[V]', returns='s')
    def set_voltage(self, c, value):
        '''
        Sets the immediate voltage on the power supply.

         The immediate voltage is the voltage programmed for the output terminals.
         Equivlanet to VOLT <value> <units>
        '''
        dev = self.selectedDevice(c)
        notified = self.getOtherListeners(c)
        if value['V'] > 20 or value['V'] < 0:
            message = "Input voltage, "+str(value['V'])+" V, out of range.  (Range: 0-20 V)"
            returnValue(message)
        else:
            yield dev.write('VOLT '+str(value['V'])+' V')
            self.voltsignal(value,notified)
            error = yield self.error(c)
            print error
            returnValue(error)

    @setting(31, 'Get Set Current', returns = 'v[A]')
    def get_set_current(self, c):
        dev = self.selectedDevice(c)
        yield dev.write('CURR:LEV?')
        message = yield dev.read()
        result = U(float(message),'A')
        returnValue(result)

    @setting(32, 'Get Set Voltage', returns = 'v[V]')
    def get_set_voltage(self, c):
        dev = self.selectedDevice(c)
        yield dev.write('VOLT:LEV?')
        message = yield dev.read()
        result = U(float(message),'V')
        returnValue(result)

    @setting(15, 'Output State', value = 'b', returns = 's')
    def output_state(self, c, value=None):#Overloaded Function
        '''
        Passing a boolean value (True or False, case sensitive) sets on/off state of the output on the power supply.

         Equivalent to OUTP <0/1>
         Passing no arguments will query the power supply for its state.
         Equivalent to OUTP:STAT?
        '''
        dev = self.selectedDevice(c)
        notified = self.getOtherListeners(c)
        if value==None:                     #This is the behavior if no input is given
            yield dev.write('OUTP:STAT?')
            state = yield dev.read()
            self.clear_status(c)
            returnValue(state)
        else:                               #This is the behavior if input is given
            if value == True:
                 bit = 1
            elif value == False:
                 bit = 0
            yield dev.write('OUTP '+str(bit))
            self.outpsignal(value,notified)
            error = 'none'#yield self.error(c)
            returnValue(error)

    @setting(16, 'Output Clear', returns='s')
    def output_clear(self, c):
        #Not Yet Tested but should work
        '''
        Clears output overvoltage, overcurrent, or overtemperature status condition.

         Equivalent to OUTP:PROT:CLE
        '''
        dev = self.selectedDevice(c)
        yield dev.write('OUTP:PROT:CLE')
        error = 'none'#yield self.error(c)
        returnValue(error)

    @setting(17, 'IDN', returns = 's')
    def idn(self, c):
        '''
        Requests the device identify itself.

         Equivalent to *IDN?
        '''
        dev = self.selectedDevice(c)
        yield dev.write('*IDN?')
        sleep(0.5)
        idn = yield dev.read()
        self.clear_status(c)
        returnValue(idn)

    @setting(18, 'Settings Recall', value = 'i', returns='s')
    def settings_recall(self, c, value):
        '''
        Recalls power supply settings from 1 of 5 memory locations (index 0 to 4).

         Settings affected:  Current, Voltage, Output
         Equivalent to *RCL <value>
         Use settings_save to save settings.
        '''
        dev = self.selectedDevice(c)
        if value<0 or value >4:
            message = "Memory location index out of range.  Use an integer from 0 to 4."
            returnValue(message)
        elif value>=0 and value <=4:
            yield dev.write('*RCL '+str(value))
            error = 'none'#yield self.error(c)
            returnValue(error)

    @setting(19, 'Settings Reset', returns='s')
    def settings_reset(self, c):
        '''
        Resets the power supply to factory defined settings.

         Note that this will disable the Output.
         Equivalent to *RST
        '''
        dev = self.selectedDevice(c)
        yield dev.write('*RST')
        error = 'none'#yield self.error(c)
        returnValue(error)

    @setting(20, 'Settings Save', value = 'i', returns='s')
    def settings_save(self, c, value):
        '''
        Saves the power supply settings to 1 of 5 memory locations (index 0 to 4).

         Settings saved:  Current, Voltage, Output
         Equivalent to *SAV <value>
         Use settings_recall to recall settings.
        '''
        dev = self.selectedDevice(c)
        if value<0 or value >4:
            message = "Memory location index out of range.  Use an integer from 0 to 4."
            returnValue(message)
        elif value>=0 and value <=4:
            yield dev.write('*SAV '+str(value))
            error = 'none'#yield self.error(c)
            returnValue(error)

    @setting(21, 'Clear Status')
    def clear_status(self, c):
        '''
        Clears error statuses.

         Equivalent to *CLS
        '''
        dev = self.selectedDevice(c)
        yield dev.write('*CLS')

    @setting(22, 'Error', returns = 's')
    def error(self, c):
        '''
        Reads the error message register.

         Equivalent to SYST:ERR?
        '''
        dev = self.selectedDevice(c)
        yield dev.write('SYST:ERR?')
        error = yield dev.read()
        returnValue(error)

    @setting(23, 'Status Byte',returns = 's')
    def status_byte(self, c):
        '''
        Reads the status byte without clearing it.

         Equivalent to *STB?
        '''
        dev = self.selectedDevice(c)
        yield dev.write('*STB?')
        sleep(0.1)
        statusbyte = yield dev.read()
        self.clear_status(c)
        dict = {'+128': 'OPER: Operation status summary', '+64': 'MSS: Master status summary',
                '+32': 'ESB: Event status byte summary', '+16': 'MAV: Message Available',
                '+8': 'QUES: Questionable status summary', '+0': 'None'}
        returnValue(statusbyte+' '+dict[statusbyte])

    @setting(24, 'Self Test', returns = 's')
    def self_test(self, c):
        '''
        Instructs the power supply to conduct a self test and report errors.
        '''
        dev = self.selectedDevice(c)
        yield dev.write('*TST?')
        sleep(0.1)
        result = yield dev.read()
        self.clear_status(c)
        if float(result)==0:
            returnValue(result+' Passed')
        else:
            returnValue(result+' Failed')

    @setting(25, 'Status Oper Cond', returns = 'w')
    def status_oper_cond(self, c):
        '''
        Queries the power supply's Operation Condition register.

         Equivalent to STAT:OPER:COND?
        '''
        dev = self.selectedDevice(c)
        yield dev.write('STAT:OPER:COND?')
        sleep(0.1)
        result = yield dev.read()
        self.clear_status(c)
        dict={'+1024': 'CC: Constant Current', '+256': 'CV: Constant Voltage',
              '+32': 'WTG: Waiting for Trigger', '+0': 'None'}
        returnValue(int(result))

    @setting(26, 'Status Ques Cond', returns = 's')
    def status_ques_cond(self, c):
        '''
        Queries the power supply's Questionable Condition register.

         Equivalent to STAT:QUES:COND?
        '''
        dev = self.selectedDevice(c)
        yield dev.write('STAT:QUES:COND?')
        sleep(0.1)
        result = yield dev.read()
        self.clear_status(c)
        dict={'+1024': 'UNR: Unregulated power supply output', '+512': 'RI: Remote Inhibit Active',
              '+16': 'OT: Overtemperature', '+2': 'OC: Overcurrent',
              '+1': 'OV: Overvoltage', '+0': 'None'}
        returnValue(result+' '+dict[result])

    @setting(27, "Get Settings", returns = 's')
    def get_settings(self, c):
        '''
        Displays the measured voltage, current, and output state in one command.
        '''
        voltage = yield self.get_voltage(c)
        current = yield self.get_current(c)
        output_state = yield self.output_state(c)
        returnValue('Voltage: '+str(voltage['V'])+' V, Current: '+str(current['A'])+' A, Output: '+output_state)

    @setting(28, "CC Mode", returns = 'b')
    def cc_mode(self, c):
        operating_condition = yield self.status_oper_cond(c)
        result = '0b01000000000' and bin(operating_condition) #1024 = CC Mode
        returnValue(result==bin(1024))

    @setting(29, "CV Mode", returns = 'b')
    def cv_mode(self, c):
        operating_condition = yield self.status_oper_cond(c)
        result = '0b00100000000' and bin(operating_condition) #256 = CC Mode
        returnValue(result==bin(256))

__server__ = HP6033A_Server()

if __name__ == '__main__':
    from labrad import util
    util.runServer(__server__)
