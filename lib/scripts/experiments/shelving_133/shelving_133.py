import labrad
from twisted.internet.defer import inlineCallbacks, returnValue

from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
from barium.lib.scripts.pulse_sequences.Shelving133 import shelving133 as main_sequence

from config.FrequencyControl_config import FrequencyControl_config
from config.multiplexerclient_config import multiplexer_config

import time
from labrad.units import WithUnit
import numpy as np
import datetime as datetime


class shelving_133(experiment):

    name = 'shelving_133'

    exp_parameters = []

    # Add the parameters from the required subsequences
    exp_parameters.extend(main_sequence.all_required_parameters())

    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters


    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.cxn = labrad.connect(name = 'Shelving_133')
        self.cxnwlm = labrad.connect('wavemeter', name = 'shelving 133', password = 'lab')
        self.wm = self.cxnwlm.multiplexerserver
        self.pulser = self.cxn.pulser
        self.dv = self.cxn.data_vault
        self.grapher = self.cxn.grapher
        self.HPA = self.cxn.hp8672a_server
        self.HPB = self.cxn.hp8657b_server
        self.single_lock = self.cxn.software_laser_lock_server
        self.pv = self.cxn.parametervault
        self.shutter = self.cxn.arduinottl
        self.pb = self.cxn.protectionbeamserver
        self.reg = self.cxn.registry

        # Define variables to be used
        self.p = self.parameters
        self.cycles = self.p.Shelving133.cycles
        self.start_time = self.p.Shelving133.Start_Time
        self.stop_time = self.p.Shelving133.Stop_Time
        self.step_time = self.p.Shelving133.Time_Step
        self.start_freq = self.parameters.Shelving133.Frequency_Start
        self.stop_freq = self.parameters.Shelving133.Frequency_Stop
        self.step_freq = self.parameters.Shelving133.Frequency_Step
        self.scan = self.parameters.Shelving133.Scan
        self.scan_laser = self.parameters.Shelving133.Scan_Laser

        # Get software laser lock info
        self.reg.cd(['Servers','software_laser_lock'])
        laser = self.reg.get(self.scan_laser)
        # Returns tuple which is not iterable
        laser = list(laser)
        self.scan_laser_chan = laser[1]

        # Get context for saving probability and histograms
        self.c_prob = self.cxn.context()
        self.c_hist = self.cxn.context()
        self.c_deshelve = self.cxn.context()

        # Need to map the gpib address to the labrad connection
        self.device_mapA = {}
        self.device_mapB = {}
        self.get_device_map()
        # Setup data saving
        self.set_up_datavault()


    def run(self, cxn, context):
        '''
        There is a limit to how long readout counts will run (count). Instead of producing an
        error it will just stop the pulse sequence and return the stored array.
        Leaving the print statement with length of counts to ensure the correct
        number of experiments is run.
        '''

        if self.scan == 'time':
            t = np.linspace(self.start_time['us'],self.stop_time['us'],\
                    int((abs(self.stop_time['us']-self.start_time['us'])/self.step_time['us']) +1))
            # Open shelving laser shutting and turn LED off
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

                    self.disc = self.pv.get_parameter('StateReadout','state_readout_threshold')
                    self.p.Shelving133.shelving_duration = WithUnit(t[i], 'us')
                    self.run_pulse_sequence()

                    # First check if the protection was enabled, do nothing if not
                    if not self.pb.get_protection_state():
                        pass
                    # if it was enabled, try to fix, continue if successful
                    # otherwise call return to break out of function
                    else:
                        # Should turn on deshelving LED while trying
                        self.pulser.switch_manual('TTL7',True)
                        if self.remove_protection_beam():
                            # If successful switch off LED and return to top of loop
                            self.pulser.switch_auto('TTL7',False)
                            continue
                        else:
                            # Failed, abort experiment
                            return

                    sd_counts = self.pulser.get_readout_counts()
                    # Dark state is the |1> state (mf = 1), plot that prob
                    dark = np.where(sd_counts <= self.disc)
                    fid = float(len(dark[0]))/len(sd_counts)
                    self.dv.add(t[i] , fid, context = self.c_prob)
                    # Save histogram
                    data = np.column_stack((np.arange(self.cycles),sd_counts))
                    self.dv.add(data, context = self.c_hist)
                    # Adding the character c and the number of cycles so plotting the histogram
                    # only plots the most recent point.
                    self.dv.add_parameter('hist'+str(i) + 'c' + str(int(self.cycles)), True, context = self.c_hist)
                    break
            self.pulser.switch_manual('TTL7',True)
            self.shutter.ttl_output(10, False)

        if self.scan == 'frequency':

            freq = np.linspace(self.start_freq['THz'],self.stop_freq['THz'],\
                    int((abs(self.stop_freq['THz']-self.start_freq['THz'])/self.step_freq['THz']) +1))

            for i in range(len(freq)):
                if self.pause_or_stop():
                    # Turn on LED if aborting experiment
                    self.pulser.switch_manual('TTL7',True)
                    return
                # for the protection beam we start a while loop and break it if we got the data,
                # continue if we didn't
                self.single_lock.set_lock_frequency(freq[i], self.scan_laser)
                time.sleep(5)
                self.shutter.ttl_output(10, True)
                time.sleep(.5)
                self.pulser.switch_auto('TTL7',False)
                # for the protection beam we start a while loop and break it if we got the data,
                # continue if we didn't
                while True:
                    frequency = self.wm.get_frequency(self.scan_laser_chan)
                    self.disc = self.pv.get_parameter('StateReadout','state_readout_threshold')
                    self.run_pulse_sequence()
                    # First check if the protection was enabled, do nothing if not
                    if not self.pb.get_protection_state():
                        pass
                    # if it was enabled, try to fix, continue if successful
                    # otherwise call return to break out of function
                    else:
                        # Should turn on deshelving LED while trying
                        self.pulser.switch_manual('TTL7',True)
                        if self.remove_protection_beam():
                            # If successful switch off LED and return to top of loop
                            self.pulser.switch_auto('TTL7',False)
                            continue
                        else:
                            # Failed, abort experiment
                            return
                    sd_counts = self.pulser.get_readout_counts()
                    dark = np.where(sd_counts <= self.disc)
                    fid = float(len(dark[0]))/len(sd_counts)
                    self.dv.add(freq[i] , fid, context = self.c_prob)
                    # Save histogram
                    data = np.column_stack((np.arange(self.cycles),sd_counts))
                    self.dv.add(data, context = self.c_hist)
                    # Adding the character c and the number of cycles so plotting the histogram
                    # only plots the most recent point.
                    self.dv.add_parameter('hist'+str(i) + 'c' + str(int(self.cycles)), True, context = self.c_hist)
                    break
                # since switching frequencies is slow, close shutter and turn LED on while waiting
                self.pulser.switch_manual('TTL7',True)
                self.shutter.ttl_output(10, False)
            # experiment is over so turn the led back on and close the shutter
            self.pulser.switch_manual('TTL7',True)
            self.shutter.ttl_output(10, False)


    def get_device_map(self):
        gpib_listA = FrequencyControl_config.gpibA
        gpib_listB = FrequencyControl_config.gpibB

        devices = self.HPA.list_devices()
        for i in range(len(gpib_listA)):
            for j in range(len(devices)):
                if devices[j][1].find(gpib_listA[i]) > 0:
                    self.device_mapA[gpib_listA[i]] = devices[j][0]
                    break

        devices = self.HPB.list_devices()
        for i in range(len(gpib_listB)):
            for j in range(len(devices)):
                if devices[j][1].find(gpib_listB[i]) > 0:
                    self.device_mapB[gpib_listB[i]] = devices[j][0]
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

    def set_up_datavault(self):
        # set up folder
        date = datetime.datetime.now()
        year  = `date.year`
        month = '%02d' % date.month  # Padded with a zero if one digit
        day   = '%02d' % date.day    # Padded with a zero if one digit
        trunk = year + '_' + month + '_' + day
        self.dv.cd(['',year,month,trunk],True, context = self.c_prob)
        dataset = self.dv.new('shelving133_prob',[('time', 'us')], [('Probability', 'Probability', 'num')], context = self.c_prob)
        # add dv params
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context = self.c_prob)

        self.dv.cd(['',year,month,trunk],True, context = self.c_hist)
        dataset1 = self.dv.new('shelving_hist',[('time', 'us')], [('Probability', 'Probability', 'num')], context = self.c_hist)
        # add dv params
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context = self.c_hist)
        self.dv.add_parameter('Readout Threshold', self.disc, context = self.c_hist)

        # Set live plotting
        self.grapher.plot(dataset, 'shelving', False)


    def finalize(self, cxn, context):
        self.cxn.disconnect()


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = shelving_133(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)




