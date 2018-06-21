from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit


class shelving(pulse_sequence):

    required_parameters = [
                           ('Shelving', 'channel_493'),
                           ('Shelving', 'frequency_493'),
                           ('Shelving', 'amplitude_493'),
                           ('Shelving', 'channel_650'),
                           ('Shelving', 'frequency_650'),
                           ('Shelving', 'amplitude_650'),
                           ('Shelving', 'channel_455'),
                           ('Shelving', 'frequency_455'),
                           ('Shelving', 'amplitude_455'),
                           ('Shelving', 'channel_585'),
                           ('Shelving', 'frequency_585'),
                           ('Shelving', 'amplitude_585'),
                           ('Shelving', 'doppler_cooling_duration'),
                           ('Shelving', 'shelving_duration'),
                           ('Shelving', 'deshelving_duration'),
                           ('Shelving', 'cycles'),
                           ('Shelving', 'Start_Time'),
                           ('Shelving', 'Stop_Time'),
                           ('Shelving', 'Time_Step'),
                           ('Shelving', 'Frequency_Start'),
                           ('Shelving', 'Frequency_Stop'),
                           ('Shelving', 'Frequency_Step'),
                           ('Shelving', 'Scan'),
                           ('Shelving', 'Scan_Laser'),
                           ('Shelving', 'detection_duration'),
                           ('Shelving', 'dc_threshold'),
                           ]

    def sequence(self):

        self.p = self.parameters.Shelving
        self.start = WithUnit(10.0,'us')

        self.channel_493 = self.p.channel_493
        self.freq_493 = self.p.frequency_493
        self.amp_493 = self.p.amplitude_493
        self.channel_650 = self.p.channel_650
        self.freq_650 = self.p.frequency_650
        self.amp_650 = self.p.amplitude_650
        self.channel_455 = self.p.channel_455
        self.freq_455 = self.p.frequency_455
        self.amp_455 = self.p.amplitude_455
        self.channel_585 = self.p.channel_585
        self.freq_585 = self.p.frequency_585
        self.amp_585 = self.p.amplitude_585
        self.cycles = self.p.cycles
        self.t0 = self.start - WithUnit(0.5,'us') # takes 1us to switch frequencies. This way actually turns on at 10us
        self.advance = WithUnit(0.85,'us')
        self.offset = WithUnit(250.0,'ns')
        self.cool_time = self.p.doppler_cooling_duration
        self.deshelve_time = self.p.deshelving_duration
        self.shelve_time = self.p.shelving_duration
        self.detection_time = self.p.detection_duration
        self.clean_out_time = WithUnit(20.0,'ms')

        # If we're scanning frequency or time while shelving
        if self.p.Scan != 'deshelve':
            # Turn on doppler cooling DDSs
            self.addDDS(self.channel_493, self.t0, self.cool_time, self.freq_493, self.amp_493)
            self.addDDS(self.channel_650, self.t0, self.cool_time, self.freq_650, self.amp_650)
            # Count photons during doppler cooling to monitor for dropouts
            self.addTTL('ReadoutCount', self.start, self.cool_time)

            # Turn on 455 DDS for shelving
            #self.addDDS(self.channel_455, self.t0 + self.cool_time, self.shelve_time, self.freq_455, self.amp_455)
            # Turn on DDS for shelving
            #self.addDDS(self.channel_493, self.t0 + self.cool_time, self.shelve_time, self.freq_493, self.amp_493)
            self.addDDS(self.channel_650, self.t0 + self.cool_time, self.shelve_time, self.freq_650, self.amp_650)

            if self.shelve_time != 0:
                # Turn on RF swith for 455nm AOM
                self.addTTL('TTL8', self.start + self.cool_time, self.shelve_time)
                self.addTTL('TTL9', self.start + self.cool_time, self.shelve_time)

            # Turn on 585 DDS for shelving
            #self.addDDS(self.channel_585, self.t0 + self.cool_time, self.shelve_time, self.freq_585, self.amp_585)

            # Turn on DDS for detection
            self.addDDS(self.channel_493, self.t0 + self.cool_time+ self.shelve_time + self.advance, self.detection_time +\
                        self.deshelve_time, self.freq_493, self.amp_493)
            self.addDDS(self.channel_650, self.t0 + self.cool_time+ self.shelve_time + self.advance, self.detection_time + \
                        self.deshelve_time, self.freq_650, self.amp_650)
            # Count photons during detection time
            self.addTTL('ReadoutCount', self.start + self.cool_time + self.shelve_time + self.advance, self.detection_time)

            # Turn on deshelving LED
            self.addTTL('TTL7', self.start + self.cool_time + self.shelve_time + self.advance + self.detection_time, self.deshelve_time)


        # If we're scanning deshelve time
        else:
            # Turn on doppeler cooling DDSs for entire experiment
            self.addDDS(self.channel_493, self.t0, self.cool_time + self.shelve_time + self.deshelve_time + \
                        self.detection_time + self.clean_out_time, self.freq_493, self.amp_493)
            self.addDDS(self.channel_650, self.t0, self.cool_time + self.shelve_time + self.deshelve_time + \
                        + self.detection_time + self.clean_out_time, self.freq_650, self.amp_650)

            # Count photons during doppler cooling to monitor for dropouts
            #self.addTTL('ReadoutCount', self.t0, self.cool_time)

            # Turn on 455 DDS for shelving
            self.addDDS(self.channel_455, self.t0 + self.cool_time, self.shelve_time, self.freq_455, self.amp_455)
            # Turn on RF swith for 455nm AOM
            self.addTTL('TTL8', self.start + self.cool_time, self.shelve_time)
            # Turn on 585 DDS for shelving
            self.addDDS(self.channel_585, self.t0 + self.cool_time, self.shelve_time, self.freq_585, self.amp_585)


            if self.deshelve_time != 0:
                # Turn on deshelving LED
                self.addTTL('TTL7', self.t0 + self.cool_time + self.shelve_time, self.deshelve_time)

            # Count photons during detection time
            self.addTTL('ReadoutCount', self.t0 + self.cool_time + self.shelve_time + self.deshelve_time, self.detection_time)


            # Turn on deshelving LED to make sure state is cleaned out
            self.addTTL('TTL7', self.t0 + self.cool_time + self.shelve_time + self.deshelve_time \
                        + self.detection_time, self.clean_out_time)


