from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit


class deshelve_led_xrsb(pulse_sequence):

    required_parameters = [
                           ('DeshelveLEDXRSB', 'deshelving_duration'),
                           ('DeshelveLEDXRSB', 'TTL_614_AOM'),
                           ('DeshelveLEDXRSB', 'TTL_614_EOM'),
                           ('DeshelveLEDXRSB', 'TTL_2_614_EOM'),
                           ('DeshelveLEDXRSB', 'channel_493'),
                           ('DeshelveLEDXRSB', 'frequency_493'),
                           ('DeshelveLEDXRSB', 'amplitude_493'),
                           ('DeshelveLEDXRSB', 'channel_650'),
                           ('DeshelveLEDXRSB', 'frequency_650'),
                           ('DeshelveLEDXRSB', 'amplitude_650'),
                           ('DeshelveLEDXRSB', 'channel_614'),
                           ('DeshelveLEDXRSB', 'frequency_614'),
                           ('DeshelveLEDXRSB', 'amplitude_614'),
                           ]

    def sequence(self):
        # start time is defined to be 0s.
        p = self.parameters.DeshelveLEDXRSB

        self.addDDS(p.channel_493, self.start, \
                     p.deshelving_duration , p.frequency_493, p.amplitude_493)
        self.addDDS(p.channel_650, self.start, \
                     p.deshelving_duration, p.frequency_650, p.amplitude_650)
        self.addDDS(p.channel_614, self.start, \
                     p.deshelving_duration, p.frequency_614, p.amplitude_614)
            
        if p.deshelving_duration != 0:
            self.addTTL(p.TTL_614_AOM, self.start, p.deshelving_duration)
#            self.addTTL(p.TTL_614_EOM, self.start, p.deshelving_duration)
            self.addTTL(p.TTL_2_614_EOM, self.start, p.deshelving_duration)


        self.end = self.start + p.deshelving_duration + WithUnit(650.0, 'ns')

