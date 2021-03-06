from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit
from random import *
'''
Test a standard spin echo pulse
'''

class spin_echo(pulse_sequence):

    required_parameters = [
                           ('SpinEcho', 'microwave_duration'),
                           ('SpinEcho', 'TTL1_microwaves'),
                           ('SpinEcho', 'TTL2_microwaves'),
                           ('SpinEcho', 'TTL_493_DDS'),
                           ('SpinEcho', 'TTL_493_SD'),
                           ('SpinEcho', 'TTL_493'),
                           ('SpinEcho', 'channel_microwaves'),
                           ('SpinEcho', 'frequency_microwaves'),
                           ('SpinEcho', 'amplitude_microwaves'),
                           ('SpinEcho', 'LO_frequency'),
                           ('SpinEcho', 'random_phase'),
                           ('SpinEcho', 'use_random_phase'),
                           ]


    def sequence(self):
        # start time is defined to be 0s.
        p = self.parameters.SpinEcho

        # use this to turn the DDS to a very low power right before we turn it on
        # to avoid the weird 1us loss.
        amp_off = WithUnit(-47.0,'dBm')
        switch_on_delay = WithUnit(1.00,'us')
        amp_change_delay = WithUnit(335.0,'ns')
        phase_change_delay = WithUnit(2.0, 'us')
        dds_freq = p.frequency_microwaves - p.LO_frequency

        if p.use_random_phase == '1':
            p.random_phase = random()*360.0

        else:
            p.random_phase = 0.0
        print p.random_phase

        if p.microwave_duration != 0:
            # Make sure bad things don't turn on
            self.addTTL(p.TTL_493_DDS, self.start, 2*p.microwave_duration + 3*phase_change_delay + 2*switch_on_delay)
            self.addTTL(p.TTL_493, self.start, 2*p.microwave_duration + 3*phase_change_delay + 2*switch_on_delay)

            self.addDDS(p.channel_microwaves, self.start - amp_change_delay, switch_on_delay, \
                    dds_freq, amp_off)

            dds_start = self.start + switch_on_delay - amp_change_delay

            # Pulse 1 pi/2
            self.addDDS(p.channel_microwaves, dds_start, p.microwave_duration/2 + phase_change_delay, \
                        dds_freq, p.amplitude_microwaves, phase = WithUnit((0.0 + p.random_phase) %  360.0 , 'deg'))

            self.addTTL(p.TTL1_microwaves, self.start + phase_change_delay, p.microwave_duration/2)
            self.addTTL(p.TTL2_microwaves, self.start + phase_change_delay, p.microwave_duration/2)

            # Pulse 2 pi
            self.addDDS(p.channel_microwaves, dds_start + p.microwave_duration/2 + phase_change_delay, p.microwave_duration + phase_change_delay, \
                        dds_freq, p.amplitude_microwaves, phase = WithUnit((90.0 + p.random_phase) % 360.0   , 'deg'))

            self.addTTL(p.TTL1_microwaves, self.start + 2*phase_change_delay + p.microwave_duration/2, p.microwave_duration)
            self.addTTL(p.TTL2_microwaves, self.start + 2*phase_change_delay + p.microwave_duration/2, p.microwave_duration)


            # Pulse 3 pi/2
            self.addDDS(p.channel_microwaves, dds_start + 1.5*p.microwave_duration + 2*phase_change_delay , p.microwave_duration/2 + phase_change_delay, \
                        dds_freq, p.amplitude_microwaves, phase = WithUnit((0.0 + p.random_phase) % 360.0   , 'deg'))

            self.addTTL(p.TTL1_microwaves, self.start + 3*phase_change_delay + 1.5*p.microwave_duration, p.microwave_duration/2)
            self.addTTL(p.TTL2_microwaves, self.start + 3*phase_change_delay + 1.5*p.microwave_duration, p.microwave_duration/2)


            # adding extra time at the end to make sure the microwaves are off
            self.end = self.start + 2*switch_on_delay + 2*p.microwave_duration + 3*phase_change_delay
        else:
            self.end = self.start
