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
         1 argument sets.  No arguments queries.
         Acceptable range: [-2.000,2.000]
         Equivalent to TRLV.
        '''
        dev = self.selectedDevice(c)
        if value==None: # Function behaves as query when given no arguments
            yield dev.write('TRLV?')
            message = yield dev.read()
            returnValue(message)
        elif value > 2 or value < 2:
            message = 'Input out of range.  Acceptable range: [-2.000,2.000]'
            returnValue(message)
        else:
            yield dev.write('TRLV '+str(value['V'])) #Converts value in volts to string

    @setting(12, 'Discriminator Level', value='v[V]', returns='s')
    def discriminator_level(self, c, value=None):
        '''
        Sets or queries the discriminator level.
         1 argument sets.  No arguments queries.
         Acceptable range: [-0.300,0.300]
         Equivalent to DCLV.
        '''
        dev = self.selectedDevice(c)
        if value==None:
            yield dev.write('DCLV?')
            message = yield dev.read()
            returnValue(message)
        else:
            yield dev.write('DCLV '+str(value['V']))

    @setting(13, 'Records Per Scan', value='w', returns='s')
    def records_per_scan(self, c, value=None):
        '''
        Sets or queries the records per scan
         1 argument sets.  No arguments queries.
         Acceptable range: [0,65535]
         Equivalent to RSCN.
        '''
        dev = self.selectedDevice(c)
        if value==None:
            yield dev.write('RSCN?')
            message = yield dev.read()
            returnValue(message)
        elif value > 65535:
            message = "Input out of range.  Acceptable range: [0,65535]"
            returnValue(message)
        else:
            yield dev.write('RSCN '+str(value))

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

    @setting(18, 'Start New Scan', returns='s')
    def start_new_scan(self, c):
        '''
        Clears current data and starts new scan.
         The time of scan is calculated using (bins per record) * (bin width).
         Uses both clear_scan() and start_scan() methods.
        '''
        if duration < 0:
            message = 'Input out of range.  Range: [0, Infinity)'
            returnValue(message)
        else:
            dev = self.selectedDevice(c)
            
            bins_per_record = yield self.bins_per_record(0)     #Looks up bins per record
            bin_width = yield self.bin_width(0)                 #Looks up bin width (time duration)
            counting_wait_time = bins_per_record*bin_width*1e9  #Total scan time = bpr*bwidth
            
            yield self.clear_scan(c)    #Clears the scan of previous data
            yield self.start_scan(c)    #Starts new scan
            sleep(counting_wait_time)

    @setting(19, 'Statistics',returns='w')
    def statistics(self, c):
        '''
        Performs statistics.
         First the left limit is set to 0 and the right limit is set to the last bin (based on bins per record).
         Then statistics are done on this range, which is basically all of the bins, with a wait time of 1s.
         Then the number of counts is returned as an integer.

         SR430 commands used: LLIM, RLIM, STAT, and SPAR?2
        '''
        dev = self.selectedDevice(c)
        yield dev.write('LLIM 0')                       #Sets the left limit as bin 0
        bins_per_record = yield self.bins_per_record(0) #Looks up bins per record (total number of bins)
        last_bin_index = bins_per_record - 1
        yield dev.write('RLIM '+str(last_bin_index))    #Lets the right limit as the total number of bins - 1 (last bin)
        yield dev.write('STAT')
        sleep(1)
        yield dev.write('SPAR?2')           #Queries for the total # of counts (SPAR?2) See Manual
        number_of_counts = yield dev.read() #Reads the buffer for total # of counts
        returnValue(int(number_of_counts))  #Returns total # of counts as an integer

    @setting(20, 'Bins Per Record', value='w', returns='s')
    def bins_per_record(self, c, value=None):
        '''
        Sets or queries bins per record.
         1 argument (with value!=0) sets.
         1 argument (with value=0) queries.
         No arguments returns a list of supported arguments.
         Accepts integer multiples of 1024 as arguments up to 16*1024.
         Example: bins_per_record(1024) sets the bins per record to 1024 steps.
        
         Equivalent to BREC
        '''
        dev = self.selectedDevice(c)
        supported_arguments = [1024,2*1024,3*1024,4*1024,5*1024,
                               6*1024,7*1024,8*1024,9*1024,10*1024,
                               11*1024,12*1024,13*1024,14*1024,15*1024,
                               16*1024]
        if value==None:
            message = 'Supported arguments: '+str(supported_arguments)
            returnValue(message)
        elif value==0:
            yield dev.write('BREC?')
            message = yield dev.read()
            returnValue(message)
        elif value in supported_arguments:
            yield dev.write('BREC '+str(value))
        else:
            message = 'Unsupported argument. Supported arguments: '+str(supported_arguments)
            returnValue(message)

    @setting(21, 'Bin Width', value='w', returns='s')
    def bin_width(self, c, value=None):
        '''
        Sets or queries bin width (unsigned integervalue representing bin width in ns)
         1 argument (with value!=0) sets.
         1 argument (with value=0) queries.
         No arguments returns a list of supported arguments.
         Supported arguments: [5,40,80,160,320,640,1280,2560,5120,
                               10240,20480,40960,81920,163840,327680,
                               655360,1310700,2621400,5242900,1048600]
         Example: bin_width(5) sets the bin width to 5 ns.

         Equivalent to BWTH
        '''
        dev = self.selectedDevice(c)
        supported_arguments = [5,40,80,160,320,640,1280,2560,5120,
                               10240,20480,40960,81920,163840,327680,
                               655360,1310700,2621400,5242900,1048600]
        if value==None:
            message = 'Supported arguments: '+str(supported_arguments)
            returnValue(message)
        elif value==0:
            yield dev.write('BWTH?')
            message = yield dev.read()
            returnValue(message)
        elif value in supported_arguments:
            yield dev.write('BWTH '+str(value))
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
        yield dev.write('ESE? 0')
        input_error = yield dev.read()
        yield dev.write('ESE? 2')
        query_error = yield dev.read()
        yield dev.write('ESE? 4')
        execution_error = yield dev.read()
        yield dev.write('ESE? 5')
        command_error = yield dev.read()
        yield dev.write('ESE? 6')
        URQ = yield dev.read()
        yield dev.write('ESE? 7')
        PON = yield dev.read()
        if input_error==0 and query_error==0 and execution_error==0 and command_error==0 and URQ ==0 and PON ==0:
            message = 'No error.'
        else:
            message = ('Error bytes:  Input Error '+input_error+'; Query Error '+
                        query_error+'; Execution Error '+execution_error+
                        '; Command Error '+command_error+'; URQ '+URQ+'; PON '+PON)
        returnValue(message)



if __name__ == "__main__":
    from labrad import util
    util.runServer(SR430_Scalar_Server())
            



    
