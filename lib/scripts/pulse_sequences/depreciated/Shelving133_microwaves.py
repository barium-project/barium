from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit


class shelving133(pulse_sequence):

    required_parameters = [
                           ('Shelving133', 'channel_493'),
                           ('Shelving133', 'frequency_493'),
                           ('Shelving133', 'amplitude_493'),
                           ('Shelving133', 'channel_650'),
                           ('Shelving133', 'frequency_650'),
                           ('Shelving133', 'amplitude_650'),
                           ('Shelving133', 'amplitude_650_shelving'),
                           ('Shelving133', 'channel_455'),
                           ('Shelving133', 'frequency_455'),
                           ('Shelving133', 'amplitude_455'),
                           ('Shelving133', 'amplitude_d32'),
                           ('Shelving133', 'channel_d32'),
                           ('Shelving133', 'LO_freq'),
                           ('Shelving133', 'LO_amp'),
                           ('Shelving133', 'b_field'),
                           ('Shelving133', 'hyperfine_freq'),
                           ('Shelving133', 'hf_freq_1'),
                           ('Shelving133', 'hf_freq_2'),
                           ('Shelving133', 'hf_freq_3'),
                           ('Shelving133', 'doppler_cooling_duration'),
                           ('Shelving133', 'shelving_duration'),
                           ('Shelving133', 'deshelving_duration'),
                           ('Shelving133', 'cycles'),
                           ('Shelving133', 'Start_Time'),
                           ('Shelving133', 'Stop_Time'),
                           ('Shelving133', 'Time_Step'),
                           ('Shelving133', 'Frequency_Start'),
                           ('Shelving133', 'Frequency_Stop'),
                           ('Shelving133', 'Frequency_Step'),
                           ('Shelving133', 'Scan'),
                           ('Shelving133', 'detection_duration'),
                           ('Shelving133', 'TTL_650'),
                           ('Shelving133', 'd32_frequency_sweep'),
                           ('Shelving133', 'ramp_duration'),
                           ]

    def sequence(self):

        self.p = self.parameters.Shelving133
        self.start = WithUnit(10.0,'us')

        self.channel_493 = self.p.channel_493
        self.freq_493 = self.p.frequency_493
        self.amp_493 = self.p.amplitude_493

        self.channel_650 = self.p.channel_650
        self.freq_650 = self.p.frequency_650
        self.amp_650 = self.p.amplitude_650
        self.amp_650_shelve = self.p.amplitude_650_shelving

        self.channel_455 = self.p.channel_455
        self.freq_455 = self.p.frequency_455
        self.amp_455 = self.p.amplitude_455

        self.channel_d32 = self.p.channel_d32
        self.freq_d32 = self.p.frequency_d32
        self.amp_d32 = self.p.amplitude_d32

        self.cycles = self.p.cycles
        self.ttl_650 = self.p.TTL_650

        self.sweep = self.p.d32_frequency_sweep

        self.t0 = self.start - WithUnit(1.0,'us') # takes 1us to switch frequencies. This way actually turns on at 10us
        self.advance = WithUnit(0.85,'us')
        self.cool_time = self.p.doppler_cooling_duration
        self.deshelve_time = self.p.deshelving_duration
        self.shelve_time = self.p.shelving_duration
        self.detection_time = self.p.detection_duration
        self.ramp_time = self.p.ramp_duration
        self.sweep_time = self.ramp_time + WithUnit(10.0, 'us')

        # Turn on doppler cooling DDSs
        # 493 Only for cooling, 650 stays on for shelving, but sideband off
        self.addDDS(self.channel_493, self.t0, self.cool_time, self.freq_493, self.amp_493)
        self.addDDS(self.channel_650, self.t0, self.cool_time, self.freq_650, self.amp_650)

        # ramp if we want to

        if self.sweep == 'True':
            if self.shelve_time != 0:
                # Turn off 904 for shelving and ramping
                self.addTTL(self.ttl_650, self.t0 + self.cool_time, self.shelve_time + self.sweep_time + self.shelve_time)
                # Turn on rf switch for sweep
                self.addTTL('TTL8', self.t0 + self.cool_time + self.shelve_time, self.sweep_time)
            # shelve, ramp & clear, and shelve again
            # Turn on 455 DDS for shelving
            # Turn on 650 at low power for shelving and clearing
            self.addDDS(self.channel_455, self.t0 + self.cool_time, self.shelve_time, self.freq_455, self.amp_455)
            self.addDDS(self.channel_650, self.t0 + self.cool_time,  self.shelve_time , self.freq_650, self.amp_650_shelve)

            freq_ramp_rate = (self.p.Frequency_Stop['MHz'] - self.p.Frequency_Start['MHz'])/self.ramp_time['ms']
            print freq_ramp_rate
            if freq_ramp_rate > 7.4:
                print "error, freq ramp rate too high"
            self.addDDS(self.channel_d32, self.t0 + self.cool_time + self.shelve_time, WithUnit(10.0,'us'), WithUnit(self.p.Frequency_Start['MHz'],'MHz'), self.amp_d32)
            self.addDDS(self.channel_d32, self.t0 + self.cool_time + self.shelve_time + WithUnit(10.0,'us'), self.ramp_time, WithUnit(self.p.Frequency_Stop['MHz'],'MHz'), self.amp_d32, \
                        phase = WithUnit(0.0,'deg'), ramp_rate = WithUnit(freq_ramp_rate,'MHz'), amp_ramp_rate = WithUnit(0.0,'dB'))

            # Clear out the state with low power
            self.addDDS(self.channel_650, self.t0 + self.cool_time + self.shelve_time + self.sweep_time,  self.shelve_time , self.freq_650, self.amp_650_shelve)

            self.addDDS(self.channel_455, self.t0 + self.cool_time + self.shelve_time + self.sweep_time, self.shelve_time, self.freq_455, self.amp_455)

            # Turn back on 493 and 650 for state detection
            self.addDDS(self.channel_493, self.t0 + self.cool_time + self.shelve_time + self.sweep_time + self.shelve_time, \
                        self.detection_time + self.deshelve_time, self.freq_493, self.amp_493)
            self.addDDS(self.channel_650, self.t0 + self.cool_time + self.shelve_time + self.sweep_time + self.shelve_time,  self.detection_time + \
                        self.deshelve_time, self.freq_650, self.amp_650)
            # Count photons during detection time

            self.addTTL('ReadoutCount', self.t0 + self.cool_time + self.shelve_time + self.sweep_time + self.shelve_time, self.detection_time)

            # Turn on deshelving LED
            self.addTTL('TTL7', self.t0 + self.cool_time  + self.shelve_time + self.sweep_time + self.shelve_time + self.detection_time, self.deshelve_time)

        else:

            if self.shelve_time != 0:
                # Turn off 904 for shelving
                self.addTTL(self.ttl_650, self.t0 + self.cool_time, self.shelve_time)
                # Turn on rf switch for local oscillator
                self.addTTL('TTL8', self.start + self.cool_time, self.shelve_time)

            # Turn on 650 with low power for shelving
            self.addDDS(self.channel_650, self.t0 + self.cool_time,  self.shelve_time, self.freq_650, self.amp_650_shelve)
            # Turn on shelving laser
            self.addDDS(self.channel_455, self.t0 + self.cool_time, self.shelve_time, self.freq_455, self.amp_455)
            # Turn on shelving microwaves
            self.addDDS(self.channel_d32, self.t0 + self.cool_time, self.shelve_time/3, self.p.hf_freq_1, self.amp_d32)
            self.addDDS(self.channel_d32, self.t0 + self.cool_time + self.shelve_time/3, self.shelve_time/3, self.p.hf_freq_2, self.amp_d32)
            self.addDDS(self.channel_d32, self.t0 + self.cool_time +  2*self.shelve_time/3, self.shelve_time/3, self.p.hf_freq_3, self.amp_d32)


            # Turn back on 493 and 650 for state detection
            self.addDDS(self.channel_493, self.t0 + self.cool_time + self.shelve_time, \
                        self.detection_time + self.deshelve_time, self.freq_493, self.amp_493)
            self.addDDS(self.channel_650, self.t0 + self.cool_time + self.shelve_time,  self.detection_time + \
                        self.deshelve_time, self.freq_650, self.amp_650)
            # Count photons during detection time
            self.addTTL('ReadoutCount', self.t0 + self.cool_time + self.shelve_time , self.detection_time)

            # Turn on deshelving LED
            self.addTTL('TTL7', self.t0 + self.cool_time  + self.shelve_time  + self.detection_time, self.deshelve_time)

        # keep for deshelving but prob won't ever use
        '''
        # If we're scanning deshelve time
        else:
            # Turn on doppeler cooling DDSs for entire experiment
            self.addDDS(self.channel_493, self.t0, self.cool_time + self.shelve_time + self.deshelve_time + \
                        self.detection_time + self.clean_out_time, self.freq_493, self.amp_493)
            self.addDDS(self.channel_650, self.t0, self.cool_time + self.shelve_time + self.deshelve_time + \
                        + self.detection_time + self.clean_out_time, self.freq_650, self.amp_650)

            # Turn on 455 DDS for shelving
            self.addDDS(self.channel_455, self.t0 + self.cool_time, self.shelve_time, self.freq_455, self.amp_455)

            # Turn on deshelving LED
            self.addTTL('TTL7', self.t0 + self.cool_time + self.shelve_time, self.deshelve_time)

            # Count photons during detection time
            self.addTTL('ReadoutCount', self.t0 + self.cool_time + self.shelve_time + self.deshelve_time, self.detection_time)


            # Turn on deshelving LED to make sure state is cleaned out
            self.addTTL('TTL7', self.t0 + self.cool_time + self.shelve_time + self.deshelve_time \
                        + self.detection_time, self.clean_out_time)
        '''

