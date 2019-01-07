from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit
from random import *
'''
This is the sequence referenced in Ryan, C. A., et. al
"Robust Decoupling Techniques to Extend Quantum Coherence in Diamond" as
attributed to Dr. E. Knill
'''

class composite_2(pulse_sequence):

    required_parameters = [
                           ('Composite2', 'microwave_duration'),
                           ('Composite2', 'TTL1_microwaves'),
                           ('Composite2', 'TTL2_microwaves'),
                           ('Composite2', 'TTL_493_DDS'),
                           ('Composite2', 'TTL_493_SD'),
                           ('Composite2', 'TTL_493'),
                           ('Composite2', 'channel_microwaves'),
                           ('Composite2', 'frequency_microwaves'),
                           ('Composite2', 'amplitude_microwaves'),
                           ('Composite2', 'LO_frequency'),
                           ('Composite2', 'random_phase'),
                           ('Composite2', 'use_random_phase'),

                           ]


    def sequence(self):
        # start time is defined to be 0s.
        p = self.parameters.Composite2

        # use this to turn the DDS to a very low power right before we turn it on
        # to avoid the weird 1us loss.
        amp_off = WithUnit(-47.0,'dBm')
        switch_on_delay = WithUnit(1.00,'us')
        amp_change_delay = WithUnit(335.0,'ns')
        phase_change_delay = WithUnit(6.0, 'us')
        dds_freq = p.frequency_microwaves - p.LO_frequency

        if p.use_random_phase == '1':
            p.random_phase = random()*360.0

        else:
            p.random_phase = 0.0
        print p.random_phase

        if p.microwave_duration != 0:
            # Make sure bad things don't turn on
            self.addTTL(p.TTL_493_DDS, self.start, 5*p.microwave_duration + 5*phase_change_delay + 2*switch_on_delay)
            self.addTTL(p.TTL_493, self.start, 5*p.microwave_duration + 5*phase_change_delay + 2*switch_on_delay)

            self.addDDS(p.channel_microwaves, self.start - amp_change_delay, switch_on_delay, \
                    dds_freq, amp_off)

            dds_start = self.start + switch_on_delay - amp_change_delay

            # Pulse 1
            self.addDDS(p.channel_microwaves, dds_start, p.microwave_duration + phase_change_delay, \
                        dds_freq, p.amplitude_microwaves, phase = WithUnit((30.0 + p.random_phase) %  360.0 , 'deg'))

            self.addTTL(p.TTL1_microwaves, self.start + phase_change_delay, p.microwave_duration)
            self.addTTL(p.TTL2_microwaves, self.start + phase_change_delay, p.microwave_duration)

            # Pulse 2
            self.addDDS(p.channel_microwaves, dds_start + p.microwave_duration + phase_change_delay, p.microwave_duration + phase_change_delay, \
                        dds_freq, p.amplitude_microwaves, phase = WithUnit((0.0 + p.random_phase) % 360.0   , 'deg'))

            self.addTTL(p.TTL1_microwaves, self.start + 2*phase_change_delay + p.microwave_duration, p.microwave_duration)
            self.addTTL(p.TTL2_microwaves, self.start + 2*phase_change_delay + p.microwave_duration, p.microwave_duration)


            # Pulse 3
            self.addDDS(p.channel_microwaves, dds_start + 2*p.microwave_duration + 2*phase_change_delay , p.microwave_duration + phase_change_delay, \
                        dds_freq, p.amplitude_microwaves, phase = WithUnit((90.0 + p.random_phase) % 360.0   , 'deg'))

            self.addTTL(p.TTL1_microwaves, self.start + 3*phase_change_delay + 2*p.microwave_duration, p.microwave_duration)
            self.addTTL(p.TTL2_microwaves, self.start + 3*phase_change_delay + 2*p.microwave_duration, p.microwave_duration)


            # Pulse 4
            self.addDDS(p.channel_microwaves, dds_start + 3*p.microwave_duration + 3*phase_change_delay , p.microwave_duration + phase_change_delay, \
                        dds_freq, p.amplitude_microwaves, phase = WithUnit((0.0 + p.random_phase) % 360.0   , 'deg'))

            self.addTTL(p.TTL1_microwaves, self.start + 4*phase_change_delay + 3*p.microwave_duration, p.microwave_duration)
            self.addTTL(p.TTL2_microwaves, self.start + 4*phase_change_delay + 3*p.microwave_duration, p.microwave_duration)

            # Pulse 5
            self.addDDS(p.channel_microwaves, dds_start + 4*p.microwave_duration + 4*phase_change_delay , p.microwave_duration + phase_change_delay, \
                        dds_freq, p.amplitude_microwaves, phase = WithUnit((30.0 + p.random_phase) % 360.0   , 'deg'))

            self.addTTL(p.TTL1_microwaves, self.start + 5*phase_change_delay + 4*p.microwave_duration, p.microwave_duration)
            self.addTTL(p.TTL2_microwaves, self.start + 5*phase_change_delay + 4*p.microwave_duration, p.microwave_duration)

            # adding extra time at the end to make sure the microwaves are off
            self.end = self.start + 2*switch_on_delay + 5*p.microwave_duration + 5*phase_change_delay
        else:
            self.end = self.start
