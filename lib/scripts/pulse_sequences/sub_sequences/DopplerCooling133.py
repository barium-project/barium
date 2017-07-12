from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence

"""
6/19/2017
AS of now the default state of these TTL switches is high, they are auto inverted,
so that we cool by default. This means to turn off Doppler cooling we need to write
a TTL high for the off time.
J Christensen
"""

class doppler_cooling_133(pulse_sequence):

    required_parameters = [
                           ('DopplerCooling133', 'doppler_cooling_duration'),
                           ('DopplerCooling133', 'TTL_493'),
                           ('DopplerCooling133', 'TTL_650'),
                           ]

    def sequence(self):
        # start time is defined to be 0s.
        p = self.parameters.DopplerCooling133
        self.ttl_blank = 'TTL13'

        self.addTTL(self.ttl_blank, self.start, p.doppler_cooling_duration)
        self.end = self.start + p.doppler_cooling_duration

