from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from barium.lib.scripts.pulse_sequences.sub_sequences.DopplerCooling133 import doppler_cooling_133 as doppler_cooling_133
from labrad.units import WithUnit as U
"""
6/17/17
Need the Doppler cooling TTLs so we can turn off the sidebands
"""

class state_prep_133(pulse_sequence):

    required_parameters = [
                           ('StatePreparation133', 'state_prep_duration'),
                           ('StatePreparation133', 'TTL_prep'),
                           ('StatePreparation133', 'TTL_493'),
                           ('StatePreparation133', 'TTL_650')
                           ]

    #required_parameters.extend(doppler_cooling_133.all_required_parameters())

    def sequence(self):
        # start time is defined to be 0s.
        p = self.parameters.StatePreparation133

        self.ttl_state_prep = p.TTL_prep
        self.ttl_493 = p.TTL_493
        switch_delay = U(50,'ns')

        self.addTTL(self.ttl_state_prep, self.start, p.state_prep_duration)
        self.addTTL(self.ttl_493, self.start, p.state_prep_duration)
        self.end = self.start + p.state_prep_duration + switch_delay

