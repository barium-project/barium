from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit


class e2laser(pulse_sequence):

    required_parameters = [

                           ('E2Laser', 'TTL_1762_eom'),
                           ('E2Laser', 'TTL_493_DDS'),                           
                           ('E2Laser', 'laser_duration'),
                           ('E2Laser', 'channel_493'),
                           ('E2Laser', 'frequency_493'),
                           ('E2Laser', 'amplitude_493'),
                           ('E2Laser', 'channel_650'),
                           ('E2Laser', 'frequency_650'),
                           ('E2Laser', 'amplitude_650'),
                           ('E2Laser', 'USE_493_and_650'),
                           ]


    def sequence(self):
        # start time is defined to be 0s.
        p = self.parameters.E2Laser

        # use this to turn the DDS to a very low power right before we turn it on
        # to avoid the weird 1us loss.
        #amp_off = WithUnit(-47.0,'dBm')
        switch_on_delay = WithUnit(2.0,'us')
        amp_change_delay = WithUnit(355.0,'ns')
         
        if p.laser_duration != 0:
            
            if  p.USE_493_and_650 == 'True':
                self.addDDS(p.channel_493, self.start + switch_on_delay - amp_change_delay, p.laser_duration, p.frequency_493, p.amplitude_493)
                self.addDDS(p.channel_650, self.start + switch_on_delay - amp_change_delay, p.laser_duration, p.frequency_650, p.amplitude_650)
                self.addTTL(p.TTL_1762_eom, self.start + switch_on_delay - amp_change_delay, p.laser_duration)
            
            else:
                self.addTTL(p.TTL_1762_eom, self.start + switch_on_delay - amp_change_delay, p.laser_duration)
                self.addTTL(p.TTL_493_DDS, self.start, p.laser_duration + 2*switch_on_delay)


#	def addDDS(self, channel, start, duration, frequency, amplitude, phase = WithUnit(0, 'deg'), ramp_rate = WithUnit(0,'MHz'), amp_ramp_rate = WithUnit(0,'dB')):

            self.end = self.start + switch_on_delay +  p.laser_duration + switch_on_delay

        else:
            self.end = self.start




