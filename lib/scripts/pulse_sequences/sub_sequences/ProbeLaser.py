from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit
"""
For now in this experiment, using probe laser consists of turning on one EOM sideband.
This is done with an rf switch, so all we need is a TTL high for a specified amount
of time. If/When we use a dds, we'll need to add to this subsequence
"""

class probe_laser(pulse_sequence):

    required_parameters = [
                           ('ProbeLaser', 'probe_laser_duration'),
                           ('ProbeLaser', 'probe_laser_TTL'),
                           ('ProbeLaser', 'doppler_cooling_TTL'),
                           ('ProbeLaser', 'channel_650'),
                           ('ProbeLaser', 'amplitude_650'),
                           ('ProbeLaser', 'frequency_650'),
                           ]

    def sequence(self):
        # start time is defined to be 0s.
        p = self.parameters.ProbeLaser
        # select which laser to scan
        self.ttl = p.probe_laser_TTL
        self.dc_ttl = p.doppler_cooling_TTL
        amp_change_delay = WithUnit(600.0,'ns')

        self.addTTL(self.ttl, self.start, p.probe_laser_duration)
        self.addTTL(self.dc_ttl, self.start, p.probe_laser_duration)
        self.addDDS(p.channel_650, self.start - amp_change_delay, \
                     p.probe_laser_duration, p.frequency_650, p.amplitude_650)

        self.addTTL('TimeResolvedCount', self.start, p.probe_laser_duration)
        self.end = self.start + p.probe_laser_duration

