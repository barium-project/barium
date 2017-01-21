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
name = HP8657B Server
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



class HP8675BWrapper(GPIBDeviceWrapper):
    def initialize(self):
        pass

class HP8657B_Server(GPIBManagedServer):
    """
    This server talks to the HP8657B Microwave Signal Generator.

    Since the HP8657B does not have talk capability, it will not respond to a *IDN?
    query and therefore will not provide a device name.  Instead, we use the deviceIdentFunc
    option which returns 'Generic GPIB Device' as the name, so that the GPIB Device Manager
    will map any devices that do not respond to *IDN? to this generic device name.
    """
    name = 'HP8657B Server'
    deviceName = 'Generic GPIB Device'
    deviceIdentFunc = 'identify_device'
    deviceWrapper = HP8675BWrapper

    def __init__(self):
        super(HP8657B_Server, self).__init__()


    @setting(100, server='s', address='s')
    def identify_device(self, c, server, address):
        """
        Since the HP8657B does not have talk capability, it does not respond to *IDN? requests.
        Therefore, I've set the deviceName to 'Generic GPIB Device' to allow the HP8657B to be seen
        by this server.  This could also mean devices other than the HP8657B are seen by this server
        as well.
        """
        yield None
        returnValue(self.deviceName)

    @setting(201, value='v[dBm]')
    def set_amplitude(self, c, value):
        """Sets the amplitude of the signal generator.  Uses units of dBm.
        """
        dev = self.selectedDevice(c)
        if value['dBm'] < -143.5 or value['dBm'] > 13:
            print "Out of range.  Acceptable range: [-143.5 dBm, 13 dBm]"
        else:
            dev.write("AP "+str(value['dBm'])+" DM")
        yield None

    @setting(202, value='v[dB]')
    def amplitude_offset(self, c, value):
        dev = self.selectedDevice(c)
        dev.write("AO "+str(value['dB'])+" DB")
        yield None

    @setting(203, value='s')
    def amplitude_modulation_step(self, c, value):
        dev = self.selectedDevice(c)
        if value.lower() != 'up' and value.lower() != 'down':
            print "Bad input.  Acceptable inputs are the strings \'up\' and \'down\'."
        elif value.lower() == 'up':
            dev.write("AM UP")
        elif value.lower() == 'down':
            dev.write("AM DN")
        yield None

    @setting(204, value='v[dB]')
    def amplitude_modulation_increment(self, c, value):
        dev = self.selectedDevice(c)
        dev.write("AM IS "+str(value['dB'])+" DB")
        yield None

    @setting(205, value='v[MHz]')
    def set_frequency(self, c, value):
        """Sets the frequency of the signal generator.  Uses units of frequency (i.e. MHz).
        """
        dev = self.selectedDevice(c)
        if value['MHz'] > 2060 or value['MHz'] < 0:
            print "Value out of range.  Acceptable range: [0 MHz, 2060 MHz]"
        dev.write("FR "+str(value['MHz'])+" MZ")
        yield None

    @setting(206, value='s')
    def frequency_modulation_step(self, c, value):
        dev = self.selectedDevice(c)
        if value.lower() != 'up' and value.lower() != 'down':
            print "Bad input.  Acceptable inputs are the strings \'up\' and \'down\'."
        elif value.lower() == 'up':
            dev.write("FM UP")
        elif value.lower() == 'down':
            dev.write("FM DN")
        yield None

    @setting(207, value='v[MHz]')
    def frequency_modulation_increment(self, c, value):
        dev = self.selectedDevice(c)
        dev.write("FM IS "+str(value['MHz'])+" MZ")
        yield None

    @setting(208, value='s')
    def phase_step(self, c, value):
        dev = self.selectedDevice(c)
        if value.lower() != 'up' and value.lower() != 'down':
            print "Bad input.  Acceptable inputs are the strings \'up\' and \'down\'."
        elif value.lower() == 'up':
            dev.write("PI")
        elif value.lower() == 'down':
            dev.write("PD")
        yield None

    @setting(209, value='w')
    def recall(self, c, value):
        """Recalls settings from a memory location [0,99].
        """
        dev = self.selectedDevice(c)
        if value < 10:
            dev.write("RC 0"+str(value))
        elif value > 9 and value < 100:
            dev.write("RC "+str(value))
        else:
            print "Value out of range.  Acceptable range: Integers in [0,99]"
        yield None

    @setting(210, value='w')
    def save(self, c, value):
        """Saves settings to a memory location [0,99].
        """
        dev = self.selectedDevice(c)
        if value < 10:
            dev.write("SV 0"+str(value))
        elif value > 9 and value < 100:
            dev.write("SV "+str(value))
        else:
            print "Value out of range.  Acceptable range: Integers in [0,99]"
        yield None

    @setting(211, value='w')
    def select_external_AM(self, c, value):
        dev = self.selectedDevice(c)
        if value >= 0 and value <= 100:
            dev.write("S1 AM "+str(value)+" %")
        else:
            print "Input out of range.  Acceptable range: Integers in [0,100]"
        yield None

    @setting(212, value='v[kHz]')
    def select_external_FM(self, c, value):
        dev = self.selectedDevice(c)
        dev.write("S1 FM "+str(value)+" KZ")
        yield None

    @setting(213, value='w')
    def select_internal_400_AM(self, c, value):
        dev = self.selectedDevice(c)
        if value >= 0 and value <= 100:
            dev.write("S2 AM "+str(value)+" %")
        else:
            print "Input out of range.  Acceptable range: Integers in [0,100]"
        yield None

    @setting(214, value='v[kHz]')
    def select_internal_400_FM(self, c, value):
        dev = self.selectedDevice(c)
        dev.write("S2 FM "+str(value)+" KZ")
        yield None

    @setting(215, value='w')
    def select_internal_1000_AM(self, c, value):
        dev = self.selectedDevice(c)
        if value >= 0 and value <= 100:
            dev.write("S3 AM "+str(value)+" %")
        else:
            print "Input out of range.  Acceptable range: Integers in [0,100]"
        yield None

    @setting(216, value='v[kHz]')
    def select_internal_1000_FM(self, c, value):
        dev = self.selectedDevice(c)
        dev.write("S3 FM "+str(value)+" KZ")
        yield None

    @setting(217, value='v[kHz]')
    def select_DC_FM(self, c, value):
        dev = self.selectedDevice(c)
        dev.write("S5 FM "+str(value)+" KZ")
        yield None

    @setting(218, value='s')
    def shutoff_external(self, c, value):
        dev = self.selectedDevice(c)
        if value.upper == "AM":
            dev.write("AM S1 S4")
        elif value.upper == "FM":
            dev.write("FM S1 S4")
        else:
            print "Please enter modulation string 'AM' or 'FM' as an argument."
        yield None

    @setting(219, value='s')
    def shutoff_internal_400(self, c, value):
        dev = self.selectedDevice(c)
        if value.upper == "AM":
            dev.write("AM S2 S4")
        elif value.upper == "FM":
            dev.write("FM S2 S4")
        else:
            print "Please enter modulation string 'AM' or 'FM' as an argument."
        yield None

    @setting(220, value='s')
    def shutoff_internal_1000(self, c, value):
        dev = self.selectedDevice(c)
        if value.upper == "AM":
            dev.write("AM S3 S4")
        elif value.upper == "FM":
            dev.write("FM S3 S4")
        else:
            print "Please enter modulation string 'AM' or 'FM' as an argument."
        yield None

    @setting(221)
    def shutoff_DC_FM(self, c):
        dev = self.selectedDevice(c)
        dev.write("AM S5 S4")
        yield None

    @setting(222)
    def shutoff_AM(self, c):
        dev = self.selectedDevice(c)
        dev.write("AM S4")
        yield None

    @setting(223)
    def shutoff_FM(self, c):
        dev = self.selectedDevice(c)
        dev.write("FM 4")
        yield None

    @setting(224, value='b')
    def RF_state(self, c, value):
        """Turns the RF state on or off.
        """
        dev = self.selectedDevice(c)
        if value:
            dev.write("R3")
        elif not value:
            dev.write("R2")
        yield None

    @setting(225, value='b')
    def standby_state(self, c, value):
        """Changes the device's standby state.
        .standby_state(True) puts the device on standby.
        .standby_state(False) wakes the deice from standby.
        """
        dev = self.selectedDevice(c)
        if value:
            dev.write("R0")
        elif not value:
            dev.write("R1")
        yield None

__server__ = HP8657B_Server()

if __name__ == '__main__':
    from labrad import util
    util.runServer(__server__)
