from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit


class doppler_cooling_133(pulse_sequence):

    required_parameters = [
                           ('DopplerCooling133', 'doppler_cooling_duration'),
                           ('DopplerCooling133', 'TTL_493_DDS'),
                           ('DopplerCooling133', 'TTL_493_SD'),
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
        # add a small delay for the switching on
        amp_change_delay = WithUnit(600.0,'ns')

        self.addDDS(p.channel_493, self.start - amp_change_delay, \
                     p.doppler_cooling_duration, p.frequency_493, p.amplitude_493)
        self.addDDS(p.channel_650, self.start - amp_change_delay, \
                     p.doppler_cooling_duration, p.frequency_650, p.amplitude_650)

        # Count photons during doppler cooling to monitor for dropouts
        self.addTTL('ReadoutCount', self.start, p.doppler_cooling_duration)
        self.end = self.start + p.doppler_cooling_duration

