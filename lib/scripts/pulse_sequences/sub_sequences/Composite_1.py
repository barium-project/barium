from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

'''
This is the sequence referenced in Ryan, C. A., et. al
"Robust Decoupling Techniques to Extend Quantum Coherence in Diamond" as
attributed to Dr. E. Knill
'''

class composite_1(pulse_sequence):

    required_parameters = [
                           ('Composite1', 'microwave_duration'),
                           ('Composite1', 'switch_duration'),
                           ('Composite1', 'TTL1_microwaves'),
                           ('Composite1', 'TTL2_microwaves'),
                           ('Composite1', 'TTL_493_DDS'),
                           ('Composite1', 'TTL_493'),
                           ('Composite1', 'channel_microwaves'),
                           ('Composite1', 'frequency_microwaves'),
                           ('Composite1', 'amplitude_microwaves'),
                           ('Composite1', 'LO_frequency'),
                           ]


    def sequence(self):
        # start time is defined to be 0s.
        p = self.parameters.Composite1

        # use this to turn the DDS to a very low power right before we turn it on
        # to avoid the weird 1us loss.
        amp_off = WithUnit(-47.0,'dBm')
        switch_on_delay = WithUnit(2.0,'us')
        amp_change_delay = WithUnit(335.0,'ns')
        phase_change_delay = WithUnit(200.0, 'ns')
        dds_freq = p.frequency_microwaves - p.LO_frequency

        if p.microwave_duration != 0:
            #We want to leave the DDS on, so we'll use two fast microwave switches to turn things on and off
            self.addTTL(p.TTL1_microwaves, self.start + switch_on_delay, 5*p.microwave_duration)
            self.addTTL(p.TTL2_microwaves, self.start + switch_on_delay, 5*p.microwave_duration)
            self.addTTL(p.TTL_493_DDS, self.start, 5*p.microwave_duration + 2*switch_on_delay)
            self.addTTL(p.TTL_493, self.start, 5*p.microwave_duration + 2*switch_on_delay)
        # Turn the DDS on at low power
        self.addDDS(p.channel_microwaves, self.start - amp_change_delay, switch_on_delay, \
                    dds_freq, amp_off)

        # Here we need to start the sequence early to account for the turn on delay, and end it early to account
        # for the phase delay.
        dds_start = self.start + switch_on_delay - amp_change_delay

        self.addDDS(p.channel_microwaves, dds_start, p.microwave_duration - phase_change_delay, \
                    dds_freq, p.amplitude_microwaves)


        self.addDDS(p.channel_microwaves, dds_start + p.microwave_duration - phase_change_delay, p.microwave_duration, \
                    dds_freq, p.amplitude_microwaves, phase = WithUnit(180.0,'deg'))


        self.addDDS(p.channel_microwaves, dds_start - phase_change_delay + 2*p.microwave_duration , p.microwave_duration, \
                    dds_freq, p.amplitude_microwaves, phase = WithUnit(0.0,'deg'))

        self.addDDS(p.channel_microwaves, dds_start - phase_change_delay + 3*p.microwave_duration , p.microwave_duration, \
                    dds_freq, p.amplitude_microwaves, phase = WithUnit(180.0,'deg'))

        # The last pulse needs the phase delay added to the duration
        self.addDDS(p.channel_microwaves, dds_start - phase_change_delay + 4*p.microwave_duration, p.microwave_duration + phase_change_delay, \
                    dds_freq, p.amplitude_microwaves, phase = WithUnit(0.0,'deg'))

        # adding extra time at the end to make sure the microwaves are off
        self.end = self.start + + 2*switch_on_delay + 5*p.microwave_duration
