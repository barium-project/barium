from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit
from random import *

class microwaves_133(pulse_sequence):

    required_parameters = [
                           ('Microwaves133', 'microwave_duration'),
                           ('Microwaves133', 'TTL1_microwaves'),
                           ('Microwaves133', 'channel_microwaves'),
                           ('Microwaves133', 'frequency_microwaves'),
                           ('Microwaves133', 'amplitude_microwaves'),
                           ('Microwaves133', 'LO_frequency'),
                           ('Microwaves133', 'TTL_493_DDS'),
                           ('Microwaves133', 'TTL_493_SD'),
                           ('Microwaves133', 'TTL_493'),
                           ('Microwaves133', 'use_random_phase'),
                           ('Microwaves133', 'random_phase'),
                           ]


    def sequence(self):
        # start time is defined to be 0s.
        p = self.parameters.Microwaves133



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




