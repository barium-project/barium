from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit


class deshelve_led(pulse_sequence):

    required_parameters = [
                           ('DeshelveLED', 'deshelving_duration'),
                           ('DeshelveLED', 'TTL_614_AOM'),
                           ('DeshelveLED', 'TTL_614_EOM'),
                           ('DeshelveLED', 'TTL_2_614_EOM'),
                           ('DeshelveLED', 'channel_493'),
                           ('DeshelveLED', 'frequency_493'),
                           ('DeshelveLED', 'amplitude_493'),
                           ('DeshelveLED', 'channel_650'),
                           ('DeshelveLED', 'frequency_650'),
                           ('DeshelveLED', 'amplitude_650'),
                           ]

    def sequence(self):
        # start time is defined to be 0s.
        p = self.parameters.DeshelveLED

        self.addDDS(p.channel_493, self.start, \
                     p.deshelving_duration , p.frequency_493, p.amplitude_493)
        self.addDDS(p.channel_650, self.start, \
                     p.deshelving_duration, p.frequency_650, p.amplitude_650)

        if p.deshelving_duration != 0:
            self.addTTL(p.TTL_614_AOM, self.start, p.deshelving_duration)
            self.addTTL(p.TTL_614_EOM, self.start, p.deshelving_duration)
            self.addTTL(p.TTL_2_614_EOM, self.start, p.deshelving_duration)


        self.end = self.start + p.deshelving_duration + WithUnit(650.0, 'ns')

