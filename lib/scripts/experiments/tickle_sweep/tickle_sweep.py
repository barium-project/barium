import labrad
from twisted.internet.defer import inlineCallbacks, returnValue
from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
from labrad.units import WithUnit
import numpy as np
from config.multiplexerclient_config import multiplexer_config
import time
import socket
import os
import datetime as datetime


class tickle_sweep(experiment):

    name = 'Tickle Sweep'

    exp_parameters = [('TickleSweep', 'Start_Frequency'),
                      ('TickleSweep', 'Stop_Frequency'),
                      ('TickleSweep', 'Frequency_Step'),
                      ('TickleSweep', 'Amplitude'),
                      ('TickleSweep', 'Num_Pts_to_Avg'),]
    
    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters


    def initialize(self, cxn, context, ident):

        self.ident = ident
        self.wm_p = multiplexer_config.info
        self.cxn = labrad.connect(name = 'Tickle Sweep')
        self.cxnwlm = labrad.connect(multiplexer_config.ip, name = 'Tickle Sweep', password = 'lab')


        
##        self.wm_p = multiplexer_config.info
##        self.ip = multiplexer_config.ip
##
##
##        self.wlm = self.cxnwlm.multiplexerserver
        
        #self.grapher = self.cxn.grapher
        self.grapher = self.cxn.real_simple_grapher
        self.dv = self.cxn.data_vault

        # Define variables to be used
        self.p = self.parameters
        self.start_frequency = self.p.TickleSweep.Start_Frequency
        self.stop_frequency = self.p.TickleSweep.Stop_Frequency
        self.step_frequency = self.p.TickleSweep.Frequency_Step
        self.Amplitude = self.p.TickleSweep.Amplitude
        self.numAvg = self.p.TickleSweep.Num_Pts_to_Avg



        self.PMTFlow = self.cxn.normalpmtflow
        self.agilent = self.cxn.agilent_33220a_server

        self.agilent.select_device()

        # Get contexts for saving the data sets
        self.c_pmt = self.cxn.context()

        self.set_up_datavault()
       

    def run(self, cxn, context):

        '''
        Main loop
        '''
        freq = np.linspace(self.start_frequency['Hz'],self.stop_frequency['Hz'],\
                    int((abs(self.stop_frequency['Hz']-self.start_frequency['Hz'])/self.step_frequency['Hz'])+1))

        self.agilent.frequency(self.start_frequency)
        self.agilent.amplitude(self.Amplitude)
        self.agilent.output(True)

        for i in range(len(freq)):
            if self.pause_or_stop():
                self.agilent.output(False)
                break

            self.agilent.frequency(WithUnit(freq[i], 'Hz'))
            time.sleep(.3) # time to switch frequencies

            if self.PMTFlow.isrunning():#BUGBUG  -- error handling
                mean_pmt_count = np.mean(self.PMTFlow.get_next_counts('ON',int(self.numAvg))) 
            else:           
                mean_pmt_count = 0.0

            # Save freq (kHz) vs counts
            self.dv.add(freq[i]*1e-3, mean_pmt_count, context = self.c_pmt)

        self.agilent.output(False)

    def set_up_datavault(self):
        # set up folder
        date = datetime.datetime.now()
        year  = `date.year`
        month = '%02d' % date.month  # Padded with a zero if one digit
        day   = '%02d' % date.day    # Padded with a zero if one digit
        trunk = year + '_' + month + '_' + day

        # Open new data sets for prob and saving histogram data
        self.dv.cd(['',year,month,trunk],True, context = self.c_pmt)
        dataset = self.dv.new('Tickle_Sweep',[('freq', 'kHz')],[('Counts', 'Counts', 'num')], context = self.c_pmt)
        # add dv params
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context = self.c_pmt)


        # Set live plotting
        self.grapher.plot(dataset, 'tickle_sweep', False)


    def finalize(self, cxn, context):
        self.cxnwlm.disconnect()


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = tickle_sweep(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
