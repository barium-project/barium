from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit
from random import *

class second_microwaves_133(pulse_sequence):

    required_parameters = [
                           ('SecondMicrowaves133', 'microwave_duration'),
                           ('SecondMicrowaves133', 'TTL1_microwaves'),
                           ('SecondMicrowaves133', 'channel_microwaves'),
                           ('SecondMicrowaves133', 'frequency_microwaves'),
                           ('SecondMicrowaves133', 'amplitude_microwaves'),
                           ('SecondMicrowaves133', 'LO_frequency'),
                           ('SecondMicrowaves133', 'TTL_493_DDS'),
                           ('SecondMicrowaves133', 'TTL_493_SD'),
                           ('SecondMicrowaves133', 'TTL_493'),
                           ('SecondMicrowaves133', 'use_random_phase'),
                           ('SecondMicrowaves133', 'random_phase'),
                           ]


    def sequence(self):
        # start time is defined to be 0s.
        p = self.parameters.SecondMicrowaves133



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

        #print p.random_phase

        if p.microwave_duration != 0:
            #We want to leave the DDS on, so we'll use two fast microwave switches to turn things on and off
            self.addTTL(p.TTL1_microwaves, self.start + switch_on_delay - amp_change_delay, p.microwave_duration)      
            self.addTTL(p.TTL_493_DDS, self.start, p.microwave_duration + 2*switch_on_delay)
            self.addTTL(p.TTL_493, self.start, p.microwave_duration + 2*switch_on_delay)


            self.addDDS(p.channel_microwaves, self.start , p.microwave_duration + switch_on_delay, \
                    dds_freq, p.amplitude_microwaves, phase = WithUnit(p.random_phase %  360.0 , 'deg'))

            self.end = self.start + switch_on_delay +  p.microwave_duration + switch_on_delay

        else:
            self.end = self.start




