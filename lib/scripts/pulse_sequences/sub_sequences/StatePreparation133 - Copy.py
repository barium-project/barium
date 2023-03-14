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
                           ('StatePreparation133', 'TTL_493_SD'),
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

        # add a small delay for the switching on
        amp_change_delay = WithUnit(2.0,'us')
        amp_change_delay_2 = WithUnit(350.0,'ns')


        if p.state_prep_duration != 0:
            self.addDDS(p.channel_493, self.start - amp_change_delay_2,\
                     p.state_prep_duration - amp_change_delay_2, p.frequency_493, p.amplitude_493)
            self.addDDS(p.channel_650, self.start - amp_change_delay_2, \
                     p.state_prep_duration - amp_change_delay_2 + amp_change_delay, p.frequency_650, p.amplitude_650)

            #Need to make sure the 5.8 is off while turning off
            self.addTTL(p.TTL_493, self.start, p.state_prep_duration + amp_change_delay)
            self.addTTL(p.TTL_prep, self.start, p.state_prep_duration + amp_change_delay/2)
            self.addTTL(p.TTL_493_DDS, self.start+ p.state_prep_duration, amp_change_delay)


        self.end = self.start + p.state_prep_duration + amp_change_delay

