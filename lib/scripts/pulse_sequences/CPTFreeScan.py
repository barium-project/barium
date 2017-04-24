from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.DopplerCooling import doppler_cooling
from sub_sequences.ProbeLaser import probe_laser
from sub_sequences.RepumpLaser import repump_laser
from sub_sequences.PhotonTimeTags import photon_timetags
from labrad.units import WithUnit



class cpt_free_scan(pulse_sequence):

    required_parameters = [('CPTFreeScan', 'Repump_Cycles'),
                           ('CPTFreeScan', 'Repump_Duration')]

    required_parameters.extend(doppler_cooling.all_required_parameters())
    required_parameters.extend(probe_laser.all_required_parameters())
    required_parameters.extend(photon_timetags.all_required_parameters())


    required_subsequences = [doppler_cooling, probe_laser, photon_timetags]

    def sequence(self):
        self.start = WithUnit(0.0,'us')
        self.p = self.parameters
        self.t1 = self.p.DopplerCooling.doppler_cooling_duration
        self.t2 = self.p.DopplerCooling.off_time

        self.cycles = self.p.CPTFreeScan.Repump_Cycles
        self.repump_time = self.p.RepumpLaser.Repump_Duration
        self.probe_time = self.p.ProbeLaser.probe_laser_duration


        # Doppler cool for specified time
        self.addSequence(doppler_cooling, position = self.start)
        self.end = self.start + self.t1
        # Start time tags
        self.addSequence(photon_timetags)

        # Since the channels are autoinverted, setting the repump high turns it off
        # So we set both to start at the same time. After they finish we add dead time
        # for the repumper to be on by pushing out self.end
        for i in range(self.cycles):
            self.addSequence(probe_laser)
            self.addSequence(repump_laser)
            self.end = self.end + self.probe_time + self.repump_time




