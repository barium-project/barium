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
name = SR430 Scalar Server
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

from labrad.gpib import GPIBManagedServer, GPIBDeviceWrapper
from labrad.types import Error
from twisted.internet import reactor
from labrad.server import Signal, setting
from labrad import types as T
from twisted.internet.task import LoopingCall
from twisted.internet.defer import returnValue
from labrad.support import getNodeName
from labrad.units import WithUnit as U
from time import sleep

class SR430_Scalar_Wrapper(GPIBDeviceWrapper):
    def initialize(self):
        pass

class SR430_Scalar_Server(GPIBManagedServer):
    '''
    This server talks to the SR430 Multichannel Scalar/Averager
    '''
    name = "SR430 Scalar Server"
    deviceName = "Stanford_Research_Systems SR430"
    deviceWrapper = SR430_Scalar_Wrapper

    @setting(10, 'IDN', returns = 's')
    def idn(self, c):
        '''
        Requests the device to identify itself.
         Equivalent to *IDN?
        '''
        dev = self.selectedDevice(c)
        yield dev.write('*IDN?')
        message = yield dev.read()
        returnValue(message)

    @setting(11, 'Trigger Level', value='v[V]', returns='s')
    def trigger_level(self, c, value=None):
        '''
        Sets or queries the trigger level.
         ".trigger_level(x)" sets the trigger level to x (number with voltage unit).  Acceptable range: [U(-2.000,'V'),U(2.000,'V')]
         ".trigger_level()" queries.
         Equivalent to TRLV.
        '''
        dev = self.selectedDevice(c)
        if value==None: # Function behaves as query when given no arguments
            yield dev.write('TRLV?')
            message = yield dev.read()
            returnValue(message)
        elif value['V'] < -2.0 or value['V'] > 2.0:
            message = 'Input out of range.  Acceptable range: [U(-2.000,\'V\'),U(2.000,\'V\')]'
            returnValue(message)
        else:
            yield dev.write('TRLV '+str(value['V'])) #Converts value in volts to string
            returnValue('Success')

    @setting(12, 'Discriminator Level', value='v[V]', returns='s')
    def discriminator_level(self, c, value=None):
        '''
        Sets or queries the discriminator level.
         ".discriminator_level(x)" sets the discriminator level to x (number with voltage unit).  Acceptable range: [U(-0.300,'V'),U(0.300,'V')]
         ".discriminator_level()" queries.
         Equivalent to DCLV.
        '''
        dev = self.selectedDevice(c)
        if value==None:
            yield dev.write('DCLV?')
            message = yield dev.read()
            returnValue(message)
        else:
            if value['V'] > 0.300 or value['V'] < -0.300:
                message = "Input out of range.  Acceptable range: [-0.300,0.300]"
                returnValue(message)
            elif value['V'] <= 0.300 and value['V'] >= -0.300:
                yield dev.write('DCLV '+str(value['V']))
                returnValue('Success')

    @setting(13, 'Records Per Scan', value='w', returns='s')
    def records_per_scan(self, c, value=None):
        '''
        Sets or queries the records per scan
         ".records_per_scan(x)" sets the records per scan to x.  Acceptable range: [0,32767)U(32769,65535] (Due to the internal programming of the scalar, 32768 is not a working input.)
         ".records_per_scan()" queries.
         Equivalent to RSCN.
        '''
        dev = self.selectedDevice(c)
        if value==None:
            yield dev.write('RSCN?')
            read_rps = yield dev.read()
            if int(read_rps) < 0:           #The scalar has a bug where a number, N > 32768
                rps = int(read_rps) + 65536    #will return as N - 65536
            else:
                rps = int(read_rps)
            message = str(rps)
            returnValue(message)
        elif value == 32768:
            message = "Input out of range.  Acceptable range: [0,32767)U(32769,65535]"
        else:
            if value > 65535:
                message = "Input out of range.  Acceptable range: [0,32767)U(32769,65535]"
                returnValue(message)
            elif value <= 65535:
                yield dev.write('RSCN '+str(value))
                returnValue('Success')

    @setting(14, 'Output GPIB')
    def output_gpib(self, c):
        '''
        Sets query output to GPIB.  This is necessary so that any queries to the
         scalar will output to the GPIB port.
         Equivlanet to OUTP 1.
        '''
        dev = self.selectedDevice(c)
        yield dev.write('OUTP 1')

    @setting(15, 'Start Scan')
    def start_scan(self, c):
        '''
        Starts scan (without clearing).  Same as pressing the [START] key.
         For starting a scan with clearing, use start_new_scan().
         Equivalent to SSCN.
        '''
        dev = self.selectedDevice(c)
        yield dev.write('SSCN')

    @setting(16, 'Stop Scan')
    def stop_scan(self, c):
        '''
        Pauses a scan in progress.  Same as pressing [STOP] key.
         Equivalent to PAUS.
        '''
        dev = self.selectedDevice(c)
        yield dev.write('PAUS')

    @setting(17, 'Clear Scan')
    def clear_scan(self, c):
        '''
        Resets the unit to CLEAR state, losing all data.  Same as pressing [STOP],[STOP]
         Equivalent to CLRS
        '''
        dev = self.selectedDevice(c)
        yield dev.write('CLRS')

    @setting(18, 'Start New Scan', returns='s', wait_time='v[s]')
    def start_new_scan(self, c, wait_time):
        '''
        Clears current data and starts new scan, and pauses the program over the input wait_time to allow scan to run uninterrupted.
         ".start_new_scan(wait_time)" is the proper syntax, where wait_time is a number with time unit in seconds, i.e. U(1.0,'s').
         Uses both clear_scan() and start_scan() methods.
        '''
        if wait_time['s'] < 0 or wait_time==None:
            message = 'Input out of range.  Range: [0, Infinity)'
            returnValue(message)
        else:
            dev = self.selectedDevice(c)

            yield self.clear_scan(c)    #Clears the scan of previous data
            yield self.start_scan(c)    #Starts new scan
            sleep(wait_time['s'])
            returnValue('Success.')

    @setting(19, 'Get Counts',returns='w')
    def get_counts(self, c):
        '''
        Get counts of last run over a statistcal analysis on all bins.
         ".get_counts()" performs the count summation and returns the sum as an integer.
         SR430 commands used: LLIM, RLIM, STAT, and SPAR?2
        '''
        dev = self.selectedDevice(c)
        yield dev.write('LLIM 0')                       #Sets the left limit as bin 0
        bins_per_record = yield self.bins_per_record(c,0) #Looks up bins per record (total number of bins)
        last_bin_index = int(bins_per_record) - 1
        yield dev.write('RLIM '+str(last_bin_index))    #Lets the right limit as the total number of bins - 1 (last bin)
        yield dev.write('STAT')
        sleep(1)
        yield dev.write('SPAR?2')           #Queries for the total # of counts (SPAR?2) See Manual
        number_of_counts = yield dev.read() #Reads the buffer for total # of counts
        returnValue(int(float(number_of_counts)))  #Returns total # of counts as an integer

    @setting(20, 'Bins Per Record', value='w', returns='s')
    def bins_per_record(self, c, value=None):
        '''
        Sets or queries bins per record.
         ".bins_per_record(x)" sets the bins per record to x (nonzero positive number).
         ".bins_per_record(0)" queries.
         ".bins_per_record()" returns a list of supported arguments.  Accepts integer multiples of 1024 as arguments up to 16*1024.
         Example: "bins_per_record(1024)" sets the bins per record to 1024 steps.
         Equivalent to BREC
        '''
        dev = self.selectedDevice(c)
        argument_dictionary = {1024: 1, 2*1024: 2, 3*1024: 3, 4*1024: 4, 5*1024: 5,
                               6*1024: 6, 7*1024: 7, 8*1024: 8, 9*1024: 9, 10*1024: 10,
                                11*1024: 11, 12*1024: 12, 13*1024: 13, 14*1024: 14,
                                15*1024: 15, 16*1024: 16}
        inverted_dictionary = dict([[v,k] for k,v in argument_dictionary.items()])
        supported_arguments = argument_dictionary.keys()            #Defines an array with dictionary keys
        if value==None:
            message = 'Supported arguments: '+str(supported_arguments)
            returnValue(message)
        elif value==0:
            yield dev.write('BREC?')
            bit = yield dev.read()                 #Reads in bit
            message = str(inverted_dictionary[int(bit)]) #Uses dictionary to convert bit to number of bins per record value
            returnValue(message)
        elif value in supported_arguments:
            yield dev.write('BREC '+str(argument_dictionary[value]))  #Uses dictionary to look up the input value's corresponding bit
            returnValue('Success')
        else:
            message = 'Unsupported argument. Supported arguments: '+str(supported_arguments)
            returnValue(message)

    @setting(21, 'Bin Width', value='w', returns='s')
    def bin_width(self, c, value=None):
        '''
        Sets or queries bin width (unsigned integervalue representing bin width in ns)
         ".bin_width(x)" sets the bin width to x (nonzero positive number).
         ".bin_width(0)" queries.
         ".bin_width()" returns a list of supported arguments.  Supported arguments: [5,40,80,160,320,640,1280,2560,5120,10240,20480,40960,81920,163840,327680,655360,1310700,2621400,5242900,1048600]
         Example: "bin_width(5)" sets the bin width to 5 ns.
         Equivalent to BWTH
        '''
        dev = self.selectedDevice(c)
        argument_dictionary = {5: 0,40: 1,80: 2,160: 3,320: 4,640: 5,1280: 6,2560: 7, 5120: 8,      #Defines dictionary
                               10240: 9, 20480: 10, 40960: 11, 81920: 12, 163840: 13, 327680: 14,
                               655360: 15, 1310720: 16, 2621400: 17, 5242900: 18, 10486000: 19}
        inverted_dictionary = dict([[v,k] for k,v in argument_dictionary.items()])
        supported_arguments = argument_dictionary.keys()            #Defines array with dictionary keys

        if value==None:
            message = 'Supported arguments: '+str(supported_arguments)
            returnValue(message)
        elif value==0:
            yield dev.write('BWTH?')
            bit = yield dev.read()            #Reads in bit
            message = str(inverted_dictionary[int(bit)])+' ns' #Uses dictionary to convert bit to width value
            returnValue(message)
        elif value in supported_arguments:
            yield dev.write('BWTH '+str(argument_dictionary[value]))        #Converts value to corresponding bit
            returnValue('Success')
        else:
            message = 'Unsupported argument.  Supported arguments: '+str(supported_arguments)
            returnValue(message)

    @setting(23, 'Clear Status')
    def clear_status(self, c):
        '''
        Clears all status registers.
         Equivalent to *CLS
        '''
        dev = self.selectedDevice(c)
        yield dev.write('*CLS')

    @setting(24, 'Error', returns='s')
    def error(self, c):
        '''
        Reads and reports standard event errors.
         Equivalent to ESE?
        '''
        dev = self.selectedDevice(c)
        yield dev.write('ESE?0')
        input_error = yield dev.read()
        yield dev.write('ESE?2')
        query_error = yield dev.read()
        yield dev.write('ESE?4')
        execution_error = yield dev.read()
        yield dev.write('ESE?5')
        command_error = yield dev.read()
        yield dev.write('ESE?6')
        URQ = yield dev.read()
        yield dev.write('ESE?7')
        PON = yield dev.read()
        if input_error==0 and query_error==0 and execution_error==0 and command_error==0 and URQ ==0 and PON ==0:
            message = 'No error.'
        else:
            message = ('Error bytes:  Input Error '+input_error+'; Query Error '+
                        query_error+'; Execution Error '+execution_error+
                        '; Command Error '+command_error+'; URQ '+URQ+'; PON '+PON)
        returnValue(message)

__server__ = SR430_Scalar_Server()

if __name__ == "__main__":
    from labrad import util
    util.runServer(__server__)
