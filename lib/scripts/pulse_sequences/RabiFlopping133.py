from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class rabi_flopping(pulse_sequence):

    required_parameters = [('RabiFlopping133', 'dds_channel'),
                           ('RabiFlopping133', 'dds_frequency'),
                           ('RabiFlopping133', 'dds_amplitude'),
                           ('RabiFlopping133', 'doppler_cooling_duration'),
                           ('RabiFlopping133', 'state_prep_duration'),
                           ('RabiFlopping133', 'state_detection_duration'),
                           ('RabiFlopping133', 'microwave_frequency'),
                           ('RabiFlopping133', 'microwave_duration'),
                           ('RabiFlopping133', 'TTL_493'),
                           ('RabiFlopping133', 'TTL_650'),
                           ('RabiFlopping133', 'TTL_prep'),
                           ('RabiFlopping133', 'TTL_microwaves'),
                           ('RabiFlopping133', 'Sequences_Per_Point'),
                           ('RabiFlopping133', 'Start_Time'),
                           ('RabiFlopping133', 'Stop_Time'),
                           ('RabiFlopping133', 'Time_Step'),
                           ]

    def sequence(self):
        self.start = WithUnit(10.0,'us')
        self.p = self.parameters.RabiFlopping133

        self.channel = self.p.dds_channel
        self.freq = self.p.dds_frequency
        self.amp = self.p.dds_amplitude
        self.ttl_493 = self.p.TTL_493
        self.ttl_650 = self.p.TTL_650
        self.ttl_prep = self.p.TTL_prep
        self.ttl_microwave = self.p.TTL_microwaves

        self.cool_time = self.p.doppler_cooling_duration
        self.prep_time = self.p.state_prep_duration
        self.microwave_time = self.p.microwave_duration
        self.sd_time = self.p.state_detection_duration
        self.switch_time = WithUnit(500,'ns')

        self.addDDS(self.channel, self.start,  self.cool_time + self.prep_time , self.freq, self.amp)
        # First Doppler cool which is doing nothing
        # Next optically pump by turning off 5.8GHz and 1.84GHz on
        self.addTTL(self.ttl_493, self.start + self.cool_time, self.prep_time + self.microwave_time + self.sd_time + 2*self.switch_time)
        self.addTTL(self.ttl_prep, self.start + self.cool_time, self.prep_time)
        # Next apply microwaves and turn off everything else
        self.addTTL(self.ttl_650, self.start + self.cool_time + self.prep_time, self.sd_time + self.microwave_time + 2*self.switch_time)
        # Add a small delay so DDS and ttl can turn off
        self.start += self.switch_time
        self.addTTL(self.ttl_microwave, self.start + self.cool_time + self.prep_time , self.microwave_time)


        # Turn the dds back on for state detection
        self.addDDS(self.channel, self.start + self.cool_time + self.prep_time + self.microwave_time,  self.sd_time + self.switch_time , self.freq, self.amp)
        # Add the delay back so the time tag photons line up
        self.start += self.switch_time
        self.addTTL('ReadoutCount', self.start + self.cool_time + self.prep_time + self.microwave_time, self.sd_time)




