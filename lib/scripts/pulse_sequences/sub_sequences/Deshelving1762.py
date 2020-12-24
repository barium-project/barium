from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class deshelving_1762(pulse_sequence):

    required_parameters = [
                           ('Deshelving1762', 'deshelving_duration'),
                           ('Deshelving1762', 'TTL_1762_eom'),
                           ('Deshelving1762', 'channel_493'),
                           ('Deshelving1762', 'frequency_493'),
                           ('Deshelving1762', 'amplitude_493'),
                           ]


    def sequence(self):
        # start time is defined to be 0s.
        p = self.parameters.Deshelving1762

        # time for DDS to turn on
        amp_change_delay = WithUnit(600.0,'ns')
        # buffer before we start deshelving
        switch_on_delay = WithUnit(2.0,'us')

        if p.Deshelving_duration != 0:

            self.addDDS(p.channel_493, self.start - amp_change_delay +\
                switch_on_delay, p.deshelving_duration, p.frequency_493,\
                p.amplitude_493)
        
            self.addTTL(p.TTL_1762_eom, self.start + switch_on_delay,\
                        p.deshelving_duration)    
            # add another buffer at the end of the sequence with another
            # switch_on_delay
            self.end = self.start + switch_on_delay +  p.shelving_duration\
            + switch_on_delay

        else:
            self.end = self.start




