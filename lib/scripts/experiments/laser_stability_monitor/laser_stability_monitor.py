import labrad
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
import time
import socket
import os


class lasermonitor(QsimExperiment):

    name = 'Laser Monitor'

    exp_parameters = []
    exp_parameters.append(('lasermonitor', 'lasers'))
    exp_parameters.append(('lasermonitor', 'measuretime'))

    def initialize(self, cxn, context, ident):

        self.ident = ident
        self.cxnwlm = labrad.connect('10.97.112.2',
                                     name=socket.gethostname() + " Laser Monitor",
                                     password=os.environ['LABRADPASSWORD'])

        self.wlm = self.cxnwlm.multiplexerserver

    def run(self, cxn, context):

        '''
        Main loop
        '''

        self.inittime = time.time()
        self.initfreq = self.wlm.get_frequency(int(self.p.lasermonitor.lasers[-1]))
        self.setup_datavault('Elapsed Time', 'Frequency Deviation')
        self.setup_grapher('current')
        while (time.time() - self.inittime) <= self.p.lasermonitor.measuretime['s']:
            should_stop = self.pause_or_stop()
            if should_stop:
                break
            freq = self.wlm.get_frequency(int(self.p.lasermonitor.lasers[-1]))
            try:
                self.dv.add(time.time() - self.inittime, 1e6*(self.initfreq - freq))
            except:
                pass
            progress = float(time.time() - self.inittime)/self.p.lasermonitor.measuretime['s']
            self.sc.script_set_progress(self.ident, progress)

    def finalize(self, cxn, context):
        self.cxnwlm.disconnect()


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = lasermonitor(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
