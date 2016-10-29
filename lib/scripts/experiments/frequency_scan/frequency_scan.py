import labrad
from labrad.units import WithUnit
from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
import datetime as datetime
from twisted.internet.defer import inlineCallbacks, returnValue
import numpy as np
from config.FrequencyControl_config import FrequencyControl_config
import time

class frequency_scan(experiment):

    name = 'Frequency Scan'

    exp_parameters = []

    exp_parameters.append(('Frequency_Scan', 'Frequency'))
    exp_parameters.append(('Frequency_Scan', 'Frequency_Start'))
    exp_parameters.append(('Frequency_Scan', 'Frequency_Stop'))
    exp_parameters.append(('Frequency_Scan', 'Frequency_Step'))
    exp_parameters.append(('Frequency_Scan', 'Time_Step'))


    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters


    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.cxn = labrad.connect(name = 'Frequency Scan')
        self.cxnwlm = labrad.connect('10.97.111.8', name = 'Frequency Scan', password = 'lab')
        self.cxnFreq = labrad.connect('planetexpress', name = 'Frequency Scan', password = 'lab')

        self.HPA = self.cxnFreq.hp8672a_server
        self.HPB = self.cxnFreq.hp8657b_server
        self.wm = self.cxnwlm.multiplexerserver

        # Need to map the gpib address to the labrad context number
        self.device_mapA = {}
        self.device_mapB = {}

        self.get_device_map()

        self.frequency = self.parameters.Frequency_Scan.Frequency
        self.start_frequency = self.parameters.Frequency_Scan.Frequency_Start
        self.stop_frequency = self.parameters.Frequency_Scan.Frequency_Stop
        self.step_frequency = self.parameters.Frequency_Scan.Frequency_Step
        self.time_step = self.parameters.Frequency_Scan.Time_Step


    def run(self, cxn, context):

        freq = np.linspace(self.start_frequency['THz'],self.stop_frequency['THz'],\
                    int((self.stop_frequency['THz']-self.start_frequency['THz'])/self.step_frequency['THz'] +1))
        if self.frequency == '493':
            for i in range(len(freq)):
                self.set_wm_frequency(freq[i], 1)
                time.sleep(self.time_step['s'])

        if self.frequency == '650':
            for i in range(len(freq)):
                self.set_wm_frequency(freq[i], 11)
                time.sleep(self.time_step['s'])

        if self.frequency == 'GPIB0::19':
            self.HPA.select_device(self.device_mapA['GPIB0::19'])
            for i in range(len(freq)):
                self.HPA.set_frequency(WithUnit(freq[i],'THz'))
                time.sleep(self.time_step['s'])

        if self.frequency == 'GPIB0::21':
            self.HPA.select_device(self.device_mapA['GPIB0::21'])
            for i in range(len(freq)):
                self.HPA.set_frequency(WithUnit(freq[i],'THz'))
                time.sleep(self.time_step['s'])

        if self.frequency == 'GPIB0::6':
            self.HPB.select_device(self.device_mapB['GPIB0::6'])
            for i in range(len(freq)):
                self.HPB.set_frequency(WithUnit(freq[i],'THz'))
                time.sleep(self.time_step['s'])

        if self.frequency == 'GPIB0::7':
            self.HPB.select_device(self.device_mapB['GPIB0::7'])
            for i in range(len(freq)):
                self.HPB.set_frequency(WithUnit(freq[i],'THz'))
                time.sleep(self.time_step['s'])

        if self.frequency == 'GPIB0::8':
            self.HPB.select_device(self.device_mapB['GPIB0::8'])
            for i in range(len(freq)):
                self.HPB.set_frequency(WithUnit(freq[i],'THz'))
                time.sleep(self.time_step['s'])

    def get_device_map(self):
        gpib_listA = FrequencyControl_config.gpibA
        gpib_listB = FrequencyControl_config.gpibB

        devices = self.HPA.list_devices()
        for i in range(len(gpib_listA)):
            for j in range(len(devices)):
                if devices[j][1].find(gpib_listA[i]) > 0:
                    self.device_mapA[gpib_listA[i]] = devices[j][0]
                    break

        devices = self.HPB.list_devices()
        for i in range(len(gpib_listB)):
            for j in range(len(devices)):
                if devices[j][1].find(gpib_listB[i]) > 0:
                    self.device_mapB[gpib_listB[i]] = devices[j][0]
                    break

    def set_wm_frequency(self, freq, chan):
        self.wm.set_pid_course(chan, freq)


    def finalize(self, cxn, context):
        self.cxn.disconnect()
        self.cxnwlm.disconnect()

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = frequency_scan(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)




