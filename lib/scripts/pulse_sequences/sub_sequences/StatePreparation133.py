from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from barium.lib.scripts.pulse_sequences.sub_sequences.DopplerCooling133 import doppler_cooling_133 as doppler_cooling_133
from labrad.units import WithUnit
"""
6/17/17
Need the Doppler cooling TTLs so we can turn off the sidebands
"""

class state_prep_133(pulse_sequence):

    required_parameters = [
                           ('StatePreparation133', 'state_prep_duration'),
                           ('StatePreparation133', 'TTL_prep'),
                           ('StatePreparation133', 'TTL_493'),
                           ('StatePreparation133', 'TTL_493_DDS'),
                           ('StatePreparation133', 'TTL_650'),
                           ('StatePreparation133', 'channel_493'),
                           ('StatePreparation133', 'frequency_493'),
                           ('StatePreparation133', 'amplitude_493'),
                           ('StatePreparation133', 'channel_650'),
                           ('StatePreparation133', 'frequency_650'),
                           ('StatePreparation133', 'amplitude_650'),
                           ]


    def sequence(self):
        # start time is defined to be 0s.
        p = self.parameters.StatePreparation133

        amp_off = WithUnit(-47.0,'dBm')
        switch_on_delay = WithUnit(2.0,'us')
        # add a small delay for the switching on
        amp_change_delay = WithUnit(335.0,'ns')


        self.addDDS(p.channel_493, self.start - amp_change_delay,\
                     switch_on_delay, p.frequency_493, amp_off)
        self.addDDS(p.channel_650, self.start - amp_change_delay,\
                    switch_on_delay, p.frequency_650, amp_off)

        self.addDDS(p.channel_493, self.start + switch_on_delay - amp_change_delay,\
                     p.state_prep_duration, p.frequency_493, p.amplitude_493)
        self.addDDS(p.channel_650, self.start + switch_on_delay - amp_change_delay, \
                     p.state_prep_duration, p.frequency_650, p.amplitude_650)

        if p.state_prep_duration != 0:
            self.addTTL(p.TTL_prep, self.start + switch_on_delay, p.state_prep_duration)
            self.addTTL(p.TTL_493, self.start + switch_on_delay, p.state_prep_duration)
            self.addTTL(p.TTL_493_DDS, self.start + switch_on_delay, p.state_prep_duration)
        self.end = self.start + switch_on_delay + p.state_prep_duration

