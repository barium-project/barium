from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.DopplerCooling133 import doppler_cooling_133
from sub_sequences.StandardStateDetection import standard_state_detection

from labrad.units import WithUnit


class bright_state(pulse_sequence):

    required_parameters = [
                           ('BrightState133', 'number_of_sequences')
                           ]

    required_subsequences = [doppler_cooling_133,standard_state_detection]

    def sequence(self):
        self.p = self.parameters.BrightState133

        self.end = WithUnit(10.0,'us')
        self.addSequence(doppler_cooling_133)
        self.addSequence(standard_state_detection)



