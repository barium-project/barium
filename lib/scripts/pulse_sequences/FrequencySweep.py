from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit


class frequency_sweep(pulse_sequence):

    required_parameters = [
                           ('FrequencySweep', 'scan_dds_channel'),
                           ('FrequencySweep', 'freq_1'),
                           ('FrequencySweep', 'freq_2'),
                           ('FrequencySweep', 'freq_3'),
                           ('FrequencySweep', 'scan_dds_amplitude'),
                           ('FrequencySweep', 'LO_freq'),
                           ('FrequencySweep', 'LO_amp'),
                           ('FrequencySweep', 'time_per_freq'),
                           ('FrequencySweep', 'b_field'),
                           ('FrequencySweep', 'hyperfine_freq')
                           ]

    def sequence(self):
        #self.start = WithUnit(1.0,'us')

        self.p = self.parameters.FrequencySweep

        self.scan_channel = self.p.scan_dds_channel
        self.scan_amp = self.p.scan_dds_amplitude
        self.time_per_freq = self.p.time_per_freq

        # Add the scan frequencies
        self.addDDS(self.scan_channel, self.start, self.time_per_freq, self.p.freq_1, self.scan_amp)
        self.addDDS(self.scan_channel, self.start + self.time_per_freq, self.time_per_freq, self.p.freq_2, self.scan_amp)
        self.addDDS(self.scan_channel, self.start + 2*self.time_per_freq, self.time_per_freq, self.p.freq_3, self.scan_amp)


