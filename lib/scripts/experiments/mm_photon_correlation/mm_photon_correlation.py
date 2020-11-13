#!scriptscanner
import labrad

from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
from barium.lib.scripts.pulse_sequences.sub_sequences.PhotonTimeTags import photon_timetags as main_sequence

import numpy as np
import datetime as datetime

class mm_photon_correlation(experiment):

    name = 'MM Photon Correlation'

  
    exp_parameters = []
    exp_parameters.append(('MMPhotonCorrelation', 'records_to_average'))
    exp_parameters.append(('MMPhotonCorrelation', 'trap_frequency'))

    exp_parameters.extend(main_sequence.all_required_parameters())

    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters

    def initialize(self, cxn, context, ident):

        self.ident = ident
        self.cxn = labrad.connect(name = 'MM Photon Correlation')
        self.pulser = self.cxn.pulser
        self.dv = self.cxn.data_vault
        self.p = self.parameters
        self.grapher = self.cxn.real_simple_grapher

        # Define contexts for saving data sets
        self.c_time = self.cxn.context()
        self.c_time_tags = self.cxn.context()
        
        self.set_scannable_parameters()
        self.set_up_datavault()

    def run(self, cxn, context):
        total_tags = np.array([])
        for i in range(self.average):
            if self.pause_or_stop():
                break
            pulse_sequence = main_sequence(self.p)
            pulse_sequence.programSequence(self.pulser)
            self.pulser.reset_timetags()
            self.pulser.start_single()
            self.pulser.wait_sequence_done()
            self.pulser.stop_sequence()
            time_tags = self.pulser.get_timetags()
            total_tags = np.append(total_tags,time_tags)
         
        self.dv.add(np.column_stack((np.zeros(len(total_tags)),total_tags)), context = self.c_time_tags)


        # Mod the time tags at the period of the trap freq
        total_tags = total_tags % (1./self.trap_freq['Hz'])        
        # bin up all the tags
        h = np.histogram(total_tags, bins = 100)
        data = np.column_stack((h[1][:-1],h[0]))
        self.dv.add(data, context = self.c_time)

    def set_scannable_parameters(self):
        self.record_time = self.p.PhotonTimeTags.record_timetags_duration
        self.average = int(self.p.MMPhotonCorrelation.records_to_average)
        self.trap_freq = self.p.MMPhotonCorrelation.trap_frequency

    def set_up_datavault(self):
        # set up folder
        date = datetime.datetime.now()
        year  = `date.year`
        month = '%02d' % date.month  # Padded with a zero if one digit
        day   = '%02d' % date.day    # Padded with a zero if one digit
        trunk = year + '_' + month + '_' + day
        self.dv.cd(['',year,month,trunk],True, context = self.c_time)
        dataset = self.dv.new('MMPhotonCorrelation',[('time', 'us')], [('Occurrence', 'Occurrence', 'abu')], context = self.c_time)
        
        self.dv.cd(['',year,month,trunk],True, context = self.c_time_tags)
        dataset2 = self.dv.new('MMPhoton Time Tags',[('arb', 'arb')],[('Time', 'Time_Tags', 's')], context = self.c_time_tags)        
        
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
    exprt = mm_photon_correlation(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)