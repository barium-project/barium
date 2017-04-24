from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.DopplerCooling import doppler_cooling
from sub_sequences.ProbeLaser import probe_laser
from sub_sequences.PhotonTimeTags import photon_timetags
from labrad.units import WithUnit



class probe_line_scan(pulse_sequence):

    required_parameters = []
    required_parameters.extend(doppler_cooling.all_required_parameters())
    required_parameters.extend(probe_laser.all_required_parameters())
    required_parameters.extend(photon_timetags.all_required_parameters())


    required_subsequences = [doppler_cooling, probe_laser, photon_timetags]

    def sequence(self):
        self.start = WithUnit(0.0,'us')
        self.p = self.parameters
        self.t1 = self.p.DopplerCooling.doppler_cooling_duration
        self.addSequence(doppler_cooling, position = self.start)
        self.addSequence(probe_laser, position = self.start + self.t1)
        self.addSequence(photon_timetags, position = self.start + self.t1)



