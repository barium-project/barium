from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U

"""
We want to record photon counts only when we're probing the ion with the probe
beam. Probe beam is turned on using and EOM which is controlled with an rf switch.
To photon count you must set an internal TTL labeled below as 'TimeResolvedCounts'.
We also need one ttl pulse to turn on the probe beam.
"""


class photon_timetags(pulse_sequence):

    required_parameters = [('PhotonTimeTags','record_timetags_duration')]

    def sequence(self):
        # start time is defined to be 1.0 us, but we want to start at 0.0s.
        self.start = U(0.0, 's')
        p = self.parameters.PhotonTimeTags
        self.addTTL('TimeResolvedCount', self.start, p.record_timetags_duration)
        self.end = self.start + p.record_timetags_duration