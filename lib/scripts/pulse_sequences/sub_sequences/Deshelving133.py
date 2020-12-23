from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit


class deshelving_133(pulse_sequence):

    required_parameters = [
                           ('Deshelving133', 'deshelving_duration'),
                           ('Deshelving133', 'channel_493'),
                           ('Deshelving133', 'frequency_493'),
                           ('Deshelving133', 'amplitude_493'),
                           ('Deshelving133', 'channel_650'),
                           ('Deshelving133', 'frequency_650'),
                           ('Deshelving133', 'amplitude_650'),
                           ('Deshelving133', 'TTL_614_AOM'),
                           ('Deshelving133', 'TTL_614_EOM'),

                           ]

    def sequence(self):
        # start time is defined to be 0s.
        p = self.parameters.Deshelving133

        self.addDDS(p.channel_493, self.start, \
                     p.deshelving_duration , p.frequency_493, p.amplitude_493)
        self.addDDS(p.channel_650, self.start, \
                     p.deshelving_duration, p.frequency_650, p.amplitude_650)

        if p.deshelving_duration != 0:
            self.addTTL(p.TTL_614_AOM, self.start, p.deshelving_duration)
            self.addTTL(p.TTL_614_EOM, self.start, p.deshelving_duration)

        self.end = self.start + p.deshelving_duration + WithUnit(650.0, 'ns')

