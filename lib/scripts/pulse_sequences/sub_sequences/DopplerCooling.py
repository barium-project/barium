from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence

"""
For now in this experiment, Doppler cooling just consists of turning on one EOM sideband.
This is done with an rf switch, so all we need is a TTL high for a specified amount
of time. If/When we use a dds, we'll need to add to this subsequence
"""

class doppler_cooling(pulse_sequence):

    required_parameters = [
                           ('DopplerCooling', 'doppler_cooling_duration'),
                           ]

    def sequence(self):
        # start time is defined to be 0s.
        p = self.parameters.DopplerCooling
        self.addTTL('TTL2', self.start, p.doppler_cooling_duration)
        self.end = self.start + p.doppler_cooling_duration

