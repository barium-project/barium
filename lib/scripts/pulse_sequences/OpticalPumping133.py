from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit



class optical_pumping_133(pulse_sequence):

    required_parameters = [('OpticalPumping133', 'dds_channel'),
                           ('OpticalPumping133', 'dds_frequency'),
                           ('OpticalPumping133', 'dds_amplitude'),
                           ('OpticalPumping133', 'doppler_cooling_duration'),
                           ('OpticalPumping133', 'state_prep_duration'),
                           ('OpticalPumping133', 'state_detection_duration'),
                           ('OpticalPumping133', 'TTL_493'),
                           ('OpticalPumping133', 'TTL_650'),
                           ('OpticalPumping133', 'TTL_prep'),
                           ('OpticalPumping133', 'Cycles')
                           ]

    required_subsequences = []

    def sequence(self):
        self.start = WithUnit(10.0,'us')
        self.p = self.parameters.OpticalPumping133

        self.channel = self.p.dds_channel
        self.freq = self.p.dds_frequency
        self.amp = self.p.dds_amplitude
        self.ttl_493 = self.p.TTL_493
        self.ttl_650 = self.p.TTL_650
        self.ttl_prep = self.p.TTL_prep


        self.cool_time = self.p.doppler_cooling_duration
        self.prep_time = self.p.state_prep_duration
        self.sd_time = self.p.state_detection_duration

        self.switch_time = WithUnit(1.0,'us')
        self.total_time = self.cool_time + self.prep_time + self.sd_time + self.switch_time


        self.addDDS(self.channel, self.start,  self.total_time, self.freq, self.amp)
        self.start += self.switch_time


        # First Doppler cool which is doing nothing
        # Next optically pump by turning off 5.8GHz and 1.84GHz on
        self.addTTL(self.ttl_493, self.start + self.cool_time, self.prep_time + self.sd_time)
        self.addTTL(self.ttl_prep, self.start + self.cool_time, self.prep_time)
        # Now state detect by turning off 904MHz
        self.addTTL(self.ttl_650, self.start + self.cool_time + self.prep_time, self.sd_time)
        self.addTTL('ReadoutCount', self.start + self.cool_time + self.prep_time, self.sd_time)




