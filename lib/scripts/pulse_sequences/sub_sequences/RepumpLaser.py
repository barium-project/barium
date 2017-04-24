from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence

"""
For now in this experiment, using probe laser consists of turning on one EOM sideband.
This is done with an rf switch, so all we need is a TTL high for a specified amount
of time. If/When we use a dds, we'll need to add to this subsequence
"""

class repump_laser(pulse_sequence):

    required_parameters = [
                           ('RepumpLaser', 'repump_laser_duration'),
                           ('RepumpLaser', 'repump_laser_TTL')
                           ]

    def sequence(self):
        # start time is defined to be 0s.
        p = self.parameters.RepumpLaser
        # select which laser to scan
        if p.repump_laser_TTL == '493nm':
            self.ttl = 'TTL3'
        else:
            self.ttl = 'TTL2'

        self.addTTL(self.ttl, self.start, p.repump_laser_duration)
        self.end = self.start + p.repump_laser_duration

