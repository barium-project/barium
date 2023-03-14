from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit


class greenlaser(pulse_sequence):

    required_parameters = [

                           ('GreenLaser', 'TTL_532_AOM'),
                           ('GreenLaser', 'channel_532'),
                           ('GreenLaser', 'frequency_532'),
                           ('GreenLaser', 'amplitude_532'),
                           ('GreenLaser', 'laser_duration'),
                           ('GreenLaser', 'TTL_493_DDS'),
                           ('GreenLaser', 'TTL_493'),#see RamseyDelay
                        ]


    def sequence(self):
        # start time is defined to be 0s.
        p = self.parameters.GreenLaser

        # use this to turn the DDS to a very low power right before we turn it on
        # to avoid the weird 1us loss.
        amp_off = WithUnit(-47.0,'dBm')
        switch_on_delay = WithUnit(2.0,'us')
        amp_change_delay = WithUnit(355.0,'ns')

        if p.laser_duration != 0:
            # Make sure 493 is off
            self.addTTL(p.TTL_493_DDS, self.start, switch_on_delay + p.laser_duration)
            self.addTTL(p.TTL_493, self.start, switch_on_delay + p.laser_duration)

            # Turn the DDS on at low power (amp_off)
            self.addDDS(p.channel_532, self.start - amp_change_delay, switch_on_delay, p.frequency_532, amp_off)


            # Turn the DDS on at desired power
            self.addDDS(p.channel_532, self.start + switch_on_delay - amp_change_delay, p.laser_duration, p.frequency_532, p.amplitude_532)
            # Turn on TTL switch for 532 AOM
            self.addTTL(p.TTL_532_AOM, self.start + switch_on_delay, p.laser_duration)


            self.end = self.start + switch_on_delay + p.laser_duration

        else:
            self.end = self.start

