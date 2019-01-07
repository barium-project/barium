from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class shelving_1762(pulse_sequence):

    required_parameters = [
                           ('Shelving1762', 'shelving_duration'),
                           ('Shelving1762', 'TTL_493_DDS'),
                           ('Shelving1762', 'TTL_493'),
                           ('Shelving1762', 'TTL_1762'),
                           ]


    def sequence(self):
        # start time is defined to be 0s.
        p = self.parameters.Shelving1762



        # use this to turn the DDS to a very low power right before we turn it on
        # to avoid the weird 1us loss.
        switch_on_delay = WithUnit(2.0,'us')

        if p.shelving_duration != 0:

            self.addTTL(p.TTL_493_DDS, self.start, p.shelving_duration + 2*switch_on_delay)
            self.addTTL(p.TTL_493, self.start, p.shelving_duration + 2*switch_on_delay)

            self.addTTL(p.TTL_1762, self.start + switch_on_delay, p.shelving_duration)

            self.end = self.start + switch_on_delay +  p.shelving_duration + switch_on_delay

        else:
            self.end = self.start




