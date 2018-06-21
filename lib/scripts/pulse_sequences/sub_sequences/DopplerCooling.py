from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence

"""
For now in this experiment, Doppler cooling just consists of turning on one EOM sideband.
This is done with an rf switch, so all we need is a TTL high for a specified amount
of time. If/When we use a dds, we'll need to add to this subsequence

4/14/2017
AS of now the default state of these TTL switches is high, they are auto inverted,
so that we cool by default. This means to turn off Doppler cooling we need to write
a TTL high for the off time.
"""

class doppler_cooling(pulse_sequence):

    required_parameters = [
                           ('DopplerCooling', 'doppler_cooling_duration'),
                           ]

    def sequence(self):
        # start time is defined to be 0s.
        p = self.parameters.DopplerCooling
        self.end = self.start + p.doppler_cooling_duration

