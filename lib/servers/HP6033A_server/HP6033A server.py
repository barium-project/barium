from labrad.gpib import GPIBManagedServer, GPIBDeviceWrapper
from labrad.types import Error
from twisted.internet import reactor
from labrad.server import Signal, setting
from labrad import types as T
from twisted.internet.task import LoopingCall
from twisted.internet.defer import returnValue
from labrad.support import getNodeName
from labrad.units import WithUnit as U
from labrad import units
import time

#SERVERNAME = 'HP6033AServer'
"""
### BEGIN NODE INFO
[info]
name = HP6033AServer
version = 0.2.1
description = Talks to HP 6033A Power Supply

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

class HP6033A_Wrapper(GPIBDeviceWrapper):   #This is the server wrapper.  By default, GPIBDeviceWrapper contains .read() and .write() functions.
    def initialize(self):
        pass #Edit this function as needed.

class HP6033A_Server(GPIBManagedServer):
    '''
    This server talks to the HP 6033A Power Supply.  Refer to the individual functions for their descriptions.

     Important:  Make sure the power supply's system language is set to TMSL or this server will not work!
     Write 'SYST:LANG TMSL' to change the language (i.e. gpib_write('SYST:LANG TMSL'))
     Then you will also need to set the secondary address to --- (null).  To do so [Operating Manual pg. 86],
         1) Press and hold the LCL button until the secondary address is displayed.
         2) Turn the RPG while the secondary address is being displayed to change the secondary address.
    '''
    name = 'HP6033A Server'
    deviceName = 'HEWLETT-PACKARD 6033A'
    deviceWrapper = HP6033A_Wrapper     #This line designates a wrapper for the server.

    @setting(10, 'Get VOLTage' , returns = 'v[V]')
    def get_voltage(self, c):
        '''
        Measures the voltage on the power supply and returns a value with unit V.
        
         Equivalent to MEAS:VOLT?
        '''
        dev = self.selectedDevice(c)    #This line allows .read() and .write() to be called from the GPIBDeviceWrapper
        yield dev.write('MEAS:VOLT?')
        time.sleep(0.1)
        voltage = yield dev.read()      #dev.read() returns a string
        voltage = U(float(voltage),'V') #convert string to float with units
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
        time.sleep(0.1)
        current = yield dev.read()
        current = U(float(current),'A') #convert string to float with units
        self.clear_status(c)
        returnValue(current)

    @setting(994, 'Pulse Voltage', value = 'v[V]', duration = 'v[s]', returns='s')
    def pulse_voltage(self, c, value, duration):
        '''
        Instructs the power supply to output a square pulse at a desired voltage [Volts] for a desired duration [seconds].
        
         Be sure to first initialize the voltage to 0 V.
        '''
        dev = self.selectedDevice(c)
        if value['V'] > 20 or value['V'] < 0:
            message = "Input voltage, "+str(value['V'])+" V, out of range.  (Range: 0-20 V)"
            returnValue(message)
        else:
            yield dev.write('VOLT '+str(value['V'])+' V')    #sets the voltage to value
            print "Pulsing "+str(value['V'])+" V over "+str(duration['s'])+" s..."
            time.sleep(duration['s'])                   #waits for the duration
            yield dev.write('VOLT 0 V')                 #sets the voltage back to 0
            print "Finished pulsing."
            error = yield self.error(c) #Calls the .error() method to read the error message register
            returnValue(error)          #Returns the message to the user. '+0, "No error"' means no error.

    @setting(998, 'Pulse Current', value = 'v[A]', duration = 'v[s]', returns='s')
    def pulse_current(self, c, value, duration):
        '''
        Instructs the power supply to output a square pulse at a desired current [Amps] for a desired duration [seconds].
        
         Be sure to first initialize the current to 0 A.
        '''
        dev = self.selectedDevice(c)
        if value['A'] > 30 or value['A'] < 0:
            message = "Input current, "+str(value['A'])+" A, out of range.  (Range: 0-30 A)"
            returnValue(message)
        else:
            yield dev.write('CURR '+str(value['A'])+' A')
            print "Pulsing "+str(value['A'])+" A over "+str(duration['s'])+" s..."
            time.sleep(duration['s'])
            yield dev.write('CURR 0 A')
            print "Finished pulsing."
            error = yield self.error(c)
            returnValue(error)

    @setting(13, 'Set Current', value = 'v[A]', returns='s')
    def set_current(self, c, value):
        '''
        Sets the immediate current on the power supply.
        
         The immediate current is the current programmed for the output terminals.
         Equivalent to CURR <value> <units>
        '''
        dev = self.selectedDevice(c)
        if value['A'] > 30 or value['A'] < 0:
            message = "Input current, "+str(value['A'])+" A, out of range.  (Range: 0-30 A)"
            returnValue(message)
        else:
            yield dev.write('CURR '+str(value['A'])+' A')
            error = yield self.error(c)
            returnValue(error)

    @setting(14, 'Set Voltage', value = 'v[V]', returns='s')
    def set_voltage(self, c, value):
        '''
        Sets the immediate voltage on the power supply.
        
         The immediate voltage is the voltage programmed for the output terminals.
         Equivlanet to VOLT <value> <units>
        '''
        dev = self.selectedDevice(c)
        if value['V'] > 20 or value['V'] < 0:
            message = "Input voltage, "+str(value['V'])+" V, out of range.  (Range: 0-20 V)"
            returnValue(message)
        else:
            yield dev.write('VOLT '+str(value['V'])+' V')
            error = yield self.error(c)
            returnValue(error)

    @setting(15, 'Output State', value = 'b', returns = 's')
    def output_state(self, c, value=None):#Overloaded Function
        '''
        Passing a boolean value (True or False, case sensitive) sets on/off state of the output on the power supply.
        
         Equivalent to OUTP <0/1>
         Passing no arguments will query the power supply for its state.
         Equivalent to OUTP:STAT?
        '''
        dev = self.selectedDevice(c)
        if value==None:                     #This is the behavior if no input is given
            yield dev.write('OUTP:STAT?')
            time.sleep(0.1)
            state = yield dev.read()
            self.clear_status(c)
            returnValue(state)
        else:                               #This is the behavior if input is given
            if value == True:
                 bit = 1
            elif value == False:
                 bit = 0
            yield dev.write('OUTP '+str(bit))
            error = yield self.error(c)
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
        error = yield self.error(c)
        returnValue(error)
             
    @setting(17, 'IDN', returns = 's')
    def idn(self, c):
        '''
        Requests the device identify itself.
        
         Equivalent to *IDN?
        '''
        dev = self.selectedDevice(c)
        yield dev.write('*IDN?')
        time.sleep(0.5)
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
            error = yield self.error(c)
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
        error = yield self.error(c)
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
            error = yield self.error(c)
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
        time.sleep(0.1)
        error = yield dev.read()
        if error == '+0,"No error"':
            returnValue('No error.')
        else:
            returnValue('Error Message: '+error)

    @setting(23, 'Status Byte',returns = 's')
    def status_byte(self, c):
        '''
        Reads the status byte without clearing it.
        
         Equivalent to *STB?
        '''
        dev = self.selectedDevice(c)
        yield dev.write('*STB?')
        time.sleep(0.1)
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
        time.sleep(0.1)
        result = yield dev.read()
        self.clear_status(c)
        if float(result)==0:
            returnValue(result+' Passed')
        else:
            returnValue(result+' Failed')

    @setting(25, 'Status Oper Cond', returns = 's')
    def status_oper_cond(self, c):
        '''
        Queries the power supply's Operation Condition register.

         Equivalent to STAT:OPER:COND?
        '''
        dev = self.selectedDevice(c)
        yield dev.write('STAT:OPER:COND?')
        time.sleep(0.1)
        result = yield dev.read()
        self.clear_status(c)
        dict={'+1024': 'CC: Constant Current', '+256': 'CV: Constant Voltage',
              '+32': 'WTG: Waiting for Trigger', '+0': 'None'}
        returnValue(result+' '+dict[result])

    @setting(26, 'Status Ques Cond', returns = 's')
    def status_ques_cond(self, c):
        '''
        Queries the power supply's Questionable Condition register.
        
         Equivalent to STAT:QUES:COND?
        '''
        dev = self.selectedDevice(c)
        yield dev.write('STAT:QUES:COND?')
        time.sleep(0.1)
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

if __name__ == "__main__":
    from labrad import util
    util.runServer(HP6033A_Server())
