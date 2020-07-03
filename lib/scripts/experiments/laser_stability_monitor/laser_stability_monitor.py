import labrad
from twisted.internet.defer import inlineCallbacks, returnValue
from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment

from config.multiplexerclient_config import multiplexer_config
import time
import socket
import os
import datetime as datetime


class laser_stability_monitor(experiment):

    name = 'Laser Monitor'

    exp_parameters = []
    exp_parameters.append(('LaserMonitor', 'WM_Channel'))
    exp_parameters.append(('LaserMonitor', 'Measure_Time'))


    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters


    def initialize(self, cxn, context, ident):

        self.ident = ident
        self.wm_p = multiplexer_config.info
        self.ip = multiplexer_config.ip
        self.cxnwlm = labrad.connect(self.ip,
                                     name=socket.gethostname() + " Laser Monitor",
                                     password=os.environ['LABRADPASSWORD'])
        self.cxn = labrad.connect(name = 'Laser Monitor')

        self.wlm = self.cxnwlm.multiplexerserver
        #self.grapher = self.cxn.grapher
        self.grapher = self.cxn.real_simple_grapher
        self.dv = self.cxn.data_vault
        self.p = self.parameters

        self.set_up_datavault()
        self.laser = int(self.p.LaserMonitor.WM_Channel)
       

    def run(self, cxn, context):

        '''
        Main loop
        '''

        self.inittime = time.time()
        self.initfreq = self.wlm.get_frequency(self.laser)
        
        self.dv.add_parameter('Initial Frequency',self.initfreq)
        self.dv.add_parameter('WM Channel',self.laser)
        while (time.time() - self.inittime) <= self.p.LaserMonitor.Measure_Time['s']:
            should_stop = self.pause_or_stop()
            if should_stop:
                break
            freq = self.wlm.get_frequency(self.laser)
            
            try:
                self.dv.add(time.time() - self.inittime, 1e6*(self.initfreq - freq))
            except:
                pass
            #progress = float(time.time() - self.inittime)/self.p.LaserMonitor.measuretime['s']
            #self.sc.script_set_progress(self.ident, progress)


    def set_up_datavault(self):
        # set up folder
        date = datetime.datetime.now()
        year  = `date.year`
        month = '%02d' % date.month  # Padded with a zero if one digit
        day   = '%02d' % date.day    # Padded with a zero if one digit
        trunk = year + '_' + month + '_' + day
        self.dv.cd(['',year,month,trunk],True)
        dataset = self.dv.new('Laser Monitor',[('Time', 's')], [('Frequency Deviation', 'Frequency', 'MHz')])
        # add dv params
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter])

        # Set live plotting
        self.grapher.plot(dataset, 'Laser Monitor', False)


    def finalize(self, cxn, context):
        self.cxnwlm.disconnect()


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = laser_stability_monitor(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
