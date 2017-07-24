from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.DopplerCooling133 import doppler_cooling_133
from sub_sequences.StatePreparation133 import state_prep_133
from sub_sequences.StateDetection133 import state_detection_133
from labrad.units import WithUnit
from treedict import TreeDict


class optical_pumping_133(pulse_sequence):

    required_parameters = [('OpticalPumping133', 'dds_channel'),
                           ('OpticalPumping133', 'dds_frequency'),
                           ('OpticalPumping133', 'dds_amplitude'),







                           ]

    required_parameters.extend(doppler_cooling_133.all_required_parameters())
    required_parameters.extend(state_prep_133.all_required_parameters())
    required_parameters.extend(state_detection_133.all_required_parameters())


    required_subsequences = [doppler_cooling_133, state_prep_133, state_detection_133]

    def sequence(self):
        self.end = WithUnit(10.0,'us')
        self.p = self.parameters

        self.op = self.p.OpticalPumping133
        self.channel = self.op.dds_channel
        self.freq = self.op.dds_frequency
        self.amp = self.op.dds_amplitude

        self.d = self.p.DopplerCooling133
        self.cool_time = self.d.doppler_cooling_duration

        self.sp = self.p.StatePreparation133
        self.prep_time = self.sp.state_prep_duration

        self.sd = self.p.StateDetection133
        self.sd_time = self.sd.state_detection_duration

        self.total_time = self.cool_time + self.prep_time + self.sd_time

        self.addDDS(self.channel, self.end,  self.total_time, self.freq, self.amp)
        self.end =+ WithUnit(1.0,'us')
        self.addSequence(doppler_cooling_133)
        self.addSequence(state_prep_133)
        self.addSequence(state_detection_133)



