from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.DopplerCooling import doppler_cooling
from sub_sequences.ProbeLaser import probe_laser
from labrad.units import WithUnit



class probe_line_scan(pulse_sequence):

    required_parameters = []
    required_parameters.extend(doppler_cooling.all_required_parameters())
    required_parameters.extend(probe_laser.all_required_parameters())

    required_subsequences = [doppler_cooling, probe_laser]

    def sequence(self):
        self.addSequence(doppler_cooling)
        self.addSequence(probe_laser)




