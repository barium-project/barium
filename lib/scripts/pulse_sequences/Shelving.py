from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.DopplerCooling133 import doppler_cooling_133
from sub_sequences.Shelving133_Sub import shelving_133_sub
from sub_sequences.ShelvingStateDetection import shelving_state_detection
from sub_sequences.Deshelving133 import deshelving_133
from labrad.units import WithUnit


class shelving(pulse_sequence):

    required_subsequences = [doppler_cooling_133, shelving_133_sub, shelving_state_detection, deshelving_133]

    def sequence(self):

        self.p = self.parameters.Shelving

        self.end = WithUnit(10.0,'us')
        self.addSequence(doppler_cooling_133)
        self.addSequence(shelving_133_sub)
        self.addSequence(shelving_state_detection)
        self.addSequence(deshelving_133)

