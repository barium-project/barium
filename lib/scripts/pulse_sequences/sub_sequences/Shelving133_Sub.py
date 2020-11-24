from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit


class shelving_133_sub(pulse_sequence):

    required_parameters = [
                           ('Shelving133_Sub', 'shelving_duration'),
                           ('Shelving133_Sub', 'TTL_455'),
                           ('Shelving133_Sub', 'TTL_585'),
                           ('Shelving133_Sub', 'TTL_650'),
                           ('Shelving133_Sub', 'TTL_493'),
                           ('Shelving133_Sub', 'TTL_prep'),
                           ('Shelving133_Sub', 'TTL_493_DDS'),
                           ('Shelving133_Sub', 'TTL_493_SD'),
                           ('Shelving133_Sub', 'channel_650'),
                           ('Shelving133_Sub', 'frequency_650'),
                           ('Shelving133_Sub', 'amplitude_650'),
                           ('Shelving133_Sub', 'channel_493'),
                           ('Shelving133_Sub', 'frequency_493'),
                           ('Shelving133_Sub', 'amplitude_493'),
                           ]


    def sequence(self):
        # start time is defined to be 0s.
        p = self.parameters.Shelving133_Sub

       # use this to turn the DDS to a very low power right before we turn it on
        # to avoid the weird 1us loss.
        amp_off = WithUnit(-47.0,'dBm')
        switch_on_delay = WithUnit(2.0,'us')

        # add a small delay for the switching on
        amp_change_delay = WithUnit(350.0,'ns')

        #self.addDDS(p.channel_493, self.start - amp_change_delay,\
                     #switch_on_delay, p.frequency_493, WithUnit(-48.0,'dBm'))
#        self.addDDS(p.channel_650, self.start - amp_change_delay,\
#                    switch_on_delay, p.frequency_650, amp_off)

        #self.addDDS(p.channel_493, self.start + switch_on_delay - amp_change_delay, \
                    #p.shelving_duration, p.frequency_493, p.amplitude_493)


        self.addDDS(p.channel_650, self.start + switch_on_delay - amp_change_delay, \
                     p.shelving_duration, p.frequency_650, p.amplitude_650)

        if p.shelving_duration != 0:
            self.addTTL(p.TTL_455, self.start + switch_on_delay, p.shelving_duration)
            self.addTTL(p.TTL_585, self.start + switch_on_delay, p.shelving_duration)


        self.addTTL(p.TTL_650, self.start, p.shelving_duration  + 2*switch_on_delay)
        #self.addTTL(p.TTL_493, self.start, p.shelving_duration + 2*switch_on_delay)
        #self.addTTL(p.TTL_prep, self.start, p.shelving_duration + 2*switch_on_delay)

        # If we want the 493 on turn on during shelving comment out TTL_493_DDS line below
        self.addTTL(p.TTL_493_DDS, self.start, p.shelving_duration + 2*switch_on_delay)

        # If we want the 493 on turn on the 493 DDS rf switch
#b #       self.addTTL(p.TTL_493_DDS, self.start, p.shelving_duration + 2*switch_on_delay)

  
        self.end = self.start + switch_on_delay + p.shelving_duration + switch_on_delay





