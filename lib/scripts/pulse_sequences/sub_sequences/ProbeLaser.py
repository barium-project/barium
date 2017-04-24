from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence

"""
For now in this experiment, using probe laser consists of turning on one EOM sideband.
This is done with an rf switch, so all we need is a TTL high for a specified amount
of time. If/When we use a dds, we'll need to add to this subsequence
"""

class probe_laser(pulse_sequence):

    required_parameters = [
                           ('ProbeLaser', 'probe_laser_duration'),
                           ('ProbeLaser', 'probe_laser_TTL')
                           ]

    def sequence(self):
        # start time is defined to be 0s.
        p = self.parameters.ProbeLaser
        # select which laser to scan
        if p.probe_laser_TTL == '493nm':
            self.ttl = 'TTL26'
        else:
            self.ttl = 'TTL25'

        self.addTTL(self.ttl, self.start, p.probe_laser_duration)
        self.end = self.start + p.probe_laser_duration

