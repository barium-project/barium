from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit


class bright_state(pulse_sequence):

    required_parameters = [('BrightState133', 'dds_channel'),
                           ('BrightState133', 'dds_frequency'),
                           ('BrightState133', 'dds_amplitude'),
                           ('BrightState133', 'doppler_cooling_duration'),
                           ('BrightState133', 'state_detection_duration'),
                           ('BrightState133', 'TTL_493'),
                           ('BrightState133', 'TTL_650'),
                           ('BrightState133', 'number_of_sequences')
                           ]

    required_subsequences = []

    def sequence(self):
        self.start = WithUnit(10.0,'us')
        self.p = self.parameters.BrightState133

        self.channel = self.p.dds_channel
        self.freq = self.p.dds_frequency
        self.amp = self.p.dds_amplitude
        self.ttl_493 = self.p.TTL_493
        self.ttl_650 = self.p.TTL_650

        self.cool_time = self.p.doppler_cooling_duration
        self.sd_time = self.p.state_detection_duration

        self.switch_time = WithUnit(1.0,'us')
        self.total_time = self.cool_time + self.sd_time + self.switch_time

        # Turn on the light
        self.addDDS(self.channel, self.start,  self.total_time, self.freq, self.amp)
        self.start += self.switch_time
        # First Doppler cool which is doing nothing

        # Next state detect by turning off 5.8GHz and 904MHz
        self.addTTL(self.ttl_493, self.start + self.cool_time, self.sd_time)
        self.addTTL(self.ttl_650, self.start + self.cool_time, self.sd_time)
        self.addTTL('ReadoutCount', self.start + self.cool_time, self.sd_time)




