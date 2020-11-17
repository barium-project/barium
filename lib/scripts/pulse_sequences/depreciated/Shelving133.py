from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit


class shelving133(pulse_sequence):

    required_parameters = [
                           ('Shelving133', 'channel_493'),
                           ('Shelving133', 'frequency_493'),
                           ('Shelving133', 'amplitude_493'),
                           ('Shelving133', 'amplitude_493_shelving'),
                           ('Shelving133', 'channel_650'),
                           ('Shelving133', 'frequency_650'),
                           ('Shelving133', 'amplitude_650'),
                           ('Shelving133', 'amplitude_650_shelving'),
                           ('Shelving133', 'channel_455'),
                           ('Shelving133', 'frequency_455'),
                           ('Shelving133', 'amplitude_455'),
                           ('Shelving133', 'channel_585'),
                           ('Shelving133', 'frequency_585'),
                           ('Shelving133', 'amplitude_585'),
                           ('Shelving133', 'doppler_cooling_duration'),
                           ('Shelving133', 'shelving_duration'),
                           ('Shelving133', 'state_prep_duration'),
                           ('Shelving133', 'deshelving_duration'),
                           ('Shelving133', 'cycles'),
                           ('Shelving133', 'Start_Time'),
                           ('Shelving133', 'Stop_Time'),
                           ('Shelving133', 'Time_Step'),
                           ('Shelving133', 'Frequency_Start'),
                           ('Shelving133', 'Frequency_Stop'),
                           ('Shelving133', 'Frequency_Step'),
                           ('Shelving133', 'Scan'),
                           ('Shelving133', 'Scan_Laser'),
                           ('Shelving133', 'detection_duration'),
                           ('Shelving133', 'TTL_650'),
                           ('Shelving133', 'TTL_493'),
                           ('Shelving133', 'TTL_455'),
                           ('Shelving133', 'TTL_585'),
                           ('Shelving133', 'TTL_prep'),
                           ('Shelving133', 'dc_threshold'),
                           ]

    def sequence(self):

        self.p = self.parameters.Shelving133
        self.start = WithUnit(10.0,'us')

        self.channel_493 = self.p.channel_493
        self.freq_493 = self.p.frequency_493
        self.amp_493 = self.p.amplitude_493
        self.amp_493_shelve = self.p.amplitude_493_shelving

        self.channel_650 = self.p.channel_650
        self.freq_650 = self.p.frequency_650
        self.amp_650 = self.p.amplitude_650
        self.amp_650_shelve = self.p.amplitude_650_shelving

        self.channel_455 = self.p.channel_455
        self.freq_455 = self.p.frequency_455
        self.amp_455 = self.p.amplitude_455

        self.channel_585 = self.p.channel_585
        self.freq_585 = self.p.frequency_585
        self.amp_585 = self.p.amplitude_585

        self.cycles = self.p.cycles
        self.ttl_493 = self.p.TTL_493
        self.ttl_650 = self.p.TTL_650
        self.ttl_455 = self.p.TTL_455
        self.ttl_585 = self.p.TTL_585
        self.ttl_prep = self.p.TTL_prep


        self.t0 = self.start - WithUnit(1.0,'us') # takes 1us to switch frequencies. This way actually turns on at 10us
        self.switch_time = WithUnit(1.0,'us')
        self.cool_time = self.p.doppler_cooling_duration
        self.prep_time = self.p.state_prep_duration
        self.deshelve_time = self.p.deshelving_duration
        self.shelve455_time = WithUnit(2.0,'us')
        self.shelve585_time = WithUnit(50.0,'us')
        #self.shelve_time = self.p.shelving_duration
        self.shelve_time = self.shelve455_time + self.shelve585_time
        self.detection_time = self.p.detection_duration
        self.n = 20

        # Turn on doppler cooling DDSs
        # 493 Only for cooling, 650 stays on for shelving, but sideband off
        self.addDDS(self.channel_493, self.t0, self.cool_time, self.freq_493, self.amp_493)
        self.addDDS(self.channel_650, self.t0, self.cool_time, self.freq_650, self.amp_650)
        # Count photons during doppler cooling to monitor for dropouts
        self.addTTL('ReadoutCount', self.start, self.cool_time)

        # Add a state prep step to move all the population out of the S1/2; F=0 state
        # Turn of VCO 5.8 and turn on HP8673 Oscillator. Need to remember to switch this
        # manually before running exp since we use it to heat first.
        self.addTTL(self.ttl_493, self.start + self.cool_time, self.prep_time)
        self.addTTL(self.ttl_prep, self.start + self.cool_time, self.prep_time)

        if self.shelve_time != 0:
            #self.addTTL(self.ttl_455, self.start + self.cool_time + self.prep_time + \
                         #self.switch_time, self.shelve_time)
            #self.addTTL(self.ttl_585, self.start + self.cool_time + self.prep_time +  \
                         #self.switch_time, self.shelve_time)
            # Turn off 904 for shelving
            self.addTTL(self.ttl_650, self.start + self.cool_time + self.prep_time, self.n*self.shelve_time + self.switch_time)
            # Turn on 493 if we want to scan the 585nm line. Will turn off 455nm to do this
            #self.addDDS(self.channel_493, self.t0 + self.cool_time + self.prep_time + self.switch_time,  self.shelve_time, self.freq_493, self.amp_493_shelve)
            # Turn on 650 with low power for shelving
            #self.addDDS(self.channel_650, self.t0 + self.cool_time + self.prep_time + \
                         #self.switch_time,  self.shelve_time, self.freq_650, self.amp_650_shelve)
            # Turn on shelving laser
            #self.addDDS(self.channel_455, self.t0 + self.cool_time + self.prep_time + \
                         #self.switch_time, self.shelve_time, self.freq_455, self.amp_455)
            #self.addDDS(self.channel_585, self.t0 + self.cool_time + self.prep_time + \
                         #self.switch_time, self.shelve_time, self.freq_585, self.amp_585)
            # Turn on RF swith for 455nm AOM

            for i in range(self.n):
                self.addTTL(self.ttl_455, self.start + self.cool_time + self.prep_time + self.switch_time + i*(self.shelve455_time + self.shelve585_time), self.shelve455_time)
                self.addTTL(self.ttl_585, self.start + self.cool_time + self.prep_time + self.switch_time + i*(self.shelve585_time) +(i+1)*self.shelve455_time , self.shelve585_time)
                self.addDDS(self.channel_650, self.t0 + self.cool_time + self.prep_time + \
                         self.switch_time + i*(self.shelve455_time + self.shelve585_time), self.shelve455_time, self.freq_650, self.amp_650_shelve)


        # Turn back on 493 and 650 for state detection
        self.addDDS(self.channel_493, self.t0 + self.cool_time + self.prep_time + self.switch_time + self.n*self.shelve_time, \
                    self.detection_time + self.deshelve_time, self.freq_493, self.amp_493)
        self.addDDS(self.channel_650, self.t0 + self.cool_time + self.prep_time + self.switch_time + self.n*self.shelve_time,  self.detection_time + \
                    self.deshelve_time, self.freq_650, self.amp_650)
        # Count photons during detection time
        self.addTTL('ReadoutCount', self.start + self.cool_time + self.prep_time + \
                    self.switch_time + self.n*self.shelve_time, self.detection_time)

        # Turn on deshelving LED
        self.addTTL('TTL7', self.start + self.cool_time  + self.n*self.shelve_time + self.prep_time \
                      + self.switch_time + self.detection_time, self.deshelve_time)

