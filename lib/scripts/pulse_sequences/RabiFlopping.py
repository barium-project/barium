from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.DopplerCooling133 import doppler_cooling_133
from sub_sequences.StatePreparation133 import state_prep_133
from sub_sequences.Microwaves133 import microwaves_133
from sub_sequences.Composite_1 import composite_1
from sub_sequences.Composite_2 import composite_2
from sub_sequences.Composite_3 import composite_3
from sub_sequences.Composite_4 import composite_4
from sub_sequences.Spin_Echo import spin_echo
from sub_sequences.Su_1 import su_1
from sub_sequences.E2Laser import e2laser
from sub_sequences.Shelving133_Sub import shelving_133_sub
from sub_sequences.ShelvingStateDetection import shelving_state_detection
from sub_sequences.StandardStateDetection import standard_state_detection
from sub_sequences.Deshelving133 import deshelving_133
from sub_sequences.DeshelveLED import deshelve_led
from labrad.units import WithUnit

class rabi_flopping(pulse_sequence):

    required_parameters = [
                           ('RabiFlopping', 'microwave_pulse_sequence'),
                           ('RabiFlopping','State_Detection'),
                           ('RabiFlopping','number_of_microwave_pulses'),
                           ('RabiFlopping','use_1762'),
                           ]

    required_subsequences = [doppler_cooling_133, state_prep_133, microwaves_133, composite_1, composite_2, spin_echo, e2laser, \
                             composite_3, composite_4, su_1, shelving_133_sub,\
                            standard_state_detection, shelving_state_detection,\
                                deshelving_133, deshelve_led]

    def sequence(self):

        p = self.parameters.RabiFlopping

        self.end = WithUnit(10.0,'us')
        self.addSequence(doppler_cooling_133)
        self.addSequence(state_prep_133)

        # Do n microwave pulses. This is only for checking
        # pi pulse fidelity
        for i in range(int(p.number_of_microwave_pulses)):
            if p.microwave_pulse_sequence == 'single':
                self.addSequence(microwaves_133)
            elif p.microwave_pulse_sequence == 'composite_1':
                self.addSequence(composite_1)
            elif p.microwave_pulse_sequence == 'composite_2':
                self.addSequence(composite_2)
            elif p.microwave_pulse_sequence == 'composite_3':
                self.addSequence(composite_3)
            elif p.microwave_pulse_sequence == 'composite_4':
                self.addSequence(composite_4)
            elif p.microwave_pulse_sequence == 'spin_echo':
                self.addSequence(spin_echo)
            elif p.microwave_pulse_sequence == 'su_1':
                self.addSequence(su_1)

        if p.use_1762 == "True":
            self.addSequence(e2laser)
            
        if p.State_Detection == 'spin-1/2':
            self.addSequence(standard_state_detection)

        elif p.State_Detection == 'shelving':
            if p.use_1762 == "False":
                self.addSequence(shelving_133_sub)
            self.addSequence(shelving_state_detection)
            self.addSequence(deshelve_led)
         
