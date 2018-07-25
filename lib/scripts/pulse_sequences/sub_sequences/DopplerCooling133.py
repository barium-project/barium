from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit


class doppler_cooling_133(pulse_sequence):

    required_parameters = [
                           ('DopplerCooling133', 'doppler_cooling_duration'),
                           ('DopplerCooling133', 'TTL_493_DDS'),
                           ('DopplerCooling133', 'TTL_493'),
                           ('DopplerCooling133', 'TTL_650'),
                           ('DopplerCooling133', 'channel_493'),
                           ('DopplerCooling133', 'frequency_493'),
                           ('DopplerCooling133', 'amplitude_493'),
                           ('DopplerCooling133', 'channel_650'),
                           ('DopplerCooling133', 'frequency_650'),
                           ('DopplerCooling133', 'amplitude_650'),
                           ]

    def sequence(self):
        # start time is defined to be 0s.
        p = self.parameters.DopplerCooling133

       # use this to turn the DDS to a very low power right before we turn it on
        # to avoid the weird 1us loss.
        amp_off = WithUnit(-47.0,'dBm')
        switch_on_delay = WithUnit(2.0,'us')

        # add a small delay for the switching on
        amp_change_delay = WithUnit(335.0,'ns')

        self.addTTL(p.TTL_493_DDS, self.start + switch_on_delay, p.doppler_cooling_duration)

        self.addDDS(p.channel_493, self.start - amp_change_delay,\
                     switch_on_delay, p.frequency_493, amp_off)
        self.addDDS(p.channel_650, self.start - amp_change_delay,\
                    switch_on_delay, p.frequency_650, amp_off)

        self.addDDS(p.channel_493, self.start + switch_on_delay - amp_change_delay, \
                     p.doppler_cooling_duration, p.frequency_493, p.amplitude_493)
        self.addDDS(p.channel_650, self.start + switch_on_delay - amp_change_delay, \
                     p.doppler_cooling_duration, p.frequency_650, p.amplitude_650)

        # Count photons during doppler cooling to monitor for dropouts
        self.addTTL('ReadoutCount', self.start, p.doppler_cooling_duration)
        self.end = self.start + switch_on_delay + p.doppler_cooling_duration

