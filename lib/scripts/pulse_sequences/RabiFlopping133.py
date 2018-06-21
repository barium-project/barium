from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class rabi_flopping(pulse_sequence):

    required_parameters = [
                           ('RabiFlopping133', 'channel_493'),
                           ('RabiFlopping133', 'frequency_493'),
                           ('RabiFlopping133', 'amplitude_493'),
                           ('RabiFlopping133', 'channel_650'),
                           ('RabiFlopping133', 'frequency_650'),
                           ('RabiFlopping133', 'amplitude_650'),
                           ('RabiFlopping133', 'amplitude_650_shelving'),
                           ('RabiFlopping133', 'channel_455'),
                           ('RabiFlopping133', 'frequency_455'),
                           ('RabiFlopping133', 'amplitude_455'),
                           ('RabiFlopping133', 'channel_585'),
                           ('RabiFlopping133', 'frequency_585'),
                           ('RabiFlopping133', 'amplitude_585'),
                           ('RabiFlopping133', 'doppler_cooling_duration'),
                           ('RabiFlopping133', 'state_prep_duration'),
                           ('RabiFlopping133', 'state_detection_duration'),
                           ('RabiFlopping133', 'shelving_duration'),
                           ('RabiFlopping133', 'deshelving_duration'),
                           ('RabiFlopping133', 'microwave_frequency'),
                           # The microwave duration is the parameter that can be changed and passed to the pulser
                           # each time you run a pulse sequence
                           ('RabiFlopping133', 'microwave_duration'),
                           ('RabiFlopping133', 'TTL_493'),
                           ('RabiFlopping133', 'TTL_650'),
                           ('RabiFlopping133', 'TTL_455'),
                           ('RabiFlopping133', 'TTL_585'),
                           ('RabiFlopping133', 'TTL_prep'),
                           ('RabiFlopping133', 'TTL_microwaves'),
                           ('RabiFlopping133', 'TTL_deshelve'),
                           ('RabiFlopping133', 'Sequences_Per_Point'),
                           ('RabiFlopping133', 'Start_Time'),
                           ('RabiFlopping133', 'Stop_Time'),
                           ('RabiFlopping133', 'Time_Step'),
                           ('RabiFlopping133', 'State_Detection'),
                           ('RabiFlopping133', 'dc_threshold'),
                           ]

    def sequence(self):
        self.start = WithUnit(10.0,'us')
        self.t0 = self.start - WithUnit(1.0,'us')
        self.p = self.parameters.RabiFlopping133

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
        self.ttl_455 = self.p.TTL_455
        self.ttl_585 = self.p.TTL_585
        self.ttl_prep = self.p.TTL_prep
        self.ttl_microwave = self.p.TTL_microwaves
        self.ttl_deshelve = self.p.TTL_deshelve
        self.state_detection = self.p.State_Detection

        self.cool_time = self.p.doppler_cooling_duration
        self.prep_time = self.p.state_prep_duration
        self.microwave_time = self.p.microwave_duration

        self.shelve455_time = WithUnit(3.0,'us')
        self.shelve585_time = WithUnit(30.0,'us')
        self.shelving_time = self.shelve455_time + self.shelve585_time

        self.deshelving_time = self.p.deshelving_duration
        self.sd_time = self.p.state_detection_duration
        self.switch_time = WithUnit(1.0,'us') # Looked on a scope. Really about 200ns but figured this was safe
        self.sd_switch_time = WithUnit(3.0,'us')
        self.n = 20

        if self.state_detection == 'spin-1/2':
            self.addDDS(self.channel_493, self.t0,  self.cool_time + self.prep_time , self.freq_493, self.amp_493)
            self.addTTL('ReadoutCount', self.start, self.cool_time)
            # First Doppler cool which is doing nothing
            # Next optically pump by turning off 5.8GHz and 1.84GHz on
            self.addTTL(self.ttl_493, self.start + self.cool_time, self.prep_time + \
                        self.switch_time + self.microwave_time + self.switch_time + self.sd_time)
            self.addTTL(self.ttl_prep, self.start + self.cool_time, self.prep_time)
            # Next apply microwaves and turn off everything else
            # DDS will turn off from above setting
            self.addTTL(self.ttl_650, self.start + self.cool_time + self.prep_time, \
                         self.switch_time + self.microwave_time + self.switch_time + self.sd_time)

            self.addTTL(self.ttl_microwave, self.start + self.cool_time + self.prep_time + \
                         self.switch_time , self.microwave_time)

            # Turn the dds back on for state detection
            self.addDDS(self.channel_493, self.t0 + self.cool_time + self.prep_time + \
                        self.switch_time + self.microwave_time, self.switch_time + self.sd_time, self.freq_493, self.amp_493)
            # Turn on photon counting for state detection
            self.addTTL('ReadoutCount', self.start + self.cool_time + self.prep_time + \
                        self.switch_time + self.microwave_time, self.switch_time + self.sd_time)

        if self.state_detection == 'shelving':
            # First we doppler cool. We want to monitor counts during cooling in case something bad happens.
            self.addTTL('ReadoutCount', self.start, self.cool_time)
            self.addDDS(self.channel_493, self.t0,  self.cool_time + self.prep_time , self.freq_493, self.amp_493)
            self.addDDS(self.channel_650, self.t0,  self.cool_time + self.prep_time , self.freq_650, self.amp_650)
            # Next optically pump by turning off 5.8GHz and 1.84GHz on
            self.addTTL(self.ttl_493, self.start + self.cool_time, self.prep_time + self.switch_time + self.microwave_time + \
                        self.switch_time + self.n*self.shelving_time)
            self.addTTL(self.ttl_prep, self.start + self.cool_time, self.prep_time)
            # Next apply microwaves and turn off everything else
            # DDS will turn off from above setting
            self.addTTL(self.ttl_650, self.start + self.cool_time + self.prep_time, self.switch_time + self.microwave_time + \
                         self.switch_time + self.n*self.shelving_time)
            self.addTTL(self.ttl_microwave, self.start + self.cool_time + self.prep_time + self.switch_time , self.microwave_time)

            # Turn on shelving lasers

            # Need to send 455 & 585 through an RF switch
            if self.shelving_time != 0:
                #self.addTTL(self.ttl_455, self.start + self.cool_time + self.prep_time + self.switch_time + self.microwave_time + \
                         #self.switch_time, self.shelving_time)
                #self.addTTL(self.ttl_585, self.start + self.cool_time + self.prep_time + self.switch_time + self.microwave_time + \
                         #self.switch_time, self.shelving_time)
                for i in range(self.n):
                    self.addTTL(self.ttl_455, self.start + self.cool_time + self.prep_time + self.switch_time + i*(self.shelve455_time + self.shelve585_time), self.shelve455_time)
                    self.addTTL(self.ttl_585, self.start + self.cool_time + self.prep_time + self.switch_time + i*(self.shelve585_time) +(i+1)*self.shelve455_time , self.shelve585_time)
            #self.addDDS(self.channel_455, self.t0 + self.cool_time + self.prep_time + self.switch_time + \
                        #self.microwave_time + self.switch_time, self.shelving_time, self.freq_455, self.amp_455)
            #Turn on low power 650
            self.addDDS(self.channel_650, self.t0 +  self.cool_time + self.prep_time + self.switch_time + \
                        self.microwave_time + self.switch_time, self.n*self.shelving_time , self.freq_650, self.amp_650_shelving)
            #self.addDDS(self.channel_585, self.t0 + self.cool_time + self.prep_time + self.switch_time + \
                        #self.microwave_time + self.switch_time, self.shelving_time, self.freq_585, self.amp_585)


            # Turn the dds back on for state detection
            self.addDDS(self.channel_493, self.t0 + self.cool_time + self.prep_time + self.switch_time + \
                         self.microwave_time + self.switch_time + self.n*self.shelving_time + self.sd_switch_time, self.sd_time + self.deshelving_time, self.freq_493, self.amp_493)
            self.addDDS(self.channel_650, self.t0 + self.cool_time + self.prep_time + self.switch_time + \
                         self.microwave_time + self.switch_time + self.n*self.shelving_time + self.sd_switch_time, self.sd_time + self.deshelving_time, self.freq_650, self.amp_650)
            # Turn on photon counting for state detection
            self.addTTL('ReadoutCount', self.start + self.cool_time + self.prep_time + self.switch_time + \
                         self.microwave_time + self.switch_time + self.n*self.shelving_time + self.sd_switch_time, self.sd_time)

            # Turn on deshelving LED
            self.addTTL(self.ttl_deshelve, self.start + self.cool_time + self.prep_time + self.switch_time + \
                         self.microwave_time + self.switch_time + self.n*self.shelving_time + self.sd_switch_time + self.sd_time, self.deshelving_time)
