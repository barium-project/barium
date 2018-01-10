"""
### BEGIN NODE INFO
[info]
name = Single Channel Lock Server
version = 1.0
description =
instancename = Single Channel Lock Server

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
import os
import socket
from config.multiplexerclient_config import multiplexer_config

class Single_Channel_Lock_Server(LabradServer):

    name = 'Single Channel Lock Server'

    def initServer(self):
        self.password = os.environ['LABRADPASSWORD']
        self.name = socket.gethostname() + ' Single Channel Lock Server'
        self.set_frequency = 658.116220
        self.timer = 0.1
        self.low_rail = 0
        self.high_rail =30.0
        self.p_gain = 1e-3 # Gain of piezo controller is 15V/V
        self.i_gain = 1e-5 # Not using now since lock is pretty good
        self.integral = 0 # to use for I
        self.prev_output = 0.0
        self.dac_chan = 7
        self.ff_chan = 6
        self.ff_gain = 1
        self.lasers = multiplexer_config.info
        self.laser_chan = '455nm'
        self.lc = LoopingCall(self.loop)
        self.output = 0.0
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

    @inlineCallbacks
    def loop(self):
            freq = yield self.wm.get_frequency(self.lasers[self.laser_chan][0])
            error = (self.set_frequency - freq)*1e6 # gives me diff in MHz
            self.integral = self.integral + error*self.timer
            self.output = error*self.p_gain  + self.prev_output
            if self.output >= self.high_rail:
                self.output = self.high_rail
            elif self.output <= self.low_rail:
                self.output = self.low_rail
            else:
                pass
            self.prev_output = self.output
            yield self.trap.set_dc(self.output,int(self.dac_chan))

    @setting(13, state='b')
    def toggle(self, c, state):
        '''
        Turn lock on or off
        '''
        if state:
            self.lc.start(self.timer)
        else:
            self.lc.stop()

    @setting(14, value = 'v')
    def offset(self, c, value):
        yield self.trap.set_dc(value, int(self.dac_chan))
        self.prev_output = value

    @setting(15, gain = 'v')
    def set_gain(self, c, gain):
        self.p_gain = gain

    @setting(16, setpoint = 'v')
    def set_point(self, c, setpoint):
        self.set_frequency = setpoint

    @setting(17, high = 'v')
    def set_high_rail(self, c, high):
        self.high_rail = high

    @setting(18, lower = 'v')
    def set_low_rail(self, c, lower):
        self.low_rail = lower

    @setting(19, returns = 'v')
    def get_lock_frequency(self, c):
        return(self.set_frequency)

    @setting(20, returns = 'v')
    def get_gain(self, c):
        return(self.p_gain)

    @setting(21, returns = '*v')
    def get_rails(self, c):
        return([self.low_rail,self.high_rail])

    @setting(22, returns = 'v')
    def get_dac_voltage(self, c):
        return(self.output)

    @setting(23)
    def reset_lock(self, c):
        self.prev_output = 0
        self.output = 0
        yield self.trap.set_dc(0.0, int(self.dac_chan))

if __name__ == "__main__":
    from labrad import util
    util.runServer(Single_Channel_Lock_Server())
