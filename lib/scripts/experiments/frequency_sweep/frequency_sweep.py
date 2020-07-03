import labrad
from twisted.internet.defer import inlineCallbacks, returnValue

from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
from barium.lib.scripts.pulse_sequences.FrequencySweep import frequency_sweep as main_sequence

from config.FrequencyControl_config import FrequencyControl_config
from config.multiplexerclient_config import multiplexer_config

import time
from labrad.units import WithUnit
import numpy as np
import datetime as datetime


class frequency_sweep(experiment):

    name = 'Frequency Sweep'

    exp_parameters = []

    # Add the parameters from the required subsequences
    exp_parameters.extend(main_sequence.all_required_parameters())

    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters


    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.cxn = labrad.connect(name = 'Frequency Sweep')
        self.pulser = self.cxn.pulser
        self.dv = self.cxn.data_vault
        self.grapher = self.cxn.real_simple_grapher

        self.HPA = self.cxn.hp8672a_server
        self.HPB = self.cxn.hp8657b_server

        # Define variables to be used
        self.p = self.parameters
        self.d = self.parameters.FrequencySweep

        # Need to map the gpib address to the labrad connection
        self.device_mapA = {}
        self.device_mapB = {}
        self.get_device_map()
        self.get_transitions()
        self.set_up_datavault()

    def run(self, cxn, context):

        self.HPB.select_device(self.device_mapB['GPIB0::6'])
        self.HPB.set_frequency(self.d.LO_freq)
        self.HPB.set_amplitude(self.d.LO_amp)


        # set the frequencies based on b-field and hyperfine splitting
        self.p.FrequencySweep.freq_1 = WithUnit(self.pi1,'MHz')
        self.p.FrequencySweep.freq_2 = WithUnit(self.pi2,'MHz')
        self.p.FrequencySweep.freq_3 = WithUnit(self.pi3,'MHz')

        pulse_sequence = main_sequence(self.p)
        pulse_sequence.programSequence(self.pulser)
        self.pulser.start_infinite()
        #self.pulser.start_number(10000)
        #self.pulser.wait_sequence_done()
        #self.pulser.stop_sequence()
        while not self.pause_or_stop():
            pass
        self.pulser.stop_sequence()
        #counts = self.pulser.get_readout_counts()
        #counts = np.sum(counts)
        #self.pulser.reset_readout_counts()
        #self.dv.add(self.d.hyperfine_freq['MHz'],counts)
        self.pulser.output('LF DDS',True)
        self.HPB.rf_state(False)

    def get_transitions(self):
        self.pi1 = -1*np.sqrt(1 + (1.25491*self.d.b_field['G']**2/self.d.hyperfine_freq['MHz']**2) + \
                              (1.12023*self.d.b_field['G']/self.d.hyperfine_freq['MHz']))*self.d.hyperfine_freq['MHz'] - self.d.LO_freq['MHz']
        self.pi2 = -1*np.sqrt(1 + (1.25491*self.d.b_field['G']**2/self.d.hyperfine_freq['MHz']**2))*self.d.hyperfine_freq['MHz'] - self.d.LO_freq['MHz']
        self.pi3 = -1*np.sqrt(1 + (1.25491*self.d.b_field['G']**2/self.d.hyperfine_freq['MHz']**2) - \
                              (1.12023*self.d.b_field['G']/self.d.hyperfine_freq['MHz']))*self.d.hyperfine_freq['MHz'] - self.d.LO_freq['MHz']

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

    def set_up_datavault(self):
        # set up folder
        date = datetime.datetime.now()
        year  = `date.year`
        month = '%02d' % date.month  # Padded with a zero if one digit
        day   = '%02d' % date.day    # Padded with a zero if one digit
        trunk = year + '_' + month + '_' + day
        self.dv.cd(['',year,month,trunk],True)
        dataset = self.dv.new('d32',[('Frequency', 'MHz')], [('Counts/sec', 'Counts', 'num')])
        # add dv params
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter])

        # Set live plotting
        self.grapher.plot(dataset, 'd32', False)

    def finalize(self, cxn, context):
        self.pulser.output('LF DDS',False)
        self.cxn.disconnect()


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = frequency_sweep(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)




