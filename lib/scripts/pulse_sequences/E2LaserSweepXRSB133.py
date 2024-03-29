from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.DopplerCooling133 import doppler_cooling_133
from sub_sequences.StatePreparation133 import state_prep_133
from sub_sequences.E2Laser import e2laser
#from sub_sequences.Composite_1 import composite_1
#from sub_sequences.Shelving133_Sub import shelving_133_sub
#from sub_sequences.ShelvingStateDetection import shelving_state_detection
from sub_sequences.ShelvingStateDetection import shelving_state_detection
from sub_sequences.StandardStateDetection import standard_state_detection
from sub_sequences.Microwaves133 import microwaves_133
from sub_sequences.Deshelving133 import deshelving_133
from sub_sequences.DeshelveLED import deshelve_led
from sub_sequences.DeshelveLEDXRSB import deshelve_led_xrsb
from sub_sequences.E2LaserXRSB import e2laserxrsb
from sub_sequences.Shelving133_Sub import shelving_133_sub
from sub_sequences.MicrowavesXRSB import microwaves_xrsb
from sub_sequences.StatePreparationXRSB import state_prep_xrsb
from labrad.units import WithUnit

class e2_laser_sweep_xrsb_133(pulse_sequence):

    required_parameters = [ ('E2LaserSweepXRSB133', 'State_Detection'),
                            ('E2LaserSweepXRSB133', 'pulsed'),
                            ('E2LaserSweepXRSB133', 'cycles')
                           ]

    required_subsequences = [doppler_cooling_133, state_prep_133, state_prep_xrsb, microwaves_133, microwaves_xrsb, e2laser, e2laserxrsb,\
                             shelving_state_detection, shelving_133_sub, standard_state_detection, deshelving_133,\
                            deshelve_led,deshelve_led_xrsb]

#    required_subsequences = [doppler_cooling_133, state_prep_133, microwaves_133, composite_1, \
#                            shelving_133_sub, standard_state_detection, shelving_state_detection, deshelving_133]


    def sequence(self):
        self.end = WithUnit(10.0,'us')
        p = self.parameters.E2LaserSweepXRSB133
        self.addSequence(doppler_cooling_133)
        if p.pulsed == 'True':
            for i in range(int(p.cycles)):
                self.addSequence(state_prep_xrsb)
                self.addSequence(e2laserxrsb)
        else:
            self.addSequence(state_prep_xrsb)
            self.addSequence(microwaves_xrsb)
            self.addSequence(e2laserxrsb)
##        self.addSequence(state_prep_xrsb)
##        self.addSequence(microwaves_xrsb)
##        self.addSequence(e2laser)
##        self.addSequence(shelving_133_sub)
        self.addSequence(state_prep_133)
        self.addSequence(microwaves_133)
        self.addSequence(e2laser)
        self.addSequence(shelving_state_detection)
        self.addSequence(deshelve_led)

