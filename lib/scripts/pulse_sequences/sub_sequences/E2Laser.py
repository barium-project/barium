from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit


class e2laser(pulse_sequence):

    required_parameters = [

                           ('E2Laser', 'TTL_1762_eom'),
                           ('E2Laser', 'TTL_493_DDS'),                           
                           ('E2Laser', 'exposure532_time'),
                           ('E2Laser', 'channel_493'),
                           ('E2Laser', 'frequency_493'),
                           ('E2Laser', 'amplitude_493'),
                           ('E2Laser', 'channel_650'),
                           ('E2Laser', 'frequency_650'),
                           ('E2Laser', 'amplitude_650'),
                           ('E2Laser', 'USE_493_and_650'),
                           ('E2Laser', 'channel_614_1'),
                           ('E2Laser', 'frequency_614_1'),
                           ('E2Laser', 'amplitude_614_1'),
                           ('E2Laser', 'channel_614_2'),
                           ('E2Laser', 'frequency_614_2'),
                           ('E2Laser', 'amplitude_614_2'),
                           ('E2Laser', 'USE_614_1'),
                           ('E2Laser', 'USE_614_2'),
                           ('E2Laser', 'AOM_TTL_614_1'),
                           ('E2Laser', 'AOM_TTL_614_2'),
                           ('E2Laser', 'USE_532'),
                           ('E2Laser', 'TTL_532_AOM'),
                           ('E2Laser', 'channel_532'),
                           ('E2Laser', 'frequency_532'),
                           ('E2Laser', 'amplitude_532'),
                           ('E2Laser', 'spectroscopy_start'),
                           ('E2Laser', 'E2_duration'),
                           ('E2Laser', 'laser_duration'),
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
            
##            if  p.USE_493_and_650 == 'True':
##                self.addDDS(p.channel_493, self.start + switch_on_delay - amp_change_delay, p.laser_duration, p.frequency_493, p.amplitude_493)
##                self.addDDS(p.channel_650, self.start + switch_on_delay - amp_change_delay, p.laser_duration, p.frequency_650, p.amplitude_650)
##                self.addTTL(p.TTL_1762_eom, self.start + switch_on_delay - amp_change_delay, p.laser_duration)
##
##            elif p.USE_614_1 == 'True' and p.USE_614_2== 'False':
##                self.addDDS(p.channel_614_1, self.start + switch_on_delay - amp_change_delay, p.laser_duration, p.frequency_614_1, p.amplitude_614_1)
##                self.addTTL(p.TTL_1762_eom, self.start + switch_on_delay - amp_change_delay, p.laser_duration)
##                self.addTTL(p.TTL_493_DDS, self.start, p.laser_duration + 2*switch_on_delay)
##                self.addTTL(p.AOM_TTL_614_1, self.start + switch_on_delay, p.laser_duration)

##            elif p.USE_532 == 'True':
            if p.USE_532 == 'True':
                self.addDDS(p.channel_532, self.start + switch_on_delay - amp_change_delay, p.exposure532_time, p.frequency_532, p.amplitude_532)
                self.addTTL(p.TTL_532_AOM, self.start + switch_on_delay, p.exposure532_time)
                self.addTTL(p.TTL_1762_eom,self.start + switch_on_delay + p.spectroscopy_start, p.E2_duration)                
#                self.addTTL(p.TTL_1762_eom, p.laser_duration-p.E2_duration, p.E2_duration)
                self.end = self.start + switch_on_delay +  p.exposure532_time + switch_on_delay


##            elif p.USE_614_2 == 'True' and p.USE_614_1== 'False':
##                self.addDDS(p.channel_614_2, self.start + switch_on_delay - amp_change_delay, p.laser_duration, p.frequency_614_2, p.amplitude_614_2)
##                self.addTTL(p.TTL_1762_eom, self.start + switch_on_delay - amp_change_delay, p.laser_duration)
##                self.addTTL(p.TTL_493_DDS, self.start, p.laser_duration + 2*switch_on_delay)
##                self.addTTL(p.AOM_TTL_614_2, self.start + switch_on_delay, p.laser_duration)
##
##            elif p.USE_614_1 == 'True' and p.USE_614_2== 'True':
##                self.addDDS(p.channel_614_1, self.start + switch_on_delay - amp_change_delay, p.laser_duration, p.frequency_614_1, p.amplitude_614_1)
##                self.addDDS(p.channel_614_2, self.start + switch_on_delay - amp_change_delay, p.laser_duration, p.frequency_614_2, p.amplitude_614_2)
##                self.addTTL(p.AOM_TTL_614_1, self.start + switch_on_delay, p.laser_duration)
##                self.addTTL(p.AOM_TTL_614_2, self.start + switch_on_delay, p.laser_duration)
##                self.addTTL(p.TTL_1762_eom, self.start + switch_on_delay - amp_change_delay, p.laser_duration)
##                self.addTTL(p.TTL_493_DDS, self.start, p.laser_duration + 2*switch_on_delay)
                
            else:
                self.addTTL(p.TTL_1762_eom, self.start + switch_on_delay - amp_change_delay, p.laser_duration)
                self.addTTL(p.TTL_493_DDS, self.start, p.laser_duration + 2*switch_on_delay)            
                self.end = self.start + switch_on_delay +  p.laser_duration + switch_on_delay


#	def addDDS(self, channel, start, duration, frequency, amplitude, phase = WithUnit(0, 'deg'), ramp_rate = WithUnit(0,'MHz'), amp_ramp_rate = WithUnit(0,'dB')):

#            self.end = self.start + switch_on_delay +  p.laser_duration + switch_on_delay


        else:
            self.end = self.start




