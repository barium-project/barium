from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence

from sub_sequences.DopplerCooling133 import doppler_cooling_133
from sub_sequences.StatePreparation133 import state_prep_133
from sub_sequences.Microwaves133 import microwaves_133
from sub_sequences.E2Laser import e2laser
from sub_sequences.MetaStableRaman import metastable_raman
from sub_sequences.ShelvingStateDetection import shelving_state_detection
from sub_sequences.Deshelving133 import deshelving_133
from sub_sequences.DeshelveLED import deshelve_led
from labrad.units import WithUnit



class metastable_rabi_flopping(pulse_sequence):

    required_parameters = [
                            ('PSMetastableRabi','prep_state'),
                           ]

    required_subsequences = [doppler_cooling_133, state_prep_133,\
                             microwaves_133, e2laser, metastable_raman,\
                            shelving_state_detection,deshelving_133,\
                            deshelve_led]

    def sequence(self):

        p = self.parameters.PSMetastableRabi

        self.end = WithUnit(10.0,'us')
        self.addSequence(doppler_cooling_133)
        self.addSequence(state_prep_133)
        if p.prep_state == '1':
            self.addSequence(microwaves_133)
        self.addSequence(e2laser)
        self.addSequence(shelving_state_detection)            
        self.addSequence(metastable_raman)
        self.addSequence(deshelving_133)
        self.addSequence(shelving_state_detection)
        self.addSequence(deshelve_led)
