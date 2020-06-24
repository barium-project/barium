from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.DopplerCooling133 import doppler_cooling_133
from sub_sequences.MetastableStatePreparation133 import metastable_state_prep_133
from sub_sequences.MetaStableRaman import metastable_raman
from sub_sequences.MetastableReadout import metastable_readout
from sub_sequences.ShelvingStateDetection import shelving_state_detection
from sub_sequences.Deshelving133 import deshelving_133
from labrad.units import WithUnit

class metastable_rabi_flopping(pulse_sequence):

    required_parameters = [
                           ]

    required_subsequences = [doppler_cooling_133, metastable_state_prep_133, metastable_raman, metastable_readout, \
                              shelving_state_detection, deshelving_133]

    def sequence(self):

        p = self.parameters.MetastableRabiFlopping

        self.end = WithUnit(10.0,'us')
        self.addSequence(doppler_cooling_133)
        self.addSequence(metastable_state_prep_133)
        self.addSequence(metastable_raman)
        self.addSequence(metastable_readout)
        self.addSequence(shelving_state_detection)
        self.addSequence(deshelving_133)
