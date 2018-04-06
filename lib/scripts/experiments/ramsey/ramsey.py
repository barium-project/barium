import labrad
from twisted.internet.defer import inlineCallbacks, returnValue

from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
from barium.lib.scripts.pulse_sequences.Ramsey133 import ramsey as main_sequence

from config.FrequencyControl_config import FrequencyControl_config
from config.multiplexerclient_config import multiplexer_config

import time
from labrad.units import WithUnit
import numpy as np
import datetime as datetime


class ramsey(experiment):

    name = 'Ramsey'

    exp_parameters = []

    # Add the parameters from the required subsequences
    exp_parameters.extend(main_sequence.all_required_parameters())

    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters


    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.cxn = labrad.connect(name = 'Ramsey')
        self.cxnwlm = labrad.connect(multiplexer_config.ip, name = 'Ramsey', password = 'lab')


        self.wm = self.cxnwlm.multiplexerserver
        self.pulser = self.cxn.pulser
        self.grapher = self.cxn.grapher
        self.dv = self.cxn.data_vault
        self.HPA = self.cxn.hp8672a_server
        self.pv = self.cxn.parametervault
        self.shutter = self.cxn.arduinottl
        self.pb = self.cxn.protectionbeamserver


        # Define variables to be used
        self.p = self.parameters
        self.cycles = self.p.Ramsey133.Sequences_Per_Point
        self.start_time = self.p.Ramsey133.Start_Time
        self.stop_time = self.p.Ramsey133.Stop_Time
        self.step_time = self.p.Ramsey133.Time_Step
        self.freq = self.p.Ramsey133.microwave_frequency
        self.disc = self.pv.get_parameter('StateReadout','state_readout_threshold')
        self.state_detection = self.p.Ramsey133.State_Detection

        # Define contexts for saving different data sets
        self.c_prob = self.cxn.context()
        self.c_hist = self.cxn.context()
        # Need to map the gpib address to the labrad conection
        self.device_mapA = {}
        self.device_mapB = {}
        self.get_device_map()
        self.HPA.select_device(self.device_mapA['GPIB0::19'])

        self.set_up_datavault()

    def run(self, cxn, context):

        t = np.linspace(self.start_time['us'],self.stop_time['us'],\
                    int((abs(self.stop_time['us']-self.start_time['us'])/self.step_time['us']) +1))

        self.HPA.set_frequency(self.freq)
        time.sleep(.3) # time to switch frequencies

        if self.state_detection == 'shelving':
            self.shutter.ttl_output(10, True)
            time.sleep(.5)
            self.pulser.switch_auto('TTL7',False)

        for i in range(len(t)):
            if self.pause_or_stop():
                # Turn on LED if aborting experiment
                self.pulser.switch_manual('TTL7',True)
                return
            # for the protection beam we start a while loop and break it if we got the data,
            # continue if we didn't
            while True:
                if self.pause_or_stop():
                    # Turn on LED if aborting experiment
                    self.pulser.switch_manual('TTL7',True)
                    return

                # set ramsey delay
                self.p.Ramsey133.Ramsey_Delay = WithUnit(t[i],'us')
                self.disc = self.pv.get_parameter('StateReadout','state_readout_threshold')
                self.run_pulse_sequence()

                counts = self.pulser.get_readout_counts()
                # 1 state is bright for standard state detection
                if self.state_detection == 'spin-1/2':
                    bright = np.where(counts >= self.disc)
                    fid = float(len(bright[0]))/len(counts)
                # 1 state is dark for shelving state detection
                elif self.state_detection == 'shelving':
                    dark = np.where(counts <= self.disc)
                    fid = float(len(dark[0]))/len(counts)

                self.dv.add(t[i] , fid, context = self.c_prob)
                data = np.column_stack((np.arange(self.cycles),counts))
                self.dv.add(data, context = self.c_hist)
                # Adding the character c and the number of cycles so plotting the histogram
                # only plots the most recent point.
                self.dv.add_parameter('hist'+str(i) + 'c' + str(int(self.cycles)), \
                                      True, context = self.c_hist)
                break
        self.pulser.switch_manual('TTL7',True)
        self.shutter.ttl_output(10, False)

    def set_up_datavault(self):
        # set up folder
        date = datetime.datetime.now()
        year  = `date.year`
        month = '%02d' % date.month  # Padded with a zero if one digit
        day   = '%02d' % date.day    # Padded with a zero if one digit
        trunk = year + '_' + month + '_' + day

        # open data sets for probability and histograms
        self.dv.cd(['',year,month,trunk],True, context = self.c_prob)
        dataset = self.dv.new('Ramsey_prob',[('run', 'arb u')], [('Counts', 'Counts', 'num')], context = self.c_prob)
        # add dv params
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context = self.c_prob)

        self.dv.cd(['',year,month,trunk],True, context = self.c_hist)
        dataset1 = self.dv.new('Ramsey_hist',[('run', 'arb u')], [('Counts', 'Counts', 'num')], context = self.c_hist)
        # add dv params
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context = self.c_hist)

        # Set live plotting
        self.grapher.plot(dataset, 'rabi_flopping', False)


    def set_wm_frequency(self, freq, chan):
        self.wm.set_pid_course(chan, freq)

    def get_device_map(self):
        gpib_listA = FrequencyControl_config.gpibA
        gpib_listB = FrequencyControl_config.gpibB

        devices = self.HPA.list_devices()
        for i in range(len(gpib_listA)):
            for j in range(len(devices)):
                if devices[j][1].find(gpib_listA[i]) > 0:
                    self.device_mapA[gpib_listA[i]] = devices[j][0]
                    break

    def remove_protection_beam(self):
        for i in range(5):
            self.pb.protection_off()
            time.sleep(.3)
            print "trying to remove " + str(i)
            print self.pb.get_protection_state()
            if not self.pb.get_protection_state():
                return True
        print 'failed to remove protection beam'
        return False

    def run_pulse_sequence(self):
        pulse_sequence = main_sequence(self.p)
        pulse_sequence.programSequence(self.pulser)
        self.pulser.reset_readout_counts()
        self.pulser.start_number(int(self.cycles))
        self.pulser.wait_sequence_done()
        self.pulser.stop_sequence()

    def finalize(self, cxn, context):
        self.cxn.disconnect()
        self.cxnwlm.disconnect()

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = ramsey(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)




