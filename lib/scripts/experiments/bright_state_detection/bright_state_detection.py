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
        self.cxnwlm = labrad.connect('10.97.111.8', name = 'Bright State', password = 'lab')


        self.wm = self.cxnwlm.multiplexerserver
        self.pulser = self.cxn.pulser
        #self.grapher = self.cxn.grapher
        self.dv = self.cxn.data_vault

        # Define variables to be used
        self.p = self.parameters
        self.cycles = self.p.BrightState133.number_of_sequences
        self.wm_p = multiplexer_config.info

        self.set_up_datavault()

    def run(self, cxn, context):

        # program sequence to be repeated
        pulse_sequence = main_sequence(self.p)
        pulse_sequence.programSequence(self.pulser)
        self.pulser.start_number(int(self.cycles))
        self.pulser.wait_sequence_done()
        self.pulser.stop_sequence()
        counts = self.pulser.get_readout_counts()
        self.pulser.reset_readout_counts()
        data = np.column_stack((np.arange(self.cycles),counts))
        self.dv.add(data)
        self.dv.add_parameter('BrightState', True)

    def set_up_datavault(self):
        # set up folder
        date = datetime.datetime.now()
        year  = `date.year`
        month = '%02d' % date.month  # Padded with a zero if one digit
        day   = '%02d' % date.day    # Padded with a zero if one digit
        trunk = year + '_' + month + '_' + day
        self.dv.cd(['',year,month,trunk],True)
        dataset = self.dv.new('BrightState',[('run', 'arb u')], [('Counts', 'Counts', 'num')])
        # add dv params
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter])

        # Set live plotting
        #self.grapher.plot(dataset, 'BrightState', False)


    def set_wm_frequency(self, freq, chan):
        self.wm.set_pid_course(chan, freq)


    def finalize(self, cxn, context):
        self.cxn.disconnect()
        self.cxnwlm.disconnect()

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = bright_state_detection(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)




