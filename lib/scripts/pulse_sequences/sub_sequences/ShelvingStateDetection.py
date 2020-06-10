from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class shelving_state_detection(pulse_sequence):

    required_parameters = [
                           ('ShelvingStateDetection', 'state_detection_duration'),
                           ('ShelvingStateDetection', 'TTL_493'),
                           ('ShelvingStateDetection', 'TTL_493_DDS'),
                           ('ShelvingStateDetection', 'TTL_493_SD'),
                           ('ShelvingStateDetection', 'TTL_650'),
                           ('ShelvingStateDetection', 'channel_493'),
                           ('ShelvingStateDetection', 'frequency_493'),
                           ('ShelvingStateDetection', 'amplitude_493'),
                           ('ShelvingStateDetection', 'channel_650'),
                           ('ShelvingStateDetection', 'frequency_650'),
                           ('ShelvingStateDetection', 'amplitude_650'),
                           ('ShelvingStateDetection', 'channel_microwaves'),
                           ('ShelvingStateDetection', 'frequency_microwaves'),
                           ('ShelvingStateDetection', 'amplitude_microwaves'),
                           ('ShelvingStateDetection', 'LO_frequency'),
                           ]

    def sequence(self):
        # start time is defined to be 0s.
        p = self.parameters.ShelvingStateDetection
        dds_freq = p.frequency_microwaves - p.LO_frequency
        amp_off = WithUnit(-47.0,'dBm')
        amp_change_delay = WithUnit(335.0,'ns')
        switch_on_delay = WithUnit(1.00,'us')

        self.addDDS(p.channel_493, self.start, \
                     p.state_detection_duration, p.frequency_493, p.amplitude_493)
        self.addDDS(p.channel_650, self.start, \
                     p.state_detection_duration, p.frequency_650, p.amplitude_650)

        # make sure doppler cooling ttl is off
        #self.addTTL(p.TTL_493_DDS, self.start, p.state_detection_duration)
        #self.addTTL(p.TTL_493_SD, self.start, p.state_detection_duration)

        # to stabilize the microwave amplitude turn microwaves on during state detection detuned by 100 MHz
        self.addDDS(p.channel_microwaves, self.start, switch_on_delay, \
                    dds_freq, amp_off)

        self.addDDS(p.channel_microwaves, self.start + switch_on_delay, p.state_detection_duration , dds_freq, p.amplitude_microwaves)


        # Count photons during doppler cooling to monitor for dropouts
        self.addTTL('ReadoutCount', self.start, p.state_detection_duration)
        # Time Tag photons for correcting quadrupole decay
        self.addTTL('TimeResolvedCount', self.start, p.state_detection_duration)
        self.end = self.start + p.state_detection_duration + switch_on_delay
