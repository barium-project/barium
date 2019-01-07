from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit
from random import *

class composite_4(pulse_sequence):

    required_parameters = [
                           ('Composite4', 'microwave_duration'),
                           ('Composite4', 'TTL1_microwaves'),
                           ('Composite4', 'TTL2_microwaves'),
                           ('Composite4', 'channel_microwaves'),
                           ('Composite4', 'frequency_microwaves'),
                           ('Composite4', 'amplitude_microwaves'),
                           ('Composite4', 'LO_frequency'),
                           ('Composite4', 'TTL_493_DDS'),
                           ('Composite4', 'TTL_493_SD'),
                           ('Composite4', 'TTL_493'),
                           ('Composite4', 'use_random_phase'),
                           ('Composite4', 'random_phase'),
                           ('Composite4', 'delay_duration'),
                           ]


    def sequence(self):
        # start time is defined to be 0s.
        p = self.parameters.Composite4



        # use this to turn the DDS to a very low power right before we turn it on
        # to avoid the weird 1us loss.
        amp_off = WithUnit(-47.0,'dBm')
        switch_on_delay = WithUnit(2.0,'us')
        amp_change_delay = WithUnit(355.0,'ns')
        dds_freq = p.frequency_microwaves - p.LO_frequency

        if p.use_random_phase == '1':
            p.random_phase = random()*360.0

        else:
            p.random_phase = 0.0

        print p.random_phase

        if p.microwave_duration != 0:
            #We want to leave the DDS on, so we'll use two fast microwave switches to turn things on and off
            self.addTTL(p.TTL1_microwaves, self.start + switch_on_delay - amp_change_delay, p.microwave_duration)
            self.addTTL(p.TTL2_microwaves, self.start + switch_on_delay - amp_change_delay, p.microwave_duration)
            self.addTTL(p.TTL_493_DDS, self.start, p.microwave_duration + 2*switch_on_delay + p.delay_duration)
            self.addTTL(p.TTL_493, self.start, p.microwave_duration + 2*switch_on_delay + p.delay_duration)


            self.addDDS(p.channel_microwaves, self.start , p.microwave_duration + switch_on_delay, \
                    dds_freq, p.amplitude_microwaves, phase = WithUnit(p.random_phase %  360.0 , 'deg'))

            self.end = self.start + switch_on_delay +  p.microwave_duration + p.delay_duration +  switch_on_delay

        else:
            self.end = self.start




