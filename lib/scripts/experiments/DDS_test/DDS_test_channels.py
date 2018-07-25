import labrad
from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment


class DDS_test_channels(experiment):

    name = 'DDS channel tester'

    exp_parameters = []

    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters

    def initialize(self, cxn, context, ident):
        self.ident = ident
        from labrad.units import WithUnit as U
        self.U = U
        self.cxn = labrad.connect(name = 'DDS Test')
        self.pulser = self.cxn.pulser
        self.starttime = self.U(0.001, 's')
        self.starttime1 = self.U(0.001, 's') - self.U(335.0,'ns')

        self.chan = 'LF DDS'
        self.duration = self.U(.000001,'s')
        self.advance = self.U(-0.0000002, 's')
        self.frequency = self.U(26.286,'MHz')
        self.frequency1 = self.U(100.0,'MHz')
        self.amp = self.U(-5.0, 'dBm')
        self.amp1 = self.U(-47.0, 'dBm')
        self.phase = self.U(0.0, 'deg')
        self.phase1 = self.U(180.0, 'deg')
        self.ramp_rate = self.U(0.0, 'MHz')
        self.amp_rate1 = self.U(3.0, 'dB')
        self.amp_rate = self.U(0.0, 'dB')
        self.ttl = 'TTL4'

    def run(self, cxn, context):

        '''
        This experiment turns the selected DDS's off for a duration, then
        sets them to the given parameters for that duration then off for
        the same duration
        '''

        self.pulser.new_sequence()

        self.pulser.add_ttl_pulse(self.ttl, self.starttime, 3*self.duration)

        self.pulser.add_dds_pulses([(self.chan, self.starttime1 - self.U(2.0,'us'),
                                     self.U(2.0,'us'),
                                     self.frequency,
                                     self.amp1,
                                     self.phase,
                                     self.ramp_rate,
                                     self.amp_rate)])

        self.pulser.add_dds_pulses([(self.chan, self.starttime1,
                                     self.duration + self.advance,
                                     self.frequency,
                                     self.amp,
                                     self.phase,
                                     self.ramp_rate,
                                     self.amp_rate)])

        self.pulser.add_dds_pulses([(self.chan, self.starttime1 + self.duration + self.advance,
                                     self.duration,
                                     self.frequency,
                                     self.amp,
                                     self.phase1,
                                     self.ramp_rate,
                                     self.amp_rate)])


        self.pulser.add_dds_pulses([(self.chan, self.starttime1 + 2*self.duration + self.advance,
                                     self.duration - self.advance,
                                     self.frequency,
                                     self.amp,
                                     self.phase,
                                     self.ramp_rate,
                                     self.amp_rate)])

        self.pulser.program_sequence()
        self.pulser.start_number(1)
        self.pulser.wait_sequence_done()
        self.pulser.stop_sequence()

    def finalize(self, cxn, context):
        self.cxn.disconnect()

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = DDS_test_channels(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)




