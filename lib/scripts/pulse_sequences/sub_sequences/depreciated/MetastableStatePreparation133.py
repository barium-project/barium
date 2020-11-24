from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from barium.lib.scripts.pulse_sequences.sub_sequences.DopplerCooling133 import doppler_cooling_133 as doppler_cooling_133
from labrad.units import WithUnit
"""
6/17/17
Need the Doppler cooling TTLs so we can turn off the sidebands
"""

class metastable_state_prep_133(pulse_sequence):

    required_parameters = [
                           ('MetastableStatePreparation133', 'state_prep_duration'),
                           ('MetastableStatePreparation133', 'TTL_455'),
                           ('MetastableStatePreparation133', 'TTL_493'),
                           ('MetastableStatePreparation133', 'TTL_prep'),
                           ('MetastableStatePreparation133', 'channel_493'),
                           ('MetastableStatePreparation133', 'frequency_493'),
                           ('MetastableStatePreparation133', 'amplitude_493'),
                           ('MetastableStatePreparation133', 'channel_650'),
                           ('MetastableStatePreparation133', 'frequency_650'),
                           ('MetastableStatePreparation133', 'amplitude_650'),
                           ('MetastableStatePreparation133', 'TTL_614'),        #int channel number
                           ('MetastableStatePreparation133', 'TTL_614_F12'),
                           ('MetastableStatePreparation133', 'TTL_614_F22'),
                           ('MetastableStatePreparation133', 'USE_TTL_614'),    #bool on/off
                           ('MetastableStatePreparation133', 'USE_TTL_614_F12'),
                           ('MetastableStatePreparation133', 'USE_TTL_614_F22'),
                           ]


    def sequence(self):
        # start time is defined to be 0s.
        p = self.parameters.MetastableStatePreparation133

        # add a small delay for the switching on
        amp_change_delay = WithUnit(2.0,'us')
        amp_change_delay_2 = WithUnit(350.0,'ns')


        if p.state_prep_duration != 0:

            self.addDDS(p.channel_493, self.start - amp_change_delay_2,\
                     p.state_prep_duration - amp_change_delay_2, p.frequency_493, p.amplitude_493)
            self.addDDS(p.channel_650, self.start - amp_change_delay_2, \
                     p.state_prep_duration - amp_change_delay_2 + amp_change_delay, p.frequency_650, p.amplitude_650)

            # Turn off 625 MHz for prep, need 455 nm on and 614 nm + 80 MHz SB
            self.addTTL(p.TTL_493, self.start, p.state_prep_duration)
            self.addTTL(p.TTL_455, self.start, p.state_prep_duration)
            self.addTTL(p.TTL_prep, self.start, p.state_prep_duration)
            #self.addTTL(p.TTL_614_Prep, self.start, p.state_prep_duration)
            #self.addTTL(p.TTL_614, self.start, p.state_prep_duration)

            if  p.USE_TTL_614 == 'True':
                self.addTTL(p.TTL_614, self.start, p.state_prep_duration)

            if  p.USE_TTL_614_F12 == 'True':
                self.addTTL(p.TTL_614_F12, self.start, p.state_prep_duration)

            if  p.USE_TTL_614_F22 == 'True':
                self.addTTL(p.TTL_614_F22, self.start, p.state_prep_duration)




        self.end = self.start + p.state_prep_duration + amp_change_delay

