import labrad
from twisted.internet.defer import inlineCallbacks, returnValue

from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
from barium.lib.scripts.pulse_sequences.D32 import D32_measurement as main_sequence

from config.FrequencyControl_config import FrequencyControl_config
from config.multiplexerclient_config import multiplexer_config

import time
from labrad.units import WithUnit
import numpy as np
import datetime as datetime


class d32_measurement(experiment):

    name = 'D32 Measurement'

    exp_parameters = []

    # Add the parameters from the required subsequences
    exp_parameters.extend(main_sequence.all_required_parameters())

    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters


    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.cxn = labrad.connect(name = 'D32 Measurement')
        self.pulser = self.cxn.pulser
        self.dv = self.cxn.data_vault
        self.grapher = self.cxn.grapher
        self.pv = self.cxn.parametervault

        self.HPA = self.cxn.hp8672a_server
        self.HPB = self.cxn.hp8657b_server

        # Define variables to be used
        self.p = self.parameters
        self.f = self.parameters.FrequencySweep
        self.d = self.parameters.D32Measurement


        self.cycles = self.d.Sequences_Per_Point
        self.c_prob = self.cxn.context()
        self.c_hist = self.cxn.context()

        # Need to map the gpib address to the labrad connection
        self.device_mapA = {}
        self.device_mapB = {}
        self.get_device_map()
        self.get_transitions()
        self.set_up_datavault()

    def run(self, cxn, context):

        t = np.linspace(self.d.Start_Time['us'],self.d.Stop_Time['us'],\
                    int((abs(self.d.Stop_Time['us']-self.d.Start_Time['us'])/self.d.Time_Step['us']) +1))

        self.HPB.select_device(self.device_mapB['GPIB0::6'])
        self.HPB.set_frequency(self.f.LO_freq)
        self.HPB.set_amplitude(self.f.LO_amp)

        # set the frequencies based on b-field and hyperfine splitting
        self.f.freq_1 = WithUnit(self.pi1,'MHz')
        self.f.freq_2 = WithUnit(self.pi2,'MHz')
        self.f.freq_3 = WithUnit(self.pi3,'MHz')

        if self.d.Scan == 'time':

            for i in range(len(t)):
                if self.pause_or_stop():
                    break

                self.f.time_per_freq = WithUnit(t[i],'us')
                self.disc = self.pv.get_parameter('StateReadout','state_readout_threshold')
                pulse_sequence = main_sequence(self.p)
                pulse_sequence.programSequence(self.pulser)
                self.pulser.start_number(int(self.cycles))
                self.pulser.wait_sequence_done()
                self.pulser.stop_sequence()

                counts = self.pulser.get_readout_counts()
                self.pulser.reset_readout_counts()
                bright = np.where(counts >= self.disc)
                fid = float(len(bright[0]))/len(counts)
                self.dv.add(t[i] , fid, context = self.c_prob)
                data = np.column_stack((np.arange(self.cycles),counts))
                self.dv.add(data, context = self.c_hist)
                self.dv.add_parameter('hist'+str(i), True, context = self.c_hist)

        elif self.d.Scan == 'frequency':

            freq = np.linspace(self.f.frequency_start['MHz'],self.f.frequency_stop['MHz'],\
                    int((abs(self.f.frequency_start['MHz']-self.f.frequency_stop['MHz'])/self.f.frequency_step['MHz']) +1))

            for i in range(len(freq)):
                if self.pause_or_stop():
                    break

                self.f.hyperfine_freq = WithUnit(freq[i],'MHz')
                self.get_transitions()
                # set the frequencies based on b-field and hyperfine splitting
                self.f.freq_1 = WithUnit(self.pi1,'MHz')
                self.f.freq_2 = WithUnit(self.pi2,'MHz')
                self.f.freq_3 = WithUnit(self.pi3,'MHz')
                self.disc = self.pv.get_parameter('StateReadout','state_readout_threshold')
                pulse_sequence = main_sequence(self.p)
                pulse_sequence.programSequence(self.pulser)
                self.pulser.start_number(int(self.cycles))
                self.pulser.wait_sequence_done()
                self.pulser.stop_sequence()

                counts = self.pulser.get_readout_counts()
                self.pulser.reset_readout_counts()
                bright = np.where(counts >= self.disc)
                fid = float(len(bright[0]))/len(counts)
                self.dv.add(freq[i] , fid, context = self.c_prob)
                data = np.column_stack((np.arange(self.cycles),counts))
                self.dv.add(data, context = self.c_hist)
                self.dv.add_parameter('hist'+str(i), True, context = self.c_hist)

        self.HPB.rf_state(False)


    def set_up_datavault(self):
        # set up folder
        date = datetime.datetime.now()
        year  = `date.year`
        month = '%02d' % date.month  # Padded with a zero if one digit
        day   = '%02d' % date.day    # Padded with a zero if one digit
        trunk = year + '_' + month + '_' + day
        self.dv.cd(['',year,month,trunk],True, context = self.c_prob)
        dataset = self.dv.new('D32_prob',[('time', 'us')], [('Probability', 'Probability', 'num')], context = self.c_prob)
        # add dv params
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context = self.c_prob)

        self.dv.cd(['',year,month,trunk],True, context = self.c_hist)
        dataset1 = self.dv.new('D32_hist',[('time', 'us')], [('Probability', 'Probability', 'num')], context = self.c_hist)
        # add dv params
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context = self.c_hist)

        # Set live plotting
        self.grapher.plot(dataset, 'd32', False)

    def get_transitions(self):
        # this function returns the three pi transitions in the D32 state
        # based on the b-field and hyperfine splitting entered
        self.pi1 = -1*np.sqrt(1 + (1.25491*self.f.b_field['G']**2/self.f.hyperfine_freq['MHz']**2) + \
                              (1.12023*self.f.b_field['G']/self.f.hyperfine_freq['MHz']))*self.f.hyperfine_freq['MHz'] - self.f.LO_freq['MHz']
        self.pi2 = -1*np.sqrt(1 + (1.25491*self.f.b_field['G']**2/self.f.hyperfine_freq['MHz']**2))*self.f.hyperfine_freq['MHz'] - self.f.LO_freq['MHz']
        self.pi3 = -1*np.sqrt(1 + (1.25491*self.f.b_field['G']**2/self.f.hyperfine_freq['MHz']**2) - \
                              (1.12023*self.f.b_field['G']/self.f.hyperfine_freq['MHz']))*self.f.hyperfine_freq['MHz'] - self.f.LO_freq['MHz']

        print self.pi1, self.pi2, self.pi3
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

    def finalize(self, cxn, context):
        self.cxn.disconnect()


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = d32_measurement(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)




