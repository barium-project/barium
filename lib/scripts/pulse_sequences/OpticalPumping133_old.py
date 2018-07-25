from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit



class optical_pumping_133(pulse_sequence):

    required_parameters = [
                           ('OpticalPumping133', 'channel_493'),
                           ('OpticalPumping133', 'frequency_493'),
                           ('OpticalPumping133', 'amplitude_493'),
                           ('OpticalPumping133', 'channel_650'),
                           ('OpticalPumping133', 'frequency_650'),
                           ('OpticalPumping133', 'amplitude_650'),
                           ('OpticalPumping133', 'amplitude_650_shelving'),
                           ('OpticalPumping133', 'channel_455'),
                           ('OpticalPumping133', 'frequency_455'),
                           ('OpticalPumping133', 'amplitude_455'),
                           ('OpticalPumping133', 'channel_585'),
                           ('OpticalPumping133', 'frequency_585'),
                           ('OpticalPumping133', 'amplitude_585'),
                           ('OpticalPumping133', 'doppler_cooling_duration'),
                           ('OpticalPumping133', 'state_prep_duration'),
                           ('OpticalPumping133', 'state_detection_duration'),
                           ('OpticalPumping133', 'shelving_duration'),
                           ('OpticalPumping133', 'deshelving_duration'),
                           ('OpticalPumping133', 'TTL_493'),
                           ('OpticalPumping133', 'TTL_650'),
                           ('OpticalPumping133', 'TTL_prep'),
                           ('OpticalPumping133', 'TTL_deshelve'),
                           ('OpticalPumping133', 'Cycles'),
                           ('OpticalPumping133', 'Start_Time'),
                           ('OpticalPumping133', 'Stop_Time'),
                           ('OpticalPumping133', 'Time_Step'),
                           ('OpticalPumping133', 'State_Detection'),
                           ('OpticalPumping133', 'Mode')
                           ]

    required_subsequences = []

    def sequence(self):
        self.start = WithUnit(10.0,'us')
        self.t0 = self.start - WithUnit(1.0,'us')
        self.p = self.parameters.OpticalPumping133

        self.channel_493 = self.p.channel_493
        self.freq_493 = self.p.frequency_493
        self.amp_493 = self.p.amplitude_493

        self.channel_650 = self.p.channel_650
        self.freq_650 = self.p.frequency_650
        self.amp_650 = self.p.amplitude_650
        self.amp_650_shelving = self.p.amplitude_650_shelving

        self.channel_455 = self.p.channel_455
        self.freq_455 = self.p.frequency_455
        self.amp_455 = self.p.amplitude_455

        self.channel_585 = self.p.channel_585
        self.freq_585  = self.p.frequency_585
        self.amp_585 = self.p.amplitude_585

        self.ttl_493 = self.p.TTL_493
        self.ttl_650 = self.p.TTL_650
        self.ttl_prep = self.p.TTL_prep
        self.ttl_deshelve = self.p.TTL_deshelve
        self.state_detection = self.p.State_Detection

        self.cool_time = self.p.doppler_cooling_duration
        self.prep_time = self.p.state_prep_duration
        self.shelving_time = self.p.shelving_duration
        self.deshelving_time = self.p.deshelving_duration
        self.sd_time = self.p.state_detection_duration
        self.switch_time = WithUnit(1.0,'us') #


        if self.state_detection == 'spin-1/2':
            self.addDDS(self.channel_493, self.t0,  self.cool_time + self.prep_time + self.sd_time, \
                         self.freq_493, self.amp_493)
            # First Doppler cool which is doing nothing
            # Next optically pump by turning off 5.8GHz and 1.84GHz on
            self.addTTL(self.ttl_493, self.start + self.cool_time, self.prep_time + self.sd_time)
            self.addTTL(self.ttl_prep, self.start + self.cool_time, self.prep_time)
            # Next apply microwaves and turn off everything else
            # DDS will turn off from above setting
            self.addTTL(self.ttl_650, self.start + self.cool_time + self.prep_time, \
                        + self.sd_time)

            # Turn on photon counting for state detection
            self.addTTL('ReadoutCount', self.start + self.cool_time + self.prep_time \
                       , self.sd_time)

        if self.state_detection == 'shelving':
            self.addDDS(self.channel_493, self.t0,  self.cool_time + self.prep_time , self.freq_493, self.amp_493)
            self.addDDS(self.channel_650, self.t0,  self.cool_time + self.prep_time , self.freq_650, self.amp_650)
            # First Doppler cool which is doing nothing
            # Next optically pump by turning off 5.8GHz and 1.84GHz on
            self.addTTL(self.ttl_493, self.start + self.cool_time, self.prep_time + self.switch_time \
                        + self.shelving_time)
            self.addTTL(self.ttl_prep, self.start + self.cool_time, self.prep_time)
            # Next apply microwaves and turn off everything else
            # DDS will turn off from above setting
            self.addTTL(self.ttl_650, self.start + self.cool_time + self.prep_time, self.switch_time + \
                        self.shelving_time)
            # Turn on shelving lasers
            # Need to send 455 & 585 through an RF switch
            if self.shelving_time != 0:
                self.addTTL('TTL8', self.start + self.cool_time + self.prep_time + \
                         self.switch_time, self.shelving_time)
                self.addTTL('TTL9', self.start + self.cool_time + self.prep_time + \
                         self.switch_time, self.shelving_time)

                #self.addDDS(self.channel_455, self.t0 + self.cool_time + self.prep_time + self.switch_time \
                        #, self.shelving_time, self.freq_455, self.amp_455)
                #Turn on low power 650
                self.addDDS(self.channel_650, self.t0 +  self.cool_time + self.prep_time + self.switch_time \
                        , self.shelving_time , self.freq_650, self.amp_650_shelving)
                #self.addDDS(self.channel_585, self.t0 + self.cool_time + self.prep_time + self.switch_time \
                        #, self.shelving_time, self.freq_585, self.amp_585)


            # Turn the dds back on for state detection
            self.addDDS(self.channel_493, self.t0 + self.cool_time + self.prep_time + self.switch_time + \
                        self.shelving_time, self.sd_time + self.deshelving_time, self.freq_493, self.amp_493)
            self.addDDS(self.channel_650, self.t0 + self.cool_time + self.prep_time + self.switch_time + \
                        self.shelving_time, self.sd_time + self.deshelving_time, self.freq_650, self.amp_650)
            # Turn on photon counting for state detection
            self.addTTL('ReadoutCount', self.start + self.cool_time + self.prep_time + self.switch_time + \
                        self.shelving_time, self.sd_time)

            # Turn on deshelving LED
            self.addTTL(self.ttl_deshelve, self.start + self.cool_time + self.prep_time + self.switch_time + \
                        self.shelving_time + self.sd_time, self.deshelving_time)

