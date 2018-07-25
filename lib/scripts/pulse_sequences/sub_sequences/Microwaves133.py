from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit


class microwaves_133(pulse_sequence):

    required_parameters = [
                           ('Microwaves133', 'microwave_duration'),
                           ('Microwaves133', 'switch_duration'),
                           ('Microwaves133', 'TTL1_microwaves'),
                           ('Microwaves133', 'TTL2_microwaves'),
                           ('Microwaves133', 'channel_microwaves'),
                           ('Microwaves133', 'frequency_microwaves'),
                           ('Microwaves133', 'amplitude_microwaves'),
                           ('Microwaves133', 'LO_frequency'),
                           ]


    def sequence(self):
        # start time is defined to be 0s.
        p = self.parameters.Microwaves133



        # use this to turn the DDS to a very low power right before we turn it on
        # to avoid the weird 1us loss.
        amp_off = WithUnit(-47.0,'dBm')
        switch_on_delay = WithUnit(2.0,'us')
        amp_change_delay = WithUnit(335.0,'ns')
        dds_freq = p.frequency_microwaves - p.LO_frequency

        if p.microwave_duration != 0:
            #We want to leave the DDS on, so we'll use two fast microwave switches to turn things on and off
            self.addTTL(p.TTL1_microwaves, self.start + switch_on_delay, p.microwave_duration)
            self.addTTL(p.TTL2_microwaves, self.start + switch_on_delay, p.microwave_duration)

        # Turn the DDS on at low power
        self.addDDS(p.channel_microwaves, self.start - amp_change_delay, switch_on_delay, \
                    dds_freq, amp_off)

        self.addDDS(p.channel_microwaves, self.start + switch_on_delay - amp_change_delay, p.microwave_duration, \
                    dds_freq, p.amplitude_microwaves)

        self.end = self.start + switch_on_delay +  p.microwave_duration

