from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.DopplerCooling133 import doppler_cooling_133
from sub_sequences.StatePreparation133 import state_prep_133
from sub_sequences.Microwaves133 import microwaves_133
from sub_sequences.Shelving1762 import shelving_1762
from sub_sequences.Shelving133_Sub import shelving_133_sub
from sub_sequences.Shelving133_585_Sub import shelving_133_585_sub
from sub_sequences.ShelvingStateDetection import shelving_state_detection
from sub_sequences.Deshelving133 import deshelving_133
from sub_sequences.DeshelveLED import deshelve_led
from labrad.units import WithUnit


class shelving(pulse_sequence):

    required_parameters = [
                      ('Shelving', 'Scan'),
                      ('Shelving', 'Scan_Laser'),
                          ]

    required_subsequences = [doppler_cooling_133, state_prep_133, shelving_133_sub, shelving_133_585_sub, shelving_1762, \
                             microwaves_133, shelving_state_detection, deshelving_133, deshelve_led]

    def sequence(self):

        self.p = self.parameters.Shelving

        self.end = WithUnit(10.0,'us')
        self.addSequence(doppler_cooling_133)
        #self.addSequence(state_prep_133)
        #self.addSequence(microwaves_133)
        #self.addSequence(shelving_1762)
#        self.addSequence(shelving_133_sub)
        if self.p.Scan_Laser == '585nm':          
            self.addSequence(shelving_133_585_sub)
        # if self.p.Scan_Laser == '455nm':          
        #         self.addSequence(shelving_133_sub)    
        elif self.p.Scan_Laser == '1762nm':          
            self.addSequence(shelving_1762)    
        else:
#            print "adding shelving_133 sub sequence"
            self.addSequence(shelving_133_sub)    
            
            
        if self.p.Scan == 'deshelve':           
            self.addSequence(deshelving_133)
        elif self.p.Scan == 'frequency' and self.p.Scan_Laser == '614nm':
            self.addSequence(deshelving_133)

        self.addSequence(shelving_state_detection)
        self.addSequence(deshelve_led)


