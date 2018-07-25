from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit


class deshelving_133(pulse_sequence):

    required_parameters = [
                           ('Deshelving133', 'deshelving_duration'),
                           ('Deshelving133', 'TTL_614'),
                           ('Deshelving133', 'TTL_493_DDS'),
                           ('Deshelving133', 'channel_493'),
                           ('Deshelving133', 'frequency_493'),
                           ('Deshelving133', 'amplitude_493'),
                           ('Deshelving133', 'channel_650'),
                           ('Deshelving133', 'frequency_650'),
                           ('Deshelving133', 'amplitude_650'),
                           ]

    def sequence(self):
        # start time is defined to be 0s.
        p = self.parameters.Deshelving133

       # use this to turn the DDS to a very low power right before we turn it on
        # to avoid the weird 1us loss.
        amp_off = WithUnit(-47.0,'dBm')
        switch_on_delay = WithUnit(2.0,'us')

        # add a small delay for the switching on
        amp_change_delay = WithUnit(335.0,'ns')

        self.addDDS(p.channel_493, self.start - amp_change_delay,\
                     switch_on_delay, p.frequency_493, amp_off)
        self.addDDS(p.channel_650, self.start - amp_change_delay,\
                    switch_on_delay, p.frequency_650, amp_off)

        self.addDDS(p.channel_493, self.start + switch_on_delay - amp_change_delay, \
                     p.deshelving_duration, p.frequency_493, p.amplitude_493)
        self.addDDS(p.channel_650, self.start + switch_on_delay - amp_change_delay, \
                     p.deshelving_duration, p.frequency_650, p.amplitude_650)

        if p.deshelving_duration != 0:
            self.addTTL(p.TTL_614, self.start + switch_on_delay, p.deshelving_duration)
            self.addTTL(p.TTL_493_DDS, self.start + switch_on_delay, p.deshelving_duration)

        self.end = self.start + switch_on_delay + p.deshelving_duration

