import labrad
from labrad.units import WithUnit as U
from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
from twisted.internet.defer import inlineCallbacks, returnValue
import numpy as np
import time, os
import datetime as datetime
from config.FrequencyControl_config import FrequencyControl_config
from keysight import command_expert as kt


class loading_curve_cam(experiment):
    '''
    This experiment is designed to take a loading curve by specifying an
    array of times to load for (filament on), and then look at the data.
    The camera will take a picture before and after loading.
    '''

    name = 'Loading Curve Cam'

    exp_parameters = []

    exp_parameters.append(('Loading_Curve_Cam', 'Loading_Time'))
    exp_parameters.append(('Loading_Curve_Cam', 'Loading_Current'))
    exp_parameters.append(('Loading_Curve_Cam', 'Loading_Voltages'))
    exp_parameters.append(('Loading_Curve_Cam', 'A_Ramp'))
    exp_parameters.append(('Loading_Curve_Cam', 'A_Ramp_Voltage'))
    exp_parameters.append(('Loading_Curve_Cam', 'A_Ramp_Time'))
    exp_parameters.append(('Loading_Curve_Cam', 'Subtract_BG'))
    exp_parameters.append(('Loading_Curve_Cam', 'Time_Step'))
    exp_parameters.append(('Loading_Curve_Cam', 'Run_Number'))


    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters


    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.cxn = labrad.connect(name = 'Loading Curve Cam')
        #self.cxnwlm = labrad.connect('10.97.111.8', name = 'Linescan Camera', password = 'lab')
        self.cxnHP = labrad.connect('bender', name = 'loading curve cam', password = 'lab')
        self.trap = self.cxn.trap_server
        self.hp = self.cxnHP.hp6033a_server
        self.hp.select_device(0)
        self.dv = self.cxn.data_vault
        self.cam = self.cxn.andor_server
        self.pmt = self.cxn.normalpmtflow
        self.pulser = self.cxn.pulser
        self.grapher = self.cxn.real_simple_grapher

    def run(self, cxn, context):
        self.set_up_parameters()
        self.set_up_datavault()

        # Get a background image if using the camera
        if int(self.subtract_bg) == 1:
            self.bg_image = self.get_image()

        self.hp.set_voltage(self.voltage)
        self.hp.set_current(self.current)
        self.trap.set_rf_state(False)
        time.sleep(30)
        self.trap.set_rf_state(True)

        date = datetime.datetime.now()
        self.start_time = (date.hour*3600+date.minute*60+date.second+date.microsecond*1e-6)
        print self.start_time
        while True:
            if self.pause_or_stop():
                break
            time.sleep(.250)
            date = datetime.datetime.now()
            date = date.hour*3600+date.minute*60+date.second+date.microsecond*1e-6
            print date
            if (date - self.start_time) > self.total_time:
                break

            image_data = self.get_image()
            if int(self.subtract_bg) == 1:
                image_data = image_data-self.bg_image

            counts = np.sum(np.sum(image_data))

            self.dv.add(date-self.start_time,counts)
            #time.sleep(self.time_step)



        self.hp.set_current(U(0,'A'))
        time.sleep(3)

        # a ramp
        if int(self.a_ramp) == 1:
                self.a_param()

        #self.get_tof_data()


    def set_up_datavault(self):
        # set up folder
        date = datetime.datetime.now()
        year  = `date.year`
        month = '%02d' % date.month  # Padded with a zero if one digit
        day   = '%02d' % date.day    # Padded with a zero if one digit
        trunk = year + '_' + month + '_' + day
        self.dv.cd(['',year,month,trunk],True)
        dataset = self.dv.new('Loading_Curve_Cam' + str(int(self.run_number)),[('Time', 's')], [('', 'Counts', 'a.b.u')])
        self.grapher.plot(dataset, 'Loading_Curve_Cam', False)

        # add dv params
        self.dv.add_parameter('Loading_Current', self.parameters.Loading_Curve_Cam.Loading_Current)
        self.dv.add_parameter('Loading_Voltage',self.parameters.Loading_Curve_Cam.Loading_Voltages)
        self.dv.add_parameter('Loading_Time', self.parameters.Loading_Curve_Cam.Loading_Time)

        self.dv.add_parameter('Subtract_BG', self.parameters.Loading_Curve_Cam.Subtract_BG)
        self.dv.add_parameter('A_Ramp',self.parameters.Loading_Curve_Cam.A_Ramp)
        self.dv.add_parameter('A_Ramp_Voltage', self.parameters.Loading_Curve_Cam.A_Ramp_Voltage)
        self.dv.add_parameter('A_Ramp_Time', self.parameters.Loading_Curve_Cam.A_Ramp_Time)
        self.dv.add_parameter('Run_Number', self.parameters.Loading_Curve_Cam.Run_Number)

    def set_up_parameters(self):
        self.current = self.parameters.Loading_Curve_Cam.Loading_Current
        self.voltage = self.parameters.Loading_Curve_Cam.Loading_Voltages
        self.subtract_bg = self.parameters.Loading_Curve_Cam.Subtract_BG
        self.a_ramp = self.parameters.Loading_Curve_Cam.A_Ramp
        self.a_ramp_voltage = self.parameters.Loading_Curve_Cam.A_Ramp_Voltage
        self.a_ramp_time = self.parameters.Loading_Curve_Cam.A_Ramp_Time
        self.run_number = self.parameters.Loading_Curve_Cam.Run_Number

        self.total_time = self.parameters.Loading_Curve_Cam.Loading_Time['s']
        self.time_step = self.parameters.Loading_Curve_Cam.Time_Step['s']

        self.time_arr = np.linspace(0,self.total_time,int(self.total_time/self.time_step))

    def a_param(self):
        rod1_volt = self.trap.get_dc_rod(3)
        rod3_volt = self.trap.get_dc_rod(2)
        self.trap.set_dc_rod(self.a_ramp_voltage['V'],3)
        self.trap.set_dc_rod(self.a_ramp_voltage['V'],2)
        time.sleep(self.a_ramp_time['s'])
        self.trap.set_dc_rod(rod1_volt,3)
        self.trap.set_dc_rod(rod3_volt,2)

    def get_image(self):
        #self.cam.set_shutter_mode('Auto')
        #self.cam.set_acquisition_mode('Single Scan')
        #self.cam.start_acquisition()
        #self.cam.wait_for_acquisition()
        image = self.cam.get_most_recent_image(None)
        #self.cam.abort_acquisition()
        #self.cam.set_shutter_mode('Close')
        return image

    def get_tof_data(self):
        channel1  = np.zeros((1,10000))
        channel2  = np.zeros((1,10000))
        channel3  = np.zeros((1,10000))
        channel4  = np.zeros((1,10000))
        self.trap.trigger_hv_pulse()

        [time_step, ch1, ch2, ch3, ch4] = kt.run_sequence('C:/Users/barium133/Code/barium/lib/scripts/Oscilloscope/read_voltages')
        channel1[0,:] = ch1
        channel2[0,:] = ch2
        channel3[0,:] = ch3
        channel4[0,:] = ch4

        direct = 'Z:/Group_Share/Barium/Data/2016/11/7/TOF_Data/run' + str(int(self.run_number))
        os.mkdir(direct)

        file_loc = 'Z:/Group_Share/Barium/Data/2016/11/7/TOF_Data/run' + str(int(self.run_number))+'/'
        data_string = '#[time step in voltage data]'
        data = np.array([time_step])
        np.savetxt(file_loc+ 'parameters.txt',data,fmt="%0.5e",
           header = data_string, comments = '')
        np.savetxt(file_loc+ 'hv_3.txt',channel1,fmt="%0.5f")
        np.savetxt(file_loc+ 'hv_2.txt',channel2,fmt="%0.5f")
        np.savetxt(file_loc+ 'ttl_v.txt',channel3,fmt="%0.5f")
        np.savetxt(file_loc+'tof_v.txt',channel4,fmt="%0.5f")


    def finalize(self, cxn, context):
        self.cxn.disconnect()
        #self.cxnwlm.disconnect()
        self.cxnHP.disconnect()

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = loading_curve_cam(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)


