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
name = HP8673 Server
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



class HP8673_Server(GPIBManagedServer):
    """
    This server talks to the HP8673 Microwave Signal Generator.

    Since the HP8673 does not have talk capability, it will not respond to a *IDN?
    query and therefore will not provide a device name.  Instead, we use the deviceIdentFunc
    option which returns 'Generic GPIB Device' as the name, so that the GPIB Device Manager
    will map any devices that do not respond to *IDN? to this generic device name.
    """
    name = 'HP8673Server'
    deviceName = 'FR00000000000HZ'
    deviceIdentFunc = 'identify_device'
    deviceManager = 'GPIB Device Manager'
    deviceWrapper = HP8673Wrapper

    def __init__(self):
        super(HP8673_Server, self).__init__()

    @setting(100, server='s', address='s', response = 's')
    def identify_device(self, c, server, address, response):
        """
        Since the HP8673 does not have talk capability, it does not respond to *IDN? requests.
        Therefore, I've set the deviceName to 'Generic GPIB Device' to allow the HP8673 to be seen
        by this server.  This could also mean devices other than the HP8673 are seen by this server
        as well.
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



__server__ = HP8673_Server()

if __name__ == '__main__':
    from labrad import util
    util.runServer(__server__)
