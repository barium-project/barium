from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit
from random import *
'''
This is the sequence referenced in Ryan, C. A., et. al
"Robust Decoupling Techniques to Extend Quantum Coherence in Diamond" as
attributed to Dr. E. Knill
'''

class composite_1(pulse_sequence):

    required_parameters = [
                           ('Composite1', 'microwave_duration'),
                           ('Composite1', 'TTL1_microwaves'),
                           ('Composite1', 'TTL2_microwaves'),
                           ('Composite1', 'TTL_493_DDS'),
                           ('Composite1', 'TTL_493_SD'),
                           ('Composite1', 'TTL_493'),
                           ('Composite1', 'channel_microwaves'),
                           ('Composite1', 'frequency_microwaves'),
                           ('Composite1', 'amplitude_microwaves'),
                           ('Composite1', 'LO_frequency'),
                           ('Composite1', 'random_phase'),
                           ('Composite1', 'use_random_phase'),
                           ]


    def sequence(self):
        # start time is defined to be 0s.
        p = self.parameters.Composite1

        # use this to turn the DDS to a very low power right before we turn it on
        # to avoid the weird 1us loss.
        amp_off = WithUnit(-47.0,'dBm')
        switch_on_delay = WithUnit(1.00,'us')
        amp_change_delay = WithUnit(335.0,'ns')
        phase_change_delay = WithUnit(225.0, 'ns')
        dds_freq = p.frequency_microwaves - p.LO_frequency

        if p.use_random_phase == '1':
            p.random_phase = WithUnit(random()*360.0,'deg')

        else:
            p.random_phase = WithUnit(0.0,'deg')
        print p.random_phase
        if p.microwave_duration != 0:
            #We want to leave the DDS on, so we'll use two fast microwave switches to turn things on and off
            self.addTTL(p.TTL1_microwaves, self.start + switch_on_delay + phase_change_delay, 5*p.microwave_duration)
            self.addTTL(p.TTL2_microwaves, self.start + switch_on_delay + phase_change_delay, 5*p.microwave_duration)
            self.addTTL(p.TTL_493_DDS, self.start - amp_change_delay, 5*p.microwave_duration + 2*switch_on_delay)
            self.addTTL(p.TTL_493, self.start - amp_change_delay, 5*p.microwave_duration + 2*switch_on_delay)
            # Turn the DDS on at low power
            self.addDDS(p.channel_microwaves, self.start - amp_change_delay, switch_on_delay, \
                    dds_freq, amp_off)

            # Here we need to start the sequence early to account for the turn on delay, and end it early to account
            # for the phase delay.
            dds_start = self.start + switch_on_delay - amp_change_delay

            self.addDDS(p.channel_microwaves, dds_start, p.microwave_duration, \
                        dds_freq, p.amplitude_microwaves, phase = WithUnit(30.0,'deg') + p.random_phase)


            self.addDDS(p.channel_microwaves, dds_start + p.microwave_duration, p.microwave_duration, \
                        dds_freq, p.amplitude_microwaves, phase = WithUnit(0.0,'deg')+ p.random_phase)


            self.addDDS(p.channel_microwaves, dds_start + 2*p.microwave_duration , p.microwave_duration, \
                        dds_freq, p.amplitude_microwaves, phase = WithUnit(90.0,'deg')+ p.random_phase)

            self.addDDS(p.channel_microwaves, dds_start + 3*p.microwave_duration , p.microwave_duration, \
                        dds_freq, p.amplitude_microwaves, phase = WithUnit(0.0,'deg')+ p.random_phase)

            # The last pulse needs the phase delay added to the duration
            self.addDDS(p.channel_microwaves, dds_start + 4*p.microwave_duration, p.microwave_duration + phase_change_delay + WithUnit(100.0,'ns'), \
                        dds_freq, p.amplitude_microwaves, phase = WithUnit(30.0,'deg')+ p.random_phase)


            # adding extra time at the end to make sure the microwaves are off
            self.end = self.start + 2*switch_on_delay + 5*p.microwave_duration
        else:
            self.end = self.start
