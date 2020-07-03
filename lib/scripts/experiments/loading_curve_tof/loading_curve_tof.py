import labrad
from labrad.units import WithUnit as U
from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
from twisted.internet.defer import inlineCallbacks, returnValue
import numpy as np
import time, os
import datetime as datetime
from keysight import command_expert as kt
import random

class loading_curve_tof(experiment):
    '''
    This experiment is designed to take a loading curve by specifying an
    array of times to load for (filament on), and the grab the tof trace.
    '''

    name = 'Loading Curve TOF'

    exp_parameters = []

    exp_parameters.append(('Loading_Curve_TOF', 'Loading_Time'))
    exp_parameters.append(('Loading_Curve_TOF', 'Loading_Current'))
    exp_parameters.append(('Loading_Curve_TOF', 'Loading_Voltages'))
    exp_parameters.append(('Loading_Curve_TOF', 'A_Ramp'))
    exp_parameters.append(('Loading_Curve_TOF', 'A_Ramp_Voltage'))
    exp_parameters.append(('Loading_Curve_TOF', 'A_Ramp_Time'))
    exp_parameters.append(('Loading_Curve_TOF', 'Discriminator'))

    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters


    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.cxn = labrad.connect(name = 'Loading Curve TOF')
        self.cxnHP = labrad.connect('bender', name = 'loading curve tof', password = 'lab')
        self.trap = self.cxn.trap_server
        self.hp = self.cxnHP.hp6033a_server
        self.hp.select_device(0)
        self.dv = self.cxn.data_vault
        self.grapher = self.cxn.real_simple_grapher

        self.set_up_parameters()
        self.set_up_tof_folder()

    def run(self, cxn, context):

        for i in range(len(self.time_arr)):
            if self.pause_or_stop():
                break

            # run the filament
            self.run_filament(self.time_arr[i])

            # a ramp
            if int(self.a_ramp) == 1:
                self.a_param()
                time.sleep(1)

            # Trigger the TOF and get the data
            self.trap.trigger_hv_pulse()
            [time_step, ch1, ch2, ch3, ch4] = kt.run_sequence('C:/Users/barium133/Code/barium/lib/scripts/Oscilloscope/read_voltages')
            time_step_arry = np.linspace(1,len(ch1),len(ch1))*time_step
            ch4 = np.array(ch4)
            ind = np.where(ch4 < -.010)
            data = ch4[ind[0]]*-1 # signal is negative, make postitive
            counts = np.sum(data)
            self.dv.add(self.time_arr[i],counts)
            self.save_tof_data(i,time_step,ch1,ch2,ch3,ch4)


    def set_up_datavault(self,x_data,y_data, run_num):
        # set up folder
        date = datetime.datetime.now()
        year  = `date.year`
        month = '%02d' % date.month  # Padded with a zero if one digit
        day   = '%02d' % date.day    # Padded with a zero if one digit
        trunk = year + '_' + month + '_' + day
        self.dv.cd(['',year,month,trunk],True)
        dataset = self.dv.new('Loading_Curve_TOF_run' + str(run_num),x_data, y_data)

        self.dv.add_parameter('Loading_Current', self.parameters.Loading_Curve_TOF.Loading_Current)
        self.dv.add_parameter('Loading_Voltage',self.parameters.Loading_Curve_TOF.Loading_Voltages)
        self.dv.add_parameter('Loading_Time', self.parameters.Loading_Curve_TOF.Loading_Time)

        self.dv.add_parameter('A_Ramp',self.parameters.Loading_Curve_TOF.A_Ramp)
        self.dv.add_parameter('A_Ramp_Voltage', self.parameters.Loading_Curve_TOF.A_Ramp_Voltage)
        self.dv.add_parameter('A_Ramp_Time', self.parameters.Loading_Curve_TOF.A_Ramp_Time)
        self.dv.add_parameter('Discriminator', self.parameters.Loading_Curve_TOF.Discriminator)
        self.dv.add_parameter('RF', self.trap.get_amplitude(2))
        self.dv.add_parameter('Rod1HV', self.trap.get_hv(3))
        self.dv.add_parameter('Rod2HV', self.trap.get_hv(1))
        self.dv.add_parameter('Rod3HV', self.trap.get_hv(2))
        self.dv.add_parameter('Rod4HV', self.trap.get_hv(0))
        self.dv.add_parameter('Elens1', self.trap.get_hv(6))
        self.dv.add_parameter('Elens2', self.trap.get_hv(7))


        self.grapher.plot(dataset, 'Loading_Curve_TOF', False)

    def set_up_parameters(self):
        self.current = self.parameters.Loading_Curve_TOF.Loading_Current
        self.voltage = self.parameters.Loading_Curve_TOF.Loading_Voltages
        self.a_ramp = self.parameters.Loading_Curve_TOF.A_Ramp
        self.a_ramp_voltage = self.parameters.Loading_Curve_TOF.A_Ramp_Voltage
        self.a_ramp_time = self.parameters.Loading_Curve_TOF.A_Ramp_Time
        self.discriminator = self.parameters.Loading_Curve_TOF.Discirminator

        self.min_time = self.parameters.Loading_Curve_TOF.Loading_Time[0]['s']
        self.max_time = self.parameters.Loading_Curve_TOF.Loading_Time[1]['s']
        self.num_steps = self.parameters.Loading_Curve_TOF.Loading_Time[2]

        self.time_arr = np.linspace(self.min_time,self.max_time,self.num_steps)
        print self.time_arr
        np.random.shuffle(self.time_arr)
        print self.time_arr

    def run_filament(self,load_time):
        self.hp.set_voltage(self.voltage)
        self.hp.set_current(self.current)
        time.sleep(int(load_time))
        self.hp.set_current(U(0,'A'))
        time.sleep(3)

    def a_param(self):
        rod1_volt = self.trap.get_dc_rod(3)
        rod3_volt = self.trap.get_dc_rod(2)
        self.trap.set_dc_rod(self.a_ramp_voltage['V'],3)
        self.trap.set_dc_rod(self.a_ramp_voltage['V'],2)
        time.sleep(self.a_ramp_time['s'])
        self.trap.set_dc_rod(rod1_volt,3)
        self.trap.set_dc_rod(rod3_volt,2)


    def save_tof_data(self, i, time_step, channel1, channel2, channel3, channel4):

        data_string = '#[time step in voltage data]'
        data = np.array([time_step])
        np.savetxt(self.direct+ str(i+1)+ '_parameters.txt',data,fmt="%0.5e", \
           header = data_string, comments = '')
        np.savetxt(self.direct+ str(i+1)+ '_hv_3.txt',channel1,fmt="%0.5f")
        np.savetxt(self.direct+ str(i+1)+ '_hv_2.txt',channel2,fmt="%0.5f")
        np.savetxt(self.direct+ str(i+1)+ '_ttl_v.txt',channel3,fmt="%0.5f")
        np.savetxt(self.direct+ str(i+1)+ '_tof_v.txt',channel4,fmt="%0.5f")

    def set_up_tof_folder(self):
        # set up folder
        date = datetime.datetime.now()
        year  = `date.year`
        month = '%02d' % date.month  # Padded with a zero if one digit
        day   = '%02d' % date.day
        folder = year+'/'+month+'/'+day
        direct = 'Z:/Group_Share/Barium/Data/'+folder+'/Loading_Curve_TOF/TOF_Data'
        run_num = np.array([])
        if os.path.exists(direct):
            direct_list = list()
            for root, dirs, files in os.walk(direct,topdown=False):
                for name in dirs:
                    direct_list.append(os.path.join(root,name))
            if len(direct_list) > 0:
                for i in range(len(direct_list)):
                    run_num = np.append(run_num, int(direct_list[i][-1]))
                max = int(np.amax(run_num))
                self.direct = direct+'/run'+str(max+1)+'/'
                os.makedirs(self.direct)
            else:
                self.direct = direct+'/run1/'
                os.makedirs(self.direct)
        else:
            self.direct = direct+'/run1/'
            os.makedirs(self.direct)

        self.set_up_datavault([('time','s')],[('Total Voltage','','V')],max)
    def finalize(self, cxn, context):
        self.cxn.disconnect()
        #self.cxnwlm.disconnect()
        self.cxnHP.disconnect()

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = loading_curve_tof(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)


