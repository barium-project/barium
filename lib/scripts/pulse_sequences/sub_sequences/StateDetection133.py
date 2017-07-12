from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from barium.lib.scripts.pulse_sequences.sub_sequences.DopplerCooling133 import doppler_cooling_133 as doppler_cooling_133
"""
6/17/17
Keeping the same format as optical pumping, but here the TTL is not auto inverted so
we use ttl high to turn on, and off time is just empty space at the end if needed.
"""

class state_detection_133(pulse_sequence):

    required_parameters = [
                           ('StateDetection133', 'state_detection_duration'),
                           ('StateDetection133', 'TTL_493'),
                           ('StateDetection133', 'TTL_650')
                           ]

    #required_parameters.extend(doppler_cooling_133.all_required_parameters())

    def sequence(self):
        # start time is defined to be 0s.
        p = self.parameters.StateDetection133


        self.ttl_493 = p.TTL_493
        self.ttl_650 = p.TTL_650

        self.addTTL('TimeResolvedCount', self.start, p.state_detection_duration)
        self.addTTL(self.ttl_493, self.start, p.state_detection_duration)
        self.addTTL(self.ttl_650, self.start, p.state_detection_duration)
        self.end = self.start + p.state_detection_duration

