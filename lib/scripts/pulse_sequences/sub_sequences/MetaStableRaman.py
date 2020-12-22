from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit


class metastable_raman(pulse_sequence):

    required_parameters = [
                           ('MetaStableRaman', 'raman_duration'),
                           ('MetaStableRaman', 'channel_614_1'),
                           ('MetaStableRaman', 'frequency_614_1'),
                           ('MetaStableRaman', 'amplitude_614_1'),
                           ('MetaStableRaman', 'channel_614_2'),
                           ('MetaStableRaman', 'frequency_614_2'),
                           ('MetaStableRaman', 'amplitude_614_2'),
                           ('MetaStableRaman', 'AOM_TTL_614_1'),
                           ('MetaStableRaman', 'AOM_TTL_614_2'),
                           ]

    def sequence(self):
        # start time is defined to be 0s.
        p = self.parameters.MetaStableRaman

        amp_off = WithUnit(-47.0,'dBm')
        switch_on_delay = WithUnit(2.0,'us')

        # add a small delay for the switching on
        amp_change_delay = WithUnit(350.0,'ns')

        if p.raman_duration != 0:
            self.addDDS(p.channel_614_1, self.start - amp_change_delay,\
                         switch_on_delay, p.frequency_614_1, amp_off)
            self.addDDS(p.channel_614_2, self.start - amp_change_delay,\
                        switch_on_delay, p.frequency_614_2, amp_off)
    
            self.addDDS(p.channel_614_1, self.start - amp_change_delay + switch_on_delay, \
                         p.raman_duration, p.frequency_614_1, p.amplitude_614_1)
            self.addDDS(p.channel_614_2, self.start - amp_change_delay+ switch_on_delay, \
                         p.raman_duration, p.frequency_614_2, p.amplitude_614_2)
    
            
            self.addTTL(p.AOM_TTL_614_1, self.start + switch_on_delay, p.raman_duration)
            self.addTTL(p.AOM_TTL_614_2, self.start + switch_on_delay, p.raman_duration)

        self.end = self.start +  amp_change_delay + switch_on_delay\
                    + p.raman_duration + switch_on_delay

