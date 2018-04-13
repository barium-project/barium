
import labrad
from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict
"""
For now in this experiment, Doppler cooling just consists of turning on one EOM sideband.
This is done with an rf switch, so all we need is a TTL high for a specified amount
of time. If/When we use a dds, we'll need to add to this subsequence

4/14/2017
AS of now the default state of these TTL switches is high, they are auto inverted,
so that we cool by default. This means to turn off Doppler cooling we need to write
a TTL high for the off time
"""

class test_sequence(pulse_sequence):

    required_parameters = [

                           ]

    def sequence(self):
        # start time is defined to be 0s.
        self.p = self.parameters.test_sequence
        # Testing TTL overlap problem
        self.addTTL('TTL7', U(1.0,'s'),U(3.0,'s'))
        self.addTTL('TTL7', U(2.0,'s'),U(2.0,'s'))


cxn = labrad.connect(name = 'Shelving')
pulser = cxn.pulser
pulse_sequence = test_sequence(TreeDict.fromdict({}))
pulse_sequence.programSequence(pulser)
pulser.start_number(int(1))
pulser.wait_sequence_done()
pulser.stop_sequence()
