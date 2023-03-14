"""
### BEGIN NODE INFO
[info]
name = Current Lock Server
version = 1.0
description =
instancename = Current Lock Server

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

class Current_Lock_Server(LabradServer):

    name = 'Current Lock Server'

    def initServer(self):
        self.password = os.environ['LABRADPASSWORD']
        self.name = socket.gethostname() + ' Current Lock Server'
        self.timer = 0.4 # faster than this and the computer has problems
        #self.lc = LoopingCall(self.loop)
        self.connect()

    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync('localhost',
                                      name=self.name,
                                      password=self.password)
        self.cc = self.cxn.current_controller
        self.piezo = self.cxn.piezo_controller
        self.reg = self.cxn.registry
        self.set_up_channels()


    @inlineCallbacks
    def set_up_channels(self):
        
        yield self.reg.cd(['Servers','current_lock'])
        self.gain = yield self.reg.get('gain')
        self.lock = yield self.reg.get('lock')
        self.current = yield self.reg.get('current')
        self.dac_i = yield self.piezo.get_voltage(4)
        self.current_i = yield self.cc.get_current()[0]
        self.loop_server()
        
    @inlineCallbacks
    def loop(self):
        dac_diff = 13.329-9.275
        cur_diff = 69.225-68.5
        g = cur_diff/dac_diff
        if self.lock:           
            dac = yield self.piezo.get_voltage(4)
            diff = dac-self.dac_i
            output = self.current_i - diff*float(self.gain)
            if output < 70 and output > 40:
                yield self.cc.set_current(U(output, 'mA'))
                self.current = output
                self.update_registry()

    @setting(101, value='b')
    def set_lock_state(self, c, value):
        '''
        Turn the current lock on or off
        '''
        self.lock = int(state)
        self.update_registry()

    @setting(200, returns='b')
    def get_output_state(self, c, value):
        return(bool(self.lock))

    @setting(15, gain = 'v')
    def set_gain(self, c, gain):
        self.gain = gain
        self.update_registry()
        
    @setting(20, returns = 'v')
    def get_gain(self, c):
        return(self.gain)

    @inlineCallbacks
    def update_registry(self):
        yield self.reg.set('gain',self.gain)
        yield self.reg.set('lock',self.lock)
        yield self.reg.set('current',self.current)



    def loop_server(self):
        reactor.callLater(self.timer, self.loop_server)
        self.loop()

if __name__ == "__main__":
    from labrad import util
    util.runServer(Current_Lock_Server())
