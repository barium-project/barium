import labrad
from twisted.internet.defer import inlineCallbacks, returnValue

from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
from barium.lib.scripts.pulse_sequences.OpticalPumping133 import optical_pumping_133 as main_sequence

from config.FrequencyControl_config import FrequencyControl_config
from config.multiplexerclient_config import multiplexer_config

import time
from labrad.units import WithUnit
import numpy as np
import datetime as datetime


class optical_pumping(experiment):

    name = 'Optical Pumping'

    exp_parameters = [
                      ('OpticalPumping133', 'Cycles'),
                      ('OpticalPumping133', 'Start_Time'),
                      ('OpticalPumping133', 'Stop_Time'),
                      ('OpticalPumping133', 'Time_Step'),
                      ('OpticalPumping133', 'Mode'),
                      ]

    # Add the parameters from the required subsequences
    exp_parameters.extend(main_sequence.all_required_parameters())

    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters


    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.cxn = labrad.connect(name = 'Optical Pumping')

        self.pulser = self.cxn.pulser
        self.grapher = self.cxn.real_simple_grapher
        self.dv = self.cxn.data_vault
        self.pb = self.cxn.protectionbeamserver
        self.shutter = self.cxn.arduinottl
        self.pv = self.cxn.parametervault
        # Define variables to be used
        self.p = self.parameters
        self.cycles = self.p.OpticalPumping133.Cycles
        self.start_time = self.p.OpticalPumping133.Start_Time
        self.stop_time = self.p.OpticalPumping133.Stop_Time
        self.step_time = self.p.OpticalPumping133.Time_Step
        self.state_detection = self.p.OpticalPumping133.State_Detection
        self.mode = self.p.OpticalPumping133.Mode

        self.disc = self.pv.get_parameter('StateReadout','state_readout_threshold')
        # Define contexts for saving data sets
        self.c_prob = self.cxn.context()
        self.c_hist = self.cxn.context()

        self.set_up_datavault()

    def run(self, cxn, context):

        t = np.linspace(self.start_time['us'],self.stop_time['us'],\
                    int((abs(self.stop_time['us']-self.start_time['us'])/self.step_time['us']) +1))

        if self.state_detection == 'shelving':
            self.pulser.switch_auto('TTL8',False)

        for i in range(len(t)):
            if self.pause_or_stop():
                # Turn on LED if aborting experiment
                self.pulser.switch_manual('TTL8',True)
                return

            # set the optical pumping duration. If optimizing leave it as set
            if self.mode == 'Normal':
                self.p.StatePreparation133.state_prep_duration = WithUnit(t[i],'us')
            self.program_pulse_sequence()
            # for the protection beam we start a while loop and break it if we got the data,
            # continue if we didn't
            while True:
                if self.pause_or_stop():
                    # Turn on LED if aborting experiment
                    self.pulser.switch_manual('TTL8',True)
                    return

                self.pulser.reset_readout_counts()
                self.pulser.start_number(int(self.cycles))
                self.pulser.wait_sequence_done()
                self.pulser.stop_sequence()
                # First check if the protection was enabled, do nothing if not
                if not self.pb.get_protection_state():
                        pass
                # if it was enabled, try to fix, continue if successful
                # otherwise call return to break out of function
                else:
                    # Should turn on deshelving LED while trying
                    self.pulser.switch_manual('TTL8',True)
                    if self.remove_protection_beam():
                        # If successful switch off LED and return to top of loop
                        self.pulser.switch_auto('TTL8',False)
                        continue
                    else:
                        # Failed, abort experiment
                        return


                pmt_counts = self.pulser.get_readout_counts()
                dc_counts = pmt_counts[::2]
                counts = pmt_counts[1::2]
                print len(dc_counts), len(counts)

                self.disc = self.pv.get_parameter('StateReadout','state_readout_threshold')
                # 1 state is bright for standard state detection
                if self.state_detection == 'spin-1/2':
                    bright = np.where(counts >= self.disc)
                    fid = float(len(bright[0]))/len(counts)
                # 1 state is dark for shelving state detection
                elif self.state_detection == 'shelving':
                    dark = np.where(counts <= self.disc)
                    fid = float(len(dark[0]))/len(counts)

                # If we are optimizing save the data point and rerun the point in the while loop
                if self.mode == 'Optimize':
                    self.dv.add(i , fid, context = self.c_prob)
                    data = np.column_stack((np.arange(self.cycles),counts))
                    self.dv.add(data, context = self.c_hist)
                    self.dv.add_parameter('hist'+str(i) + 'c' + str(int(self.cycles)), \
                                      True, context = self.c_hist)
                    i = i + 1
                    continue
                # If normal save time and prob and move on
                self.dv.add(t[i] , fid, context = self.c_prob)
                data = np.column_stack((np.arange(self.cycles),counts))
                self.dv.add(data, context = self.c_hist)
                # Adding the character c and the number of cycles so plotting the histogram
                # only plots the most recent point.
                self.dv.add_parameter('hist'+str(i) + 'c' + str(int(self.cycles)), \
                                      True, context = self.c_hist)

                break
        self.pulser.switch_manual('TTL8',True)

    def set_up_datavault(self):
        # set up folder
        date = datetime.datetime.now()
        year  = `date.year`
        month = '%02d' % date.month  # Padded with a zero if one digit
        day   = '%02d' % date.day    # Padded with a zero if one digit
        trunk = year + '_' + month + '_' + day

        # Define data sets for probability and the associated histograms
        self.dv.cd(['',year,month,trunk],True, context = self.c_prob)
        dataset = self.dv.new('Optical Pumping',[('run', 'arb u')], [('Probability', 'Probability', 'num')], context = self.c_prob)
        # add dv params
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context = self.c_prob)

        self.dv.cd(['',year,month,trunk],True, context = self.c_hist)
        dataset1 = self.dv.new('Optical Pumping_hist',[('run', 'arb u')], [('Counts', 'Counts', 'num')], context = self.c_hist)
        # add dv params
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context = self.c_hist)
        self.dv.add_parameter('Readout Threshold', self.disc, context = self.c_hist)

        # Set live plotting
        self.grapher.plot(dataset, 'bright/dark', False)


    def set_wm_frequency(self, freq, chan):
        self.wm.set_pid_course(chan, freq)

    def program_pulse_sequence(self):
        pulse_sequence = main_sequence(self.p)
        pulse_sequence.programSequence(self.pulser)

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

    def finalize(self, cxn, context):
        self.cxn.disconnect()

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = optical_pumping(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)




