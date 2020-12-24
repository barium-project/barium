from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.E2Laser import e2laser
from sub_sequences.DopplerCooling133 import doppler_cooling_133
from sub_sequences.StatePreparation133 import state_prep_133
from sub_sequences.Microwaves133 import microwaves_133
from sub_sequences.ShelvingStateDetection import shelving_state_detection
from sub_sequences.Deshelving133 import deshelving_133
from sub_sequences.Deshelving1762 import deshelving_1762
from sub_sequences.DeshelveLED import deshelve_led
from labrad.units import WithUnit

class e2_metastable_prep(pulse_sequence):

    required_parameters = [
                           ('MetastablePrep','prep_state'),
                           ('MetastablePrep','detection_method'),
                           ]

    required_subsequences = [doppler_cooling_133, state_prep_133, microwaves_133, e2laser,\
                            shelving_state_detection, deshelving_133,\
                            deshelve_led, deshelving_1762]

    def sequence(self):

        p = self.parameters.MetastablePrep

        self.end = WithUnit(10.0,'us')
        self.addSequence(doppler_cooling_133)
        self.addSequence(state_prep_133)
        if p.prep_state == '1':
            self.addSequence(microwaves_133)
        self.addSequence(e2laser)
        self.addSequence(shelving_state_detection)
        if p.detection_method == "614 nm":
            self.addSequence(deshelving_133)
        else:
            self.addSequence(deshelving_1762)            
        self.addSequence(shelving_state_detection)
        self.addSequence(deshelve_led)
        self.addSequence(shelving_state_detection)