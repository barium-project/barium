import labrad
from labrad.units import WithUnit as U
from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
from twisted.internet.defer import inlineCallbacks, returnValue
import numpy as np
import time
import datetime as datetime
from config.FrequencyControl_config import FrequencyControl_config

class filament_loading(experiment):

    name = 'Filament Loading'

    exp_parameters = []

    exp_parameters.append(('Filament_Loading', 'Loading_Time'))

    exp_parameters.append(('Filament_Loading', 'Loading_Current'))
    exp_parameters.append(('Filament_Loading', 'Loading_Voltages'))

    exp_parameters.append(('Filament_Loading', 'Toggle_RF'))
    exp_parameters.append(('Filament_Loading', 'A_Ramp'))
    exp_parameters.append(('Filament_Loading', 'A_Ramp_Voltage'))
    exp_parameters.append(('Filament_Loading', 'A_Ramp_Time'))
    exp_parameters.append(('Filament_Loading', 'Even_Isotope_Heating_While_Loading'))


    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters


    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.cxn = labrad.connect(name = 'Filament Loading')
        #self.cxnwlm = labrad.connect('10.97.111.8', name = 'Linescan Camera', password = 'lab')
        self.cxnHP = labrad.connect('bender', name = 'filament loading', password = 'lab')
        self.trap = self.cxn.trap_server
        self.hp = self.cxnHP.hp6033a_server
        self.hp.select_device(0)
        self.dv = self.cxn.data_vault
        self.hpa = self.cxnHP.hp8672a_server
        #self.cam = self.cxn.andor_server

        self.current = self.parameters.Filament_Loading.Loading_Current
        self.voltage = self.parameters.Filament_Loading.Loading_Voltages
        self.load_time = self.parameters.Filament_Loading.Loading_Time

        self.toggle_rf = self.parameters.Filament_Loading.Toggle_RF
        self.a_ramp = self.parameters.Filament_Loading.A_Ramp
        self.a_ramp_voltage = self.parameters.Filament_Loading.A_Ramp_Voltage
        self.a_ramp_time = self.parameters.Filament_Loading.A_Ramp_Time
        self.heating = self.parameters.Filament_Loading.Even_Isotope_Heating_While_Loading

        # Need to map the gpib address to the labrad context number
        self.device_mapA = {}
        self.get_device_map()


    def run(self, cxn, context):
        date = datetime.datetime.now()
        year  = `date.year`
        month = '%02d' % date.month  # Padded with a zero if one digit
        day   = '%02d' % date.day    # Padded with a zero if one digit
        trunk = year + '_' + month + '_' + day
        self.dv.cd(['',year,month,trunk],True)
        dataset = self.dv.new('Filament_Loading',[('number', 'a.b.u')], [('', 'NA','a.b.u.')])

        self.dv.add_parameter('Loading_Current', self.parameters.Filament_Loading.Loading_Current)
        self.dv.add_parameter('Loading_Voltage',self.parameters.Filament_Loading.Loading_Voltages)
        self.dv.add_parameter('Loading_Time', self.parameters.Filament_Loading.Loading_Time)

        self.dv.add_parameter('Toggle_RF', self.parameters.Filament_Loading.Toggle_RF)
        self.dv.add_parameter('A_Ramp',self.parameters.Filament_Loading.A_Ramp)
        self.dv.add_parameter('A_Ramp_Voltage', self.parameters.Filament_Loading.A_Ramp_Voltage)
        self.dv.add_parameter('A_Ramp_Time', self.parameters.Filament_Loading.A_Ramp_Time)
        self.dv.add_parameter('Even_Isotope_Heating', self.parameters.Filament_Loading.Even_Isotope_Heating_While_Loading)


        if int(self.heating) == 1:
            self.hpa.select_device(self.device_mapA['GPIB0::19'])
            self.hpa.rf_state(True)
        self.run_filament()
        if int(self.a_ramp) == 1:
            rod1_volt = self.trap.get_dc_rod(3)
            rod3_volt = self.trap.get_dc_rod(2)
            self.trap.set_dc_rod(self.a_ramp_voltage['V'],3)
            self.trap.set_dc_rod(self.a_ramp_voltage['V'],2)
            time.sleep(self.a_ramp_time['s'])
            self.trap.set_dc_rod(rod1_volt,3)
            self.trap.set_dc_rod(rod3_volt,2)
        if int(self.heating) == 1:
            self.hpa.rf_state(False)



    def run_filament(self):
        self.hp.set_voltage(self.voltage)
        self.hp.set_current(self.current)
        time.sleep(int(self.load_time['s']/2))
        if int(self.toggle_rf) == 1:
            self.trap.trigger_loading()
        time.sleep(int(self.load_time['s']/2))
        self.hp.set_current(U(0,'A'))

    def get_device_map(self):
        gpib_listA = FrequencyControl_config.gpibA
        devices = self.hpa.list_devices()
        for i in range(len(gpib_listA)):
            for j in range(len(devices)):
                if devices[j][1].find(gpib_listA[i]) > 0:
                    self.device_mapA[gpib_listA[i]] = devices[j][0]
                    break


    def finalize(self, cxn, context):
        self.cxn.disconnect()
        #self.cxnwlm.disconnect()
        self.cxnHP.disconnect()

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = filament_loading(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)


