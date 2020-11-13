from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.E2Laser import e2laser
from sub_sequences.DopplerCooling133 import doppler_cooling_133
from sub_sequences.StatePreparation133 import state_prep_133
from sub_sequences.MetastablePrep133 import metastableprep_133
from sub_sequences.Microwaves133 import microwaves_133
from sub_sequences.Composite_1 import composite_1
from sub_sequences.Shelving133_Sub import shelving_133_sub
from sub_sequences.ShelvingStateDetection import shelving_state_detection
from sub_sequences.StandardStateDetection import standard_state_detection
from sub_sequences.Deshelving133 import deshelving_133
from labrad.units import WithUnit

class microwave_fidelity(pulse_sequence):

    required_parameters = [
                           ('MetastablePrep', 'metastable_pulse_sequence'),
                           ('MetastablePrep','State_Detection'),
                           ('MetastablePrep','number_of_1762_pulses'),
                           ]

    required_subsequences = [doppler_cooling_133, state_prep_133, metastableprep_133 microwaves_133, composite_1, \
                            shelving_133_sub, standard_state_detection, shelving_state_detection, deshelving_133]

    def sequence(self):

        p = self.parameters.MetastablePrep

        self.end = WithUnit(10.0,'us')
        self.addSequence(doppler_cooling_133)
        self.addSequence(state_prep_133)
        self.addSequence(e2laser)
        
        

        if p.State_Detection == 'spin-1/2':
            self.addSequence(standard_state_detection)

        elif p.State_Detection == 'shelving':
            self.addSequence(shelving_state_detection)
            self.addSequence(deshelving_133)
