from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit


class shelving_133_585_sub(pulse_sequence):

    required_parameters = [
                           ('Shelving133_585_Sub', 'shelving_duration'),
                           ('Shelving133_585_Sub', 'TTL_585'),
                           ('Shelving133_585_Sub', 'channel_493'),
                           ('Shelving133_585_Sub', 'frequency_493'),
                           ('Shelving133_585_Sub', 'amplitude_493'),
                           ]


    def sequence(self):
        # start time is defined to be 0s.
        p = self.parameters.Shelving133_585_Sub

       # use this to turn the DDS to a very low power right before we turn it on
        # to avoid the weird 1us loss.
        amp_off = WithUnit(-47.0,'dBm')
        switch_on_delay = WithUnit(2.0,'us')

        # add a small delay for the switching on
        amp_change_delay = WithUnit(350.0,'ns')

##Turning on the 493 and 585 for shelving into the D_{5/2}
        if p.shelving_duration != 0:
            
            # Turn on 493 laser
            self.addDDS(p.channel_493, self.start - amp_change_delay,\
                    switch_on_delay, p.frequency_493, amp_off)

            self.addDDS(p.channel_493, self.start + switch_on_delay - amp_change_delay, \
                    p.shelving_duration, p.frequency_493, p.amplitude_493)
            # Turn on 585
            self.addTTL(p.TTL_585, self.start + switch_on_delay, p.shelving_duration)  
            # Finish sequence with time buffer
            self.end = self.start + switch_on_delay + p.shelving_duration + switch_on_delay





