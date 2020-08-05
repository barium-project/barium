"""
### BEGIN NODE INFO
[info]
name = TOF Server
version = 1.0
description =
instancename = tof server

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

from labrad.server import LabradServer, setting, Signal
from twisted.internet.defer import returnValue
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
#from keysight import command_expert as kt
import datetime as datetime
import numpy as np
import time

class TOFServer(LabradServer):
    """
    Server to grab and save TOF Traces
    """
    name = 'tof server'

    @inlineCallbacks
    def initServer(self):
        self.name = 'TOF Server'
        self.password = 'lab'
        self.serverIP = 'flexo'

        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync(self.serverIP,
                                      name=self.name,
                                      password=self.password)

        self.server = yield self.cxn.trapserver
        self.dv = yield self.cxn.data_vault
        self.grapher = yield self.cxn.real_simple_grapher



    @setting(1, "get_trace")
    def get_trace(self, c):
        self.save_TOF_Data()
        yield None


    @inlineCallbacks
    def save_TOF_Data(self):
        # set up folder
        date = datetime.datetime.now()
        year  = `date.year`
        month = '%02d' % date.month  # Padded with a zero if one digit
        day   = '%02d' % date.day    # Padded with a zero if one digit
        trunk = year + '_' + month + '_' + day
        self.dv.cd(['',year,month,trunk],True)
        dataset = yield self.dv.new('TOF_Data',[('time','s')], [('rod1HV','','V'),('rod3HV','','V'), \
                             ('TTL Voltage','','V'),('TOF Voltage','','V')])

        amp = yield self.server.get_amplitude(2)
        yield self.dv.add_parameter('RF', amp)
        hv1 = yield self.server.get_hv(3)
        yield self.dv.add_parameter('Rod1HV', hv1)
        hv2 = yield self.server.get_hv(1)
        self.dv.add_parameter('Rod2HV', hv2)
        hv3 = yield self.server.get_hv(2)
        self.dv.add_parameter('Rod3HV', hv3)
        hv4 = yield self.server.get_hv(0)
        self.dv.add_parameter('Rod4HV', hv4)
        e1 = yield self.server.get_hv(6)
        self.dv.add_parameter('Elens1', e1)
        e2 = yield self.server.get_hv(7)
        self.dv.add_parameter('Elens2', e2)

        [self.time_step, self.hv_1, self.hv_2, self.hv_trig, self.tof_v] = kt.run_sequence('C:/Users/barium133/Code/barium/lib/scripts/Oscilloscope/read_voltages')
        time_step_arry = np.linspace(1,len(self.hv_1),len(self.hv_1))*self.time_step

        data = np.column_stack((time_step_arry,self.hv_1,self.hv_2,self.hv_trig,self.tof_v))
        yield self.dv.add(data)

        # Find the time where the HV pulse turns on
        hv_trigger = .2
        pulse_index =  np.where(np.array(self.hv_2) > hv_trigger)[0][1]
        # Throw out data before the hv pulse
        total_time = len(self.tof_v)*self.time_step
        start_time = self.time_step*pulse_index
        time_array = np.linspace(1,len(self.tof_v),len(self.tof_v))*self.time_step*1e6
        start_index =  pulse_index


        dataset1 = yield self.dv.new('TOF_Trace',[('time','us')], [('TOF Voltage','','V')])
        self.grapher.plot(dataset1, 'TOF_Trace', False)
        data1 = np.column_stack((time_array[start_index:]-time_array[start_index],self.tof_v[start_index:]))
        yield self.dv.add(data1)









if __name__ == "__main__":
    from labrad import util
    util.runServer(TOFServer())
