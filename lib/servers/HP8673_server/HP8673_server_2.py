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
# along with this program.  If not, see <http://www.gnu.org/licenses/>

"""
### BEGIN NODE INFO
[info]
name = HP8673Server2
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


class HP8673Wrapper(GPIBDeviceWrapper):
    def initialize(self):
        pass



class HP8673_Server2(GPIBManagedServer):
    """
    This server talks to the HP8673 Microwave Signal Generator.

    """
    name = 'HP8673Server2'
    deviceName = 'FR09000000000HZ'
    deviceIdentFunc = 'identify_device'
    #deviceManager = 'GPIB Device Manager'
    deviceWrapper = HP8673Wrapper

    def __init__(self):
        super(HP8673_Server2, self).__init__()

    @setting(100, server='s', address='s', response = 's')
    def identify_device(self, c, server, address, response):
        """
        The HP8673 does not return a standard messeage to *IDN?. Because of this, an identification
        function needs to be used. There are two types of generic identification functions, see the
        register_ident_funct in the gpib manager file. The gpbi device manager will run through
        each identification function it knows about to try and find one that can properly identify
        the device. The manager will error if you connect the device before running the server (sill not
        sure why), even if you refresh the device list. This is because the ident function is not known
        before the server starts, so the manager doens't know how to handle the response. I would think
        that after starting the server and refreshing it would work, but doens't seem like it.
        So.... just start all the servers before turning on the GPIB devices with non-standard responses,
        refresh the device list, and everything will connect accordingly.
        """
        yield None
        returnValue(self.deviceName)



    # HP8673 Settings
    @setting(201, amplitude='v[dBm]')
    def set_amplitude(self, c, amplitude):
        """Sets the amplitude output range and vernier in units of dBm.
        Must be between [-100, +13] dBm
        """


        amp = amplitude['dBm']
        if amp < -100 or amp > 13:
            print 'Error: amplitude must be between -100 and 13.'
        else:
            dev = self.selectedDevice(c)
            yield dev.write("AP"+str(amp)+"DM\r\n")


    @setting(205, value='v[GHz]')
    def set_frequency(self, c, value):
        """Sets the frequency of the signal generator.  Uses units of frequency (i.e. GHz).
        """
        dev = self.selectedDevice(c)
        if value['GHz'] > 18 or value['GHz'] < 2:
            print "Value out of range.  Acceptable range: [2 GHz, 18 GHz]"
        # Need to make sure the number has the 10GHz digit (even zero) and
        # only has ten total digits
        else:
            value = value['MHz']
            #value = int(value*1e8)/1.e8
            #value = '%.8f' % value
            yield dev.write("FR"+str(value)+"MZ\r\n")


    @setting(224, value='b')
    def RF_state(self, c, value):
        """Turns the RF state on or off.
        """
        dev = self.selectedDevice(c)
        if value:
            yield dev.write("RF1\r\n")
        elif not value:
            yield dev.write("RF0\r\n")



__server__ = HP8673_Server2()

if __name__ == '__main__':
    from labrad import util
    util.runServer(__server__)
