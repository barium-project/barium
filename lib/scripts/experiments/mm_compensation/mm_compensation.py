#!scriptscanner
import labrad

from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
from barium.lib.scripts.pulse_sequences.sub_sequences.PhotonTimeTags import photon_timetags as main_sequence

from processFFT import processFFT
from labrad.units import WithUnit as U
import numpy as np
import datetime as datetime

class mm_compensation(experiment):

    name = 'MM Compensation'

    '''
    Takes FFT of incoming PMT Counts

    '''

    exp_parameters = []
    exp_parameters.append(('MMCompensation', 'center_frequency'))
    exp_parameters.append(('MMCompensation', 'cycles'))
    exp_parameters.append(('MMCompensation', 'frequency_offset'))
    exp_parameters.append(('MMCompensation', 'frequency_span'))
    exp_parameters.extend(main_sequence.all_required_parameters())

    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters

    def initialize(self, cxn, context, ident):

        self.ident = ident
        self.cxn = labrad.connect(name = 'MM Compensation')
        self.pmt = self.cxn.normalpmtflow
        self.pulser = self.cxn.pulser
        self.dv = self.cxn.data_vault
        self.processor = processFFT()
        self.p = self.parameters
        self.grapher = self.cxn.real_simple_grapher

    def run(self, cxn, context):

        self.set_scannable_parameters()
        self.set_up_datavault()

        pwr = np.zeros_like(self.freqs)
        for i in range(self.average):
            if self.pause_or_stop():
                break
            pulse_sequence = main_sequence(self.p)
            pulse_sequence.programSequence(self.pulser)
            self.pulser.reset_timetags()
            self.pulser.start_single()
            self.pulser.wait_sequence_done()
            self.pulser.stop_sequence()
            timetags = self.pulser.get_timetags()
            pwr += self.processor.getPowerSpectrum(self.freqs, timetags, self.record_time, U(10.0, 'ns'))
        pwr = pwr / float(self.average)
        data = np.array(np.vstack((self.freqs/1e6, pwr)).transpose(), dtype='float')# save in MHz
        self.dv.add(data)

    def set_scannable_parameters(self):

        self.record_time = self.p.PhotonTimeTags.record_timetags_duration
        self.average = int(self.p.MMCompensation.cycles)
        self.center_freq = self.p.MMCompensation.center_frequency
        self.freq_span = self.p.MMCompensation.frequency_span
        self.freq_offset = self.p.MMCompensation.frequency_offset
        self.freqs = self.processor.computeFreqDomain(self.record_time['s'], self.freq_span['Hz'],
                                                      self.freq_offset['Hz'], self.center_freq['Hz'])

    def set_up_datavault(self):
        # set up folder
        date = datetime.datetime.now()
        year  = `date.year`
        month = '%02d' % date.month  # Padded with a zero if one digit
        day   = '%02d' % date.day    # Padded with a zero if one digit
        trunk = year + '_' + month + '_' + day
        self.dv.cd(['',year,month,trunk],True)
        dataset = self.dv.new('MMCompensation',[('freq', 'Hz')], [('Power', 'Power', 'abu')])
        # add dv params
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter])

        #Set live plotting
        self.grapher.plot(dataset, 'mm_compensation', False)

    def finalize(self, cxn, context):
        self.cxn.disconnect()


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = mm_compensation(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)