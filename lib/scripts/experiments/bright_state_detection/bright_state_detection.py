import labrad
from twisted.internet.defer import inlineCallbacks, returnValue

from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
from barium.lib.scripts.pulse_sequences.BrightState133 import bright_state as main_sequence

from config.FrequencyControl_config import FrequencyControl_config
from config.multiplexerclient_config import multiplexer_config

import time
from labrad.units import WithUnit
import numpy as np
import datetime as datetime


class bright_state_detection(experiment):

    name = 'Bright State'

    exp_parameters = []

    # Add the parameters from the required subsequences
    exp_parameters.extend(main_sequence.all_required_parameters())

    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters


    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.cxn = labrad.connect(name = 'Bright State')

        self.pulser = self.cxn.pulser
        self.grapher = self.cxn.real_simple_grapher
        self.dv = self.cxn.data_vault
        self.pv = self.cxn.parametervault

        # Define variables to be used
        self.p = self.parameters
        self.cycles = self.p.BrightState133.number_of_sequences
        # Define contexts for saving data sets
        self.c_prob = self.cxn.context()
        self.c_hist = self.cxn.context()

        self.set_up_datavault()

    def run(self, cxn, context):
        i = 1
        # program sequence to be repeated

        self.program_pulse_sequence()
        while True:
            if self.pause_or_stop():
                #Abort experiment
                return

            self.pulser.reset_readout_counts()
            self.pulser.start_number(int(self.cycles))
            self.pulser.wait_sequence_done()
            self.pulser.stop_sequence()

            pmt_counts = self.pulser.get_readout_counts()
            dc_counts = pmt_counts[::2]
            sd_counts = pmt_counts[1::2]


            print len(pmt_counts)

            self.disc = self.pv.get_parameter('StateReadout','state_readout_threshold')
            bright = np.where(sd_counts >= self.disc)
            fid = float(len(bright[0]))/len(sd_counts)
            self.dv.add(i, fid, context = self.c_prob)
            i = i + 1
            data = np.column_stack((np.arange(len(sd_counts)),sd_counts))
            self.dv.add(data, context = self.c_hist)
            self.dv.add_parameter('hist'+str(i) + 'c' + str(int(self.cycles)), True, context = self.c_hist)

    def set_up_datavault(self):
        # set up folder
        date = datetime.datetime.now()
        year  = `date.year`
        month = '%02d' % date.month  # Padded with a zero if one digit
        day   = '%02d' % date.day    # Padded with a zero if one digit
        trunk = year + '_' + month + '_' + day
        self.dv.cd(['',year,month,trunk], True, context = self.c_prob)
        dataset = self.dv.new('BrightState_Prob',[('run', 'arb u')], [('Prob', 'Prob', 'num')], context = self.c_prob)
        # add dv params
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context = self.c_prob)
        #Hist with deleted data
        self.dv.cd(['',year,month,trunk],True, context = self.c_hist)
        dataset1 = self.dv.new('BrightState_hist',[('run', 'arb u')], [('Counts', 'Hist', 'num')], context = self.c_hist)

        # Set live plotting
        self.grapher.plot(dataset, 'bright/dark', False)

    def program_pulse_sequence(self):
        pulse_sequence = main_sequence(self.p)
        pulse_sequence.programSequence(self.pulser)

    def set_wm_frequency(self, freq, chan):
        self.wm.set_pid_course(chan, freq)


    def finalize(self, cxn, context):
        self.cxn.disconnect()

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = bright_state_detection(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)




