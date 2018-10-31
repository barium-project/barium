from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit


class ramsey_delay(pulse_sequence):

    required_parameters = [
                           ('RamseyDelay', 'ramsey_delay'),
                           ('RamseyDelay', 'microwave_duration'),
                           ('RamseyDelay', 'TTL1_microwaves'),
                           ('RamseyDelay', 'TTL2_microwaves'),
                           ('RamseyDelay', 'channel_microwaves'),
                           ('RamseyDelay', 'frequency_microwaves'),
                           ('RamseyDelay', 'amplitude_microwaves'),
                           ('RamseyDelay', 'LO_frequency'),
                           ('RamseyDelay', 'TTL_493_DDS'),
                           ('RamseyDelay', 'TTL_493'),
                           ]


    def sequence(self):
        # start time is defined to be 0s.
        p = self.parameters.RamseyDelay



        # use this to turn the DDS to a very low power right before we turn it on
        # to avoid the weird 1us loss.
        amp_off = WithUnit(-47.0,'dBm')
        switch_on_delay = WithUnit(2.0,'us')
        amp_change_delay = WithUnit(355.0,'ns')
        dds_freq = p.frequency_microwaves - p.LO_frequency

        if p.microwave_duration != 0:
            # Make sure no 493 is on
            self.addTTL(p.TTL_493_DDS, self.start, 2*p.microwave_duration + p.ramsey_delay + 2*switch_on_delay)
            self.addTTL(p.TTL_493, self.start, 2*p.microwave_duration + p.ramsey_delay + 2*switch_on_delay)

            # Turn the DDS on at low power
            self.addDDS(p.channel_microwaves, self.start - amp_change_delay, switch_on_delay , \
                    dds_freq, amp_off)

            self.addDDS(p.channel_microwaves, self.start + switch_on_delay - amp_change_delay, 2*p.microwave_duration + p.ramsey_delay, \
                    dds_freq, p.amplitude_microwaves)

            #We want to leave the DDS on, so we'll use two fast microwave switches to turn things on and off
            self.addTTL(p.TTL1_microwaves, self.start + switch_on_delay, p.microwave_duration)
            self.addTTL(p.TTL2_microwaves, self.start + switch_on_delay, p.microwave_duration)

            self.addTTL(p.TTL1_microwaves, self.start + switch_on_delay + p.microwave_duration + p.ramsey_delay, p.microwave_duration)
            self.addTTL(p.TTL2_microwaves, self.start + switch_on_delay + p.microwave_duration + p.ramsey_delay, p.microwave_duration)


            self.end = self.start + switch_on_delay +  2*p.microwave_duration + p.ramsey_delay + switch_on_delay

        else:
            self.end = self.start




