from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class standard_state_detection(pulse_sequence):

    required_parameters = [
                           ('StandardStateDetection', 'state_detection_duration'),
                           ('StandardStateDetection', 'TTL_493'),
                           ('StandardStateDetection', 'TTL_493_DDS'),
                           ('StandardStateDetection', 'TTL_493_SD'),
                           ('StandardStateDetection', 'TTL_650'),
                           ('StandardStateDetection', 'channel_493'),
                           ('StandardStateDetection', 'frequency_493'),
                           ('StandardStateDetection', 'amplitude_493'),
                           ('StandardStateDetection', 'channel_650'),
                           ('StandardStateDetection', 'frequency_650'),
                           ('StandardStateDetection', 'amplitude_650'),
                           ]

    def sequence(self):
        # start time is defined to be 0s.
        p = self.parameters.StandardStateDetection


        sd_delay = WithUnit(500.0,'ns')

        # add a small delay for the switching on
        amp_change_delay = WithUnit(335.0,'ns')


        self.addDDS(p.channel_493, self.start + sd_delay, \
                     p.state_detection_duration, p.frequency_493, p.amplitude_493)
        self.addDDS(p.channel_650, self.start + sd_delay, \
                     p.state_detection_duration, p.frequency_650, p.amplitude_650)

        # For standard state detection we want a little bit more space between the DDS turning
        # on and off
        #self.addTTL(p.TTL_493_DDS, self.start, p.state_detection_duration + 3*sd_delay)
        self.addTTL(p.TTL_493, self.start, p.state_detection_duration + 3*sd_delay)
        self.addTTL(p.TTL_650, self.start, p.state_detection_duration + 3*sd_delay)

        # Count photons during doppler cooling to monitor for dropouts
        self.addTTL('ReadoutCount', self.start, p.state_detection_duration)
        self.end = self.start + p.state_detection_duration + 3*sd_delay
