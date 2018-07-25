from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class shelving_state_detection(pulse_sequence):

    required_parameters = [
                           ('ShelvingStateDetection', 'state_detection_duration'),
                           ('ShelvingStateDetection', 'TTL_493'),
                           ('ShelvingStateDetection', 'TTL_493_DDS'),
                           ('ShelvingStateDetection', 'TTL_650'),
                           ('ShelvingStateDetection', 'channel_493'),
                           ('ShelvingStateDetection', 'frequency_493'),
                           ('ShelvingStateDetection', 'amplitude_493'),
                           ('ShelvingStateDetection', 'channel_650'),
                           ('ShelvingStateDetection', 'frequency_650'),
                           ('ShelvingStateDetection', 'amplitude_650'),
                           ]

    def sequence(self):
        # start time is defined to be 0s.
        p = self.parameters.ShelvingStateDetection

       # use this to turn the DDS to a very low power right before we turn it on
        # to avoid the weird 1us loss.
        amp_off = WithUnit(-47.0,'dBm')
        switch_on_delay = WithUnit(2.0,'us')

        # add a small delay for the switching on
        amp_change_delay = WithUnit(335.0,'ns')

        self.addTTL(p.TTL_493_DDS, self.start + switch_on_delay, p.state_detection_duration)

        self.addDDS(p.channel_493, self.start - amp_change_delay,\
                     switch_on_delay, p.frequency_493, amp_off)
        self.addDDS(p.channel_650, self.start - amp_change_delay,\
                    switch_on_delay, p.frequency_650, amp_off)

        self.addDDS(p.channel_493, self.start + switch_on_delay - amp_change_delay, \
                     p.state_detection_duration, p.frequency_493, p.amplitude_493)
        self.addDDS(p.channel_650, self.start + switch_on_delay - amp_change_delay, \
                     p.state_detection_duration, p.frequency_650, p.amplitude_650)

        # Count photons during doppler cooling to monitor for dropouts
        self.addTTL('ReadoutCount', self.start, p.state_detection_duration)
        self.end = self.start + switch_on_delay + p.state_detection_duration
