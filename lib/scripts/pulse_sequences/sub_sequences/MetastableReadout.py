from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit


class metastable_readout(pulse_sequence):

    required_parameters = [
                           ('MetastableReadout', 'readout_duration'),
                           #('MetastableReadout', 'TTL_614_Readout'),
                           #('MetastableReadout', 'use_sideband'),
                           ('MetastableReadout', 'TTL_614'),       #int channel number
                           ('MetastableReadout', 'TTL_614_F12'),
                           ('MetastableReadout', 'TTL_614_F22'),
                           ('MetastableReadout', 'USE_TTL_614'),   #bool on/off
                           ('MetastableReadout', 'USE_TTL_614_F12'),
                           ('MetastableReadout', 'USE_TTL_614_F22'),
                           ]

    def sequence(self):
        # start time is defined to be 0s.
        p = self.parameters.MetastableReadout

        if p.readout_duration != 0:

            self.addTTL('TTL2', self.start, p.readout_duration)

            if  p.USE_TTL_614 == 'True':
                self.addTTL(p.TTL_614, self.start, p.readout_duration)

            #if  p.use_sideband == 'True':
                #self.addTTL(p.TTL_614_Readout, self.start, p.readout_duration)

            if  p.USE_TTL_614_F12 == 'True':
                self.addTTL(p.TTL_614_F12, self.start, p.readout_duration)

            if  p.USE_TTL_614_F22 == 'True':
                self.addTTL(p.TTL_614_F22, self.start, p.readout_duration)

        self.end = self.start + p.readout_duration + WithUnit(650.0, 'ns')

