from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class ramsey(pulse_sequence):

    required_parameters = [('Ramsey133', 'dds_channel'),
                           ('Ramsey133', 'dds_frequency'),
                           ('Ramsey133', 'dds_amplitude'),
                           ('Ramsey133', 'doppler_cooling_duration'),
                           ('Ramsey133', 'state_prep_duration'),
                           ('Ramsey133', 'state_detection_duration'),
                           ('Ramsey133', 'microwave_frequency'),
                           ('Ramsey133', 'microwave_duration'),
                           ('Ramsey133', 'TTL_493'),
                           ('Ramsey133', 'TTL_650'),
                           ('Ramsey133', 'TTL_prep'),
                           ('Ramsey133', 'TTL_microwaves'),
                           ('Ramsey133', 'Sequences_Per_Point'),
                           ('Ramsey133', 'Start_Time'),
                           ('Ramsey133', 'Stop_Time'),
                           ('Ramsey133', 'Time_Step'),
                           # Ramsey Delay is the parameter that's changed and passed to the pulser for each
                           # pulse sequence.
                           ('Ramsey133', 'Ramsey_Delay'),
                           ]

    def sequence(self):
        self.start = WithUnit(10.0,'us')
        self.p = self.parameters.Ramsey133

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
        self.ramsey_delay = self.p.Ramsey_Delay

        # Turn on the 493
        self.addDDS(self.channel, self.start,  self.cool_time + self.prep_time , self.freq, self.amp)
        # First Doppler cool which is doing nothing
        # Next optically pump by turning off 5.8GHz and 1.84GHz on
        self.addTTL(self.ttl_493, self.start + self.cool_time, self.prep_time + self.switch_time + self.microwave_time + self.ramsey_delay + \
                     self.microwave_time  + self.switch_time + self.sd_time)
        self.addTTL(self.ttl_prep, self.start + self.cool_time, self.prep_time)
        # Next apply microwaves and turn off everything else
        self.addTTL(self.ttl_650, self.start + self.cool_time + self.prep_time, self.switch_time + self.microwave_time + self.ramsey_delay + \
                    self.microwave_time + self.switch_time  + self.sd_time)
        self.addTTL(self.ttl_microwave, self.start + self.cool_time + self.prep_time + self.switch_time , self.microwave_time)

        # Wait for the ramsey delay time
        # Do another microwave pulse
        self.addTTL(self.ttl_microwave, self.start + self.cool_time + self.prep_time + self.microwave_time + self.switch_time + self.ramsey_delay , self.microwave_time)


        # Turn the dds back on for state detection
        self.addDDS(self.channel, self.start + self.cool_time + self.prep_time + self.switch_time + self.microwave_time + self.ramsey_delay + \
                    + self.microwave_time, self.switch_time + self.sd_time , self.freq, self.amp)

        self.addTTL('ReadoutCount', self.start + self.cool_time + self.prep_time + self.switch_time + self.microwave_time + self.ramsey_delay + \
                    + self.microwave_time, self.switch_time + self.sd_time)




