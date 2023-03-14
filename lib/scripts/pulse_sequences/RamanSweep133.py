from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.DopplerCooling133 import doppler_cooling_133
from sub_sequences.StatePreparation133 import state_prep_133
from sub_sequences.Raman133 import raman_133
from sub_sequences.Composite_1 import composite_1
from sub_sequences.Shelving133_Sub import shelving_133_sub
from sub_sequences.ShelvingStateDetection import shelving_state_detection
from sub_sequences.StandardStateDetection import standard_state_detection
from sub_sequences.Deshelving133 import deshelving_133
from sub_sequences.DeshelveLED import deshelve_led
from sub_sequences.GreenLaser import greenlaser

from labrad.units import WithUnit

class raman_sweep(pulse_sequence):

    required_parameters = [
                           ('RamanSweep133', 'State_Detection'),
                           ]

    required_subsequences = [doppler_cooling_133, state_prep_133, greenlaser, composite_1, \
                            shelving_133_sub, standard_state_detection,\
                            shelving_state_detection, deshelving_133,\
                            deshelve_led]

    def sequence(self):
        p = self.parameters.RamanSweep133

        self.end = WithUnit(10.0,'us')
        self.addSequence(doppler_cooling_133)
        self.addSequence(state_prep_133)
        self.addSequence(greenlaser)

        
        if p.State_Detection == 'spin-1/2':
            self.addSequence(standard_state_detection)

        elif p.State_Detection == 'shelving':
            self.addSequence(shelving_133_sub)
            self.addSequence(shelving_state_detection)
            self.addSequence(deshelve_led)


