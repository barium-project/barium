from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class microwave_sweep(pulse_sequence):

    required_parameters = [
                           ('MicrowaveSweep133', 'channel_493'),
                           ('MicrowaveSweep133', 'frequency_493'),
                           ('MicrowaveSweep133', 'amplitude_493'),
                           ('MicrowaveSweep133', 'channel_455'),
                           ('MicrowaveSweep133', 'frequency_455'),
                           ('MicrowaveSweep133', 'amplitude_455'),
                           ('MicrowaveSweep133', 'amplitude_d32'),
                           ('MicrowaveSweep133', 'channel_d32'),
                           ('MicrowaveSweep133', 'frequency_d32'),
                           ('MicrowaveSweep133', 'LO_freq'),
                           ('MicrowaveSweep133', 'LO_amp'),
                           ('MicrowaveSweep133', 'State_Detection'),

                           ('MicrowaveSweep133', 'shelving_duration'),
                           ('MicrowaveSweep133', 'deshelving_duration'),
                           ('MicrowaveSweep133', 'doppler_cooling_duration'),
                           ('MicrowaveSweep133', 'state_prep_duration'),
                           ('MicrowaveSweep133', 'state_detection_duration'),
                           ('MicrowaveSweep133', 'microwave_duration'),
                           ('MicrowaveSweep133', 'TTL_493'),
                           ('MicrowaveSweep133', 'TTL_650'),
                           ('MicrowaveSweep133', 'TTL_prep'),
                           ('MicrowaveSweep133', 'TTL_microwaves'),
                           ('MicrowaveSweep133', 'TTL_deshelve'),
                           ('MicrowaveSweep133', 'Sequences_Per_Point'),
                           ('MicrowaveSweep133', 'Start_Frequency'),
                           ('MicrowaveSweep133', 'Stop_Frequency'),
                           ('MicrowaveSweep133', 'Frequency_Step'),
                           ]

    def sequence(self):
        self.start = WithUnit(10.0,'us')
        self.p = self.parameters.MicrowaveSweep133

        self.channel_493 = self.p.channel_493
        self.freq_493 = self.p.frequency_493
        self.amp_493 = self.p.amplitude_493

        self.channel_650 = self.p.channel_650
        self.freq_650 = self.p.frequency_650
        self.amp_650 = self.p.amplitude_650

        self.channel_455 = self.p.channel_455
        self.freq_455 = self.p.frequency_455
        self.amp_455 = self.p.amplitude_455

        self.channel_d32 = self.p.channel_d32
        self.freq_d32 = self.p.frequency_d32
        self.amp_d32 = self.p.amplitude_d32

        self.ttl_493 = self.p.TTL_493
        self.ttl_650 = self.p.TTL_650
        self.ttl_prep = self.p.TTL_prep
        self.ttl_microwave = self.p.TTL_microwaves
        self.ttl_deshelve = self.p.TTL_deshelve

        self.state_detection = self.p.State_Detection

        self.cool_time = self.p.doppler_cooling_duration
        self.prep_time = self.p.state_prep_duration
        self.microwave_time = self.p.microwave_duration
        self.sd_time = self.p.state_detection_duration
        self.switch_time = WithUnit(500,'ns')
        self.shelving_time = self.p.shelving_duration
        self.deshelving_time = self.p.deshelving_duration

        if self.state_detection == 'spin-1/2':
            self.addDDS(self.channel_493, self.start,  self.cool_time + self.prep_time , self.freq_493, self.amp_493)
            # First Doppler cool which is doing nothing
            # Next optically pump by turning off 5.8GHz and 1.84GHz on
            self.addTTL(self.ttl_493, self.start + self.cool_time, self.prep_time + self.switch_time + self.microwave_time \
                     + self.switch_time + self.sd_time)
            self.addTTL(self.ttl_prep, self.start + self.cool_time, self.prep_time)
            # Next apply microwaves and turn off everything else
            self.addTTL(self.ttl_650, self.start + self.cool_time + self.prep_time, self.switch_time + \
                          self.microwave_time + self.switch_time + self.sd_time)


            self.addTTL(self.ttl_microwave, self.start + self.cool_time + self.prep_time + self.switch_time, self.microwave_time)
            # Turn the dds back on for state detection
            self.addDDS(self.channel_493, self.start + self.cool_time + self.prep_time + self.switch_time + \
                         self.microwave_time + self.switch_time,  self.sd_time, self.freq_493, self.amp_493)
            # grab counts
            self.addTTL('ReadoutCount', self.start + self.cool_time + self.prep_time +  self.switch_time  + \
                        self.microwave_time + self.switch_time, self.sd_time)

        if self.state_detection == 'shelving':
            self.addDDS(self.channel_493, self.start,  self.cool_time + self.prep_time , self.freq_493, self.amp_493)
            # First Doppler cool which is doing nothing
            # Next optically pump by turning off 5.8GHz and 1.84GHz on
            self.addTTL(self.ttl_493, self.start + self.cool_time, self.prep_time + self.switch_time + self.microwave_time + \
                        self.switch_time + self.shelving_time)
            self.addTTL(self.ttl_prep, self.start + self.cool_time, self.prep_time)
            # Next apply microwaves and turn off everything else
            # 650 doesn't have to be off, just 904MHz
            # DDS will turn off from above setting
            self.addTTL(self.ttl_650, self.start + self.cool_time + self.prep_time, self.switch_time + self.microwave_time + \
                         self.switch_time + self.shelving_time)
            self.addTTL(self.ttl_microwave, self.start + self.cool_time + self.prep_time + self.switch_time , self.microwave_time)
            # Turn on shelving laser and microwaves to drive the D3/2 transition
            self.addDDS(self.channel_455, self.start + self.cool_time + self.prep_time + self.switch_time + \
                        self.microwave_time + self.switch_time, self.shelving_time, self.freq_455, self.amp_455)
            self.addDDS(self.channel_d32, self.start + self.cool_time + self.prep_time + self.switch_time + \
                        self.microwave_time + self.switch_time, self.shelving_time, self.freq_d32, self.amp_d32)
            # Turn on rf switch for microwaves
            self.addTTL('TTL8',self.start + self.cool + self.prep_time + self.switch_time + self.microwave_time + \
                        self.switch_time, self.shelving_time)

            # Turn the dds back on for state detection
            self.addDDS(self.channel_493, self.start + self.cool_time + self.prep_time + self.switch_time + \
                         self.microwave_time + self.switch_time + self.shelving_time, self.sd_time + self.deshelving_time, self.freq_493, self.amp_493)
            # Turn on photon counting for state detection
            self.addTTL('ReadoutCount', self.start + self.cool_time + self.prep_time + self.switch_time + \
                         self.microwave_time + self.switch_time + self.shelving_time, self.sd_time)

            # Turn on deshelving LED
            self.addTTL(self.ttl_deshelve, self.start + self.cool_time + self.prep_time + self.switch_time + \
                         self.microwave_time + self.switch_time + self.shelving_time + self.sd_time, self.deshelving_time)


