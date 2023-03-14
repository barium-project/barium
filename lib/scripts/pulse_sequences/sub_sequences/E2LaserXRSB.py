from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit


class e2laserxrsb(pulse_sequence):

    required_parameters = [

                           ('E2LaserXRSB', 'TTL_1762_eom'),
                           ('E2LaserXRSB', 'TTL_493_DDS'),                           
                           ('E2LaserXRSB', 'laser_duration'),
                           ('E2LaserXRSB', 'TTL_prep'),
                           ('E2LaserXRSB', 'TTL_493'),
                           ('E2LaserXRSB', 'channel_493'),
                           ('E2LaserXRSB', 'frequency_493'),
                           ('E2LaserXRSB', 'amplitude_493'),
                           ('E2LaserXRSB', 'channel_650'),
                           ('E2LaserXRSB', 'frequency_650'),
                           ('E2LaserXRSB', 'amplitude_650'),
                           ('E2LaserXRSB', 'USE_493'),
                           ('E2LaserXRSB', 'USE_650'),
                           ('E2LaserXRSB', 'USE_585'),
                           ('E2LaserXRSB', 'channel_614_1'),
                           ('E2LaserXRSB', 'frequency_614_1'),
                           ('E2LaserXRSB', 'amplitude_614_1'),
                           ('E2LaserXRSB', 'channel_614_2'),
                           ('E2LaserXRSB', 'frequency_614_2'),
                           ('E2LaserXRSB', 'amplitude_614_2'),
                           ('E2LaserXRSB', 'USE_614_1'),
                           ('E2LaserXRSB', 'USE_614_2'),
                           ('E2LaserXRSB', 'TTL_585'),
                           ('E2LaserXRSB', 'TTL_650'),
                           ('E2LaserXRSB', 'AOM_TTL_614_1'),
                           ('E2LaserXRSB', 'AOM_TTL_614_2')
                            ]


    def sequence(self):
##        # start time is defined to be 0s.
##        p = self.parameters.E2LaserXRSB
##
##        # add a small delay for the switching on
##        amp_change_delay = WithUnit(2.0,'us')
##        amp_change_delay_2 = WithUnit(350.0,'ns')
##        switch_on_delay = WithUnit(2.0,'us')
##
##
##        if p.laser_duration != 0:
##
##
##            self.addTTL(p.TTL_1762_eom, self.start + switch_on_delay - amp_change_delay, p.laser_duration)
##
##            if  p.USE_493 == 'True':
##                self.addDDS(p.channel_493, self.start + switch_on_delay - amp_change_delay, p.laser_duration, p.frequency_493, p.amplitude_493)
##                self.addTTL(p.TTL_493, self.start, p.laser_duration + amp_change_delay)
##                self.addTTL(p.TTL_prep, self.start, p.laser_duration + amp_change_delay/2)
##                self.addTTL(p.TTL_493_DDS, self.start+ p.laser_duration, amp_change_delay)
##                
##            else:
##                self.addTTL(p.TTL_493_DDS, self.start, p.laser_duration + 2*switch_on_delay)
##                
##            if  p.USE_650 == 'True':
##                self.addDDS(p.channel_650, self.start + switch_on_delay - amp_change_delay, p.laser_duration, p.frequency_650, p.amplitude_650)
####                self.addTTL(p.TTL_650, self.start, p.laser_duration  + 2*switch_on_delay)
##                
##            if  p.USE_614_1 == 'True':
##                self.addDDS(p.channel_614_1, self.start + switch_on_delay - amp_change_delay, p.laser_duration, p.frequency_614_1, p.amplitude_614_1)
##                self.addTTL(p.AOM_TTL_614_1, self.start + switch_on_delay, p.laser_duration)
##
##            if  p.USE_614_2 == 'True':
##                self.addDDS(p.channel_614_2, self.start + switch_on_delay - amp_change_delay, p.laser_duration, p.frequency_614_2, p.amplitude_614_2)
##                self.addTTL(p.AOM_TTL_614_2, self.start + switch_on_delay, p.laser_duration)
##            if  p.USE_585 == 'True':
##                self.addTTL(p.TTL_585, self.start + switch_on_delay - amp_change_delay, p.laser_duration)
##            
##
##            self.end = self.start + switch_on_delay +  p.laser_duration + switch_on_delay
##
##        else:
##            self.end = self.start



            
        # start time is defined to be 0s.
        p = self.parameters.E2LaserXRSB

        # use this to turn the DDS to a very low power right before we turn it on
        # to avoid the weird 1us loss.
        #amp_off = WithUnit(-47.0,'dBm')
        switch_on_delay = WithUnit(2.0,'us')
        amp_change_delay = WithUnit(2.0,'us')
        amp_change_delay_2 = WithUnit(350.0,'ns')

        
        if p.laser_duration != 0:
            
            self.addTTL(p.TTL_1762_eom, self.start + switch_on_delay - amp_change_delay, p.laser_duration)

            if  p.USE_585 == 'True':
                self.addTTL(p.TTL_585, self.start + switch_on_delay - amp_change_delay, p.laser_duration)
            
            if  p.USE_493 == 'True':
                self.addDDS(p.channel_493, self.start + switch_on_delay - amp_change_delay, p.laser_duration, p.frequency_493, p.amplitude_493)
                self.addTTL(p.TTL_493, self.start, p.laser_duration + amp_change_delay)
                self.addTTL(p.TTL_prep, self.start, p.laser_duration + amp_change_delay/2)
                self.addTTL(p.TTL_493_DDS, self.start+ p.laser_duration, amp_change_delay)
            else:
                self.addTTL(p.TTL_493_DDS, self.start, p.laser_duration + 2*switch_on_delay)
            
            if  p.USE_650 == 'True':
                self.addDDS(p.channel_650, self.start + switch_on_delay - amp_change_delay, p.laser_duration, p.frequency_650, p.amplitude_650)
##                self.addTTL(p.TTL_650, self.start, p.laser_duration  + 2*switch_on_delay)
                
            if  p.USE_614_1 == 'True':
                self.addDDS(p.channel_614_1, self.start + switch_on_delay - amp_change_delay, p.laser_duration, p.frequency_614_1, p.amplitude_614_1)
                self.addTTL(p.AOM_TTL_614_1, self.start + switch_on_delay, p.laser_duration)

            if  p.USE_614_2 == 'True':
                self.addDDS(p.channel_614_2, self.start + switch_on_delay - amp_change_delay, p.laser_duration, p.frequency_614_2, p.amplitude_614_2)
                self.addTTL(p.AOM_TTL_614_2, self.start + switch_on_delay, p.laser_duration)


#	def addDDS(self, channel, start, duration, frequency, amplitude, phase = WithUnit(0, 'deg'), ramp_rate = WithUnit(0,'MHz'), amp_ramp_rate = WithUnit(0,'dB')):

            self.end = self.start + switch_on_delay +  p.laser_duration + switch_on_delay

        else:
            self.end = self.start




