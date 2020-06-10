"""
### BEGIN NODE INFO
[info]
name = Software Laser Lock Server
version = 1.0
description =
instancename = Software Laser Lock Server

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

from twisted.internet.defer import returnValue
import os
import time
from labrad.server import LabradServer, setting
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import LoopingCall
from twisted.internet import reactor
import socket
from config.multiplexerclient_config import multiplexer_config
from labrad.units import WithUnit as U

class Software_Laser_Lock_Server(LabradServer):

    name = 'Software Laser Lock Server'

    def initServer(self):
        self.password = os.environ['LABRADPASSWORD']
        self.name = socket.gethostname() + ' Software Laser Lock Server'
        self.lasers = {}
        self.timer = 0.1
        #self.lc = LoopingCall(self.loop)
        self.connect()

    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync(multiplexer_config.ip,
                                      name=self.name,
                                      password=self.password)
        self.trap_cxn = yield connectAsync('bender',
                                      name=self.name,
                                      password=self.password)
        self.wm = self.cxn.multiplexerserver
        self.trap = self.trap_cxn.trapserver

        #self.bristol = self.trap_cxn.bristolserver
        self.piezo = self.trap_cxn.piezo_controller

        self.reg = self.trap_cxn.registry
        self.set_up_channels()


    @inlineCallbacks
    def set_up_channels(self):
        """
        Laser locking parameters are stored in the registry. The registry must contain
        a key called 'lasers', which is a list of the keys for each set of laser
        parameters. i.e. lasers = ['455nm','585nm'], where '455nm' is a registry key
        which identifies a list of the laser locking parameters for the 455nm laser:
        (lock frequency (THz), Multiplexer Channel, display_location (column,row), gain,
        DAC Channel (0 unassigned)), Rail Volatages [low,high], locked, output voltage)
        """

        yield self.reg.cd(['Servers','software_laser_lock'])
        lasers_to_lock = yield self.reg.get('lasers')
        for chan in lasers_to_lock:
            self.lasers[chan] = yield self.reg.get(chan)
            self.lasers[chan] = list(self.lasers[chan])
        
        #self.lc.start(self.timer)
        self.loop_server()
    @inlineCallbacks
    def loop(self):
        for laser in self.lasers:
            if self.lasers[laser][6]:# == True and self.lasers[laser][4] != 4:
                # Get the frequency
                freq = yield self.wm.get_frequency(self.lasers[laser][1])
                # Make sure we didn't get some erroneous reading and throw the lock
                if (freq < self.lasers[laser][0]) + .1 and freq > (self.lasers[laser][0] -.1):
                    error = (self.lasers[laser][0] - freq)*1e6 # gives me diff in MHz
                    # Multiply error by the gain and add the previous output
                    output = error*self.lasers[laser][3]  + self.lasers[laser][7]
                    # Check against the rails
                    if output >= float(self.lasers[laser][5][1]):
                        output = float(self.lasers[laser][5][1])
                    elif output <= float(self.lasers[laser][5][0]):
                        output = float(self.lasers[laser][5][0])
                    else:
                        pass
                    # Store the output
                    self.lasers[laser][7] = output
                    #yield self.trap.set_dc(output,int(self.lasers[laser][4]))
                    yield self.piezo.set_voltage(int(self.lasers[laser][4]),U(output, 'V'))
            
            elif self.lasers[laser][6] == True and self.lasers[laser][4] == 4:
                freq = yield self.bristol.get_frequency()
                error = (self.lasers[laser][0] - freq)*1e6 # gives me diff in MHz
                # Multiply error by the gain and add the previous output
                output = error*self.lasers[laser][3]  + self.lasers[laser][7]
                # Check against the rails
                if output >= float(self.lasers[laser][5][1]):
                    output = float(self.lasers[laser][5][1])
                elif output <= float(self.lasers[laser][5][0]):
                    output = float(self.lasers[laser][5][0])
                else:
                    pass
                # Store the output
                self.lasers[laser][7] = output
                yield self.piezo.set_voltage(4,U(output, 'V'))
            
    @setting(13, state='b', chan = 's')
    def lock_channel(self, c, state, chan):
        '''
        Turn lock on or off
        '''
        self.lasers[chan][6] = int(state)
        self.update_registry(chan)

    @setting(14, value = 'v')
    def offset(self, c, value):
        yield self.trap.set_dc(value, int(self.dac_chan))
        self.prev_output = value

    @setting(15, gain = 'v', chan = 's')
    def set_gain(self, c, gain, chan):
        self.lasers[chan][3] = gain
        self.update_registry(chan)

    @setting(16, setpoint = 'v', chan = 's')
    def set_lock_frequency(self, c, setpoint, chan):
        self.lasers[chan][0] = setpoint
        self.update_registry(chan)

    @setting(17, high = 'v', chan = 's')
    def set_high_rail(self, c, high, chan):
        print high, chan
        self.lasers[chan][5][1] = high
        self.update_registry(chan)

    @setting(18, lower = 'v', chan = 's')
    def set_low_rail(self, c, lower, chan):
        self.lasers[chan][5][0] = lower
        self.update_registry(chan)

    @setting(50, voltage = 'v', chan = 's')
    def set_dac_voltage(self, c, voltage, chan):
        self.lasers[chan][7] = voltage
        yield self.piezo.set_voltage(int(self.lasers[chan][4]),U(voltage, 'V'))

    @setting(19, chan = 's', returns = 'v')
    def get_lock_frequency(self, c, chan):
        return(self.lasers[chan][0])

    @setting(20, chan = 's', returns = 'v')
    def get_gain(self, c, chan):
        return(self.lasers[chan][3])

    @setting(21, chan  = 's', returns = '*v')
    def get_rails(self, c, chan):
        return(self.lasers[chan][5])

    @setting(22, chan = 's', returns = 'v')
    def get_dac_voltage(self, c, chan):
        return(self.lasers[chan][7])

    @setting(23, chan = 's')
    def reset_lock(self, c, chan):
        self.lasers[chan][7] = 0
        if self.lasers[chan][4] != -1:
            yield self.trap.set_dc(0.0, int(self.lasers[chan][4]))
        else:
            yield self.piezo.set_voltage(4,U(0.0, 'V'))

        self.update_registry(chan)

    @setting(24, chan  = 's', returns = 'b')
    def get_lock_state(self, c, chan):
        return(bool(self.lasers[chan][6]))

    @inlineCallbacks
    def update_registry(self, chan):
        yield self.reg.set(chan, tuple(self.lasers[chan]))

    def loop_server(self):
        reactor.callLater(0.2, self.loop_server)
        self.loop()

if __name__ == "__main__":
    from labrad import util
    util.runServer(Software_Laser_Lock_Server())
