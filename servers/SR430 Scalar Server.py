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
        sleep(0.1)
        message = yield dev.read()
        returnValue(message)

    @setting(11, 'Trigger Level', value='v[V]', returns='s')
    def trigger_level(self, c, value=None):
        '''
        Sets the trigger level.

         Equivalent to TRLV.
        '''
        dev = self.selectedDevice(c)
        if value==None: # Function behaves as query when given no arguments
            yield dev.write('TRLV?')
            sleep(0.1)
            message = yield dev.read()
            returnValue(message)
        else:
            yield dev.write('TRLV '+str(value['V'])) #Converts value in volts to string

    @setting(12, 'Discriminator Level', value='v[V]', returns='s')
    def discriminator_level(self, c, value=None):
        '''
        Sets or queries the discriminator level.
         Acceptable range: [-0.300,0.300]
         Equivalent to DCLV.
        '''
        dev = self.selectedDevice(c)
        if value==None:
            yield dev.write('DCLV?')
            sleep(0.1)
            message = yield dev.read()
            returnValue(message)
        else:
            yield dev.write('DCLV '+str(value['V']))

    @setting(13, 'Records Per Scan', value='w', returns='s')
    def records_per_scan(self, c, value=None):
        '''
        Sets or queries the records per scan
         Acceptable range: [0,65535]
         Equivalent to RSCN.
        '''
        dev = self.selectedDevice(c)
        if value==None:
            yield dev.write('RSCN?')
            sleep(0.1)
            message = yield dev.read()
            returnValue(message)
        elif value > 65535:
            message = "Input out of range.  Acceptable range: [0,65535]
            returnValue(message)
        else:
            yield dev.write('RSCN '+str(value))

    @setting(14, 'Output GPIB')
    def output_gpib(self, c):
        '''
        Sets query output to GPIB
         
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

    @setting(18, 'Start New Scan')
    def start_new_scan(self, c):
        '''
        Clears current data and starts new scan.
         Uses both clear_scan() and start_scan() methods.
        '''
        dev = self.selectedDevice(c)
        yield self.clear_scan(c)
        sleep(0.01)
        yield self.start_scan(c)

    @setting(19, 'Statistics')
    def statistics(self, c):
        '''
        Performs statistics.

         Equivalent to STAT
        '''
        dev = self.selectedDevice(c)
        yield dev.write('STAT')

    @setting(20, 'Bins Per Record', value='w', returns='s')
    def bins_per_record(self, c, value=None):
        '''
        Sets or queries bins per record.
         1 argumements sets.  0 arguments queries.

         Equivlanet to BREC
        '''
        dev = self.selectedDevice(c)
        if value==None:
            yield dev.write('BREC?')
            sleep(0.1)
            message = yield dev.read()
            returnValue(message)
        elif value==0 or value>16:
            message = 'Input out of range.  Acceptable range: [0,16]'
            returnValue(message)
        else:
            yield dev.write('BREC '+str(value))

    @setting(21, 'Bin Width', value='w', returns='s')
    def bin_width(self, c, value=None):
        '''
        Sets or queries bin width
         1 argument sets.  0 arguments queries.

         Equivalent to BWTH
        '''
        dev = self.selectedDevice(c)
        if value==None:
            yield dev.write('BWTH?')
            sleep(0.1)
            message = yield dev.read()
            returnValue(message)
        elif value > 19:
            message = 'Input out of range.  Acceptable range: [0,19]'
            returnValue(message)
        else:
            yield dev.write('BWTH '+str(value))

    @setting(22, 'Reset')
    def reset(self, c):
        '''
        Reset to default configurations.

         Equivalent to *RST
        '''
        dev = self.selectedDevice(c)
        yield dev.write('*RST')

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
        Reads and reports erros.
        0 Plot Error;  1 Print Error;  2 Memory Error; 3 Disk Error;
        4 Unused;  5 Clock Unlock;  6 Rate Error;  7 Overflow

         Equivalent to ERRS?
        '''
        dev = self.selectedDevice(c)
        yield dev.write('ERRS?')
        sleep(0.1)
        message = yield dev.read()
        returnValue(message)



if __name__ == "__main__":
    from labard import util
    util.runServer(SR430_Scalar_server())
            



    
