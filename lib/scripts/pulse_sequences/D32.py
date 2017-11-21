from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from barium.lib.scripts.pulse_sequences.FrequencySweep import frequency_sweep
from labrad.units import WithUnit

class D32_measurement(pulse_sequence):



    required_parameters = [('D32Measurement', 'channel_493'),
                           ('D32Measurement', 'frequency_493'),
                           ('D32Measurement', 'amplitude_493'),
                           ('D32Measurement', 'channel_650'),
                           ('D32Measurement', 'frequency_650'),
                           ('D32Measurement', 'amplitude_650'),
                           ('D32Measurement', 'doppler_cooling_duration'),
                           ('D32Measurement', 'state_prep_duration_s'),
                           ('D32Measurement', 'state_prep_duration_d'),
                           ('D32Measurement', 'state_detection_duration'),
                           ('D32Measurement', 'TTL_493'),
                           ('D32Measurement', 'TTL_650'),
                           ('D32Measurement', 'Scan'),
                           ('D32Measurement', 'Sequences_Per_Point'),
                           ('D32Measurement', 'Start_Time'),
                           ('D32Measurement', 'Stop_Time'),
                           ('D32Measurement', 'Time_Step'),
                           ]

    required_parameters.extend(frequency_sweep.all_required_parameters())

    required_subsequences = [frequency_sweep]

    def sequence(self):
        self.start = WithUnit(10.0,'us')
        self.p = self.parameters.D32Measurement
        self.f = self.parameters.FrequencySweep

        self.channel_493 = self.p.channel_493
        self.freq_493 = self.p.frequency_493
        self.amp_493 = self.p.amplitude_493
        self.channel_650 = self.p.channel_650
        self.freq_650 = self.p.frequency_650
        self.amp_650 = self.p.amplitude_650
        self.ttl_493 = self.p.TTL_493
        self.ttl_650 = self.p.TTL_650
        self.ttl_prep = self.p.TTL_prep

        self.scan_channel = self.f.scan_dds_channel
        self.scan_amp = self.f.scan_dds_amplitude
        self.time_per_freq = self.f.time_per_freq

        self.cool_time = self.p.doppler_cooling_duration
        self.prep_time_s = self.p.state_prep_duration_s
        self.prep_time_d = self.p.state_prep_duration_d
        self.microwave_time = 3*self.f.time_per_freq
        self.sd_time = self.p.state_detection_duration
        self.switch_time = WithUnit(500,'ns')



        # Turn on the 493 for the entire sequence
        self.addDDS(self.channel_493, self.start,  self.cool_time  + self.prep_time_d +
                    self.switch_time + self.microwave_time + self.switch_time + self.sd_time , self.freq_493, self.amp_493)
        # Turn on the 650 for the S, F = 1 prep time
        self.addDDS(self.channel_650, self.start,  self.cool_time , self.freq_650, self.amp_650)

        # First Doppler cool which is doing nothing
        # Next optically pump by turning off 650


        # Next we optically pump to the D, F = 1. The 650 DDS should turn off. Need to turn off the 904MHz sideband
        self.addTTL(self.ttl_650, self.start + self.cool_time , self.prep_time_d + self.switch_time + self.microwave_time + \
                    self.switch_time  + self.sd_time)

        # Turn off 5.8GHz. Could wait until right before state detection but just do it now
        self.addTTL(self.ttl_493, self.start + self.cool_time + self.prep_time_d,  self.switch_time + self.microwave_time + \
                    self.switch_time + self.sd_time)

        # Next we need to apply the microwave pulse using the frequency sweep pulse sequence.
        # This sequentially hits all three pi transitions for a specified number of transitions.

        self.addDDS(self.scan_channel, self.start + self.cool_time + self.prep_time_d + self.switch_time - WithUnit(1.0,'us') , self.time_per_freq + \
                    WithUnit(1.0, 'us'), self.f.freq_1, self.scan_amp)

        self.addDDS(self.scan_channel, self.start + self.cool_time + self.prep_time_d + self.switch_time + \
                    self.time_per_freq, self.time_per_freq, self.f.freq_2, self.scan_amp)

        self.addDDS(self.scan_channel, self.start + self.cool_time + self.prep_time_d + self.switch_time + \
                    2*self.time_per_freq, self.time_per_freq, self.f.freq_3, self.scan_amp)



        # Wait for the microwaves and then do state detection

        # Turn the 650 dds back on for state detection
        self.addDDS(self.channel_650, self.start + self.cool_time  + self.prep_time_d + self.switch_time + 3*self.time_per_freq \
                    , self.switch_time + self.sd_time , self.freq_650, self.amp_650)


        self.addTTL('ReadoutCount', self.start + self.cool_time + self.prep_time_d + self.switch_time + self.microwave_time \
                    , self.switch_time + self.sd_time)




