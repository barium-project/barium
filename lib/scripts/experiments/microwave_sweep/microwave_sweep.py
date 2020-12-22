import labrad
from twisted.internet.defer import inlineCallbacks, returnValue

from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
from barium.lib.scripts.pulse_sequences.MicrowaveSweep133 import microwave_sweep as main_sequence

from config.FrequencyControl_config import FrequencyControl_config
from config.multiplexerclient_config import multiplexer_config

import time
from labrad.units import WithUnit
import numpy as np
import datetime as datetime


class microwave_sweep(experiment):

    name = 'Microwave Sweep'

    exp_parameters = [
                      ('MicrowaveSweep133', 'Sequences_Per_Point'),
                      ('MicrowaveSweep133', 'Start_Frequency'),
                      ('MicrowaveSweep133', 'Stop_Frequency'),
                      ('MicrowaveSweep133', 'Frequency_Step'),
                      ('MicrowaveSweep133', 'dc_threshold'),
                      ]

    # Add the parameters from the required subsequences
    exp_parameters.extend(main_sequence.all_required_parameters())

    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters


    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.cxn = labrad.connect(name = 'Microwave Sweep')
        self.cxnwlm = labrad.connect(multiplexer_config.ip, name = 'Microwave Sweep', password = 'lab')


        self.wm = self.cxnwlm.multiplexerserver
        self.pulser = self.cxn.pulser
        self.grapher = self.cxn.real_simple_grapher
        self.dv = self.cxn.data_vault
        self.HPA = self.cxn.hp8672a_server
        self.pv = self.cxn.parametervault
        self.shutter = self.cxn.arduinottl
        self.pb = self.cxn.protectionbeamserver

        # Define variables to be used
        self.p = self.parameters
        self.cycles = self.p.MicrowaveSweep133.Sequences_Per_Point
        self.start_frequency = self.p.MicrowaveSweep133.Start_Frequency
        self.stop_frequency = self.p.MicrowaveSweep133.Stop_Frequency
        self.step_frequency = self.p.MicrowaveSweep133.Frequency_Step
        self.state_detection = self.p.MicrowaveSweep133.State_Detection
        self.dc_thresh = self.p.MicrowaveSweep133.dc_threshold
        self.disc = self.pv.get_parameter('StateReadout','state_readout_threshold')
        self.m_sequence = self.p.MicrowaveSweep133.microwave_pulse_sequence
        if self.m_sequence == 'single':
            self.LO_freq = self.p.Microwaves133.LO_frequency
        elif self.m_sequence == 'composite_1':
            self.LO_freq = self.p.Composite1.LO_frequency

        # Get contexts for saving the data sets
        self.c_prob = self.cxn.context()
        self.c_hist = self.cxn.context()
        self.c_dc_hist = self.cxn.context()

        # Need to map the gpib address to the labrad conection
        self.device_mapA = {}
        self.device_mapB = {}
        self.get_device_map()
        self.HPA.select_device(self.device_mapA['GPIB0::19'])

        self.set_up_datavault()

    def run(self, cxn, context):

        freq = np.linspace(self.start_frequency['MHz'],self.stop_frequency['MHz'],\
                    int((abs(self.stop_frequency['MHz']-self.start_frequency['MHz'])/self.step_frequency['MHz']) +1))

        self.set_hp_frequency()
        time.sleep(.3) # time to switch frequencies

        if self.state_detection == 'shelving':
            self.pulser.switch_auto('TTL8',False)

        for i in range(len(freq)):
            if self.pause_or_stop():
                # Turn on LED if aborting experiment
                self.pulser.stop_sequence()
                self.pulser.switch_manual('TTL8',True)
                return
            # for the protection beam we start a while loop and break it if we got the data,
            # continue if we didn't
            # Set the microwave frequency
            if self.m_sequence == 'single':
                self.p.Microwaves133.frequency_microwaves = WithUnit(freq[i],'MHz')
            elif self.m_sequence == 'composite_1':
                self.p.Composite1.frequency_microwaves = WithUnit(freq[i],'MHz')
            self.program_pulse_sequence()

            # for the protection beam we start a while loop and break it if we got the data,
            # continue if we didn't
            while True:
                if self.pause_or_stop():
                    # Turn on LED if aborting experiment
                    self.pulser.stop_sequence()
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
                        self.pulser.switch_manual('TTL8',True)
                        return

                # Here we look to see if the doppler cooling counts were low,
                # and throw out experiments that were below threshold
                pmt_counts = self.pulser.get_readout_counts()
                dc_counts = pmt_counts[::2]
                sd_counts = pmt_counts[1::2]
                ind = np.where(dc_counts < self.dc_thresh)
                counts = np.delete(sd_counts,ind[0])
                print len(counts)


                self.disc = self.pv.get_parameter('StateReadout','state_readout_threshold')
                # 1 state is bright for standard state detection
                if self.state_detection == 'spin-1/2':
                    bright = np.where(counts >= self.disc)
                    fid = float(len(bright[0]))/len(counts)
                # 1 state is dark for shelving state detection
                elif self.state_detection == 'shelving':
                    dark = np.where(counts <= self.disc)
                    fid = float(len(dark[0]))/len(counts)

                # Save freq vs prob
                self.dv.add(freq[i] , fid, context = self.c_prob)
                # We want to save all the experimental data, include dc as sd counts
                exp_list = np.arange(self.cycles)
                print len(exp_list)
                data = np.column_stack((exp_list, dc_counts, sd_counts))
                self.dv.add(data, context = self.c_dc_hist)

                # Now the hist with the ones we threw away
                exp_list = np.delete(exp_list,ind[0])
                data = np.column_stack((exp_list,counts))
                self.dv.add(data, context = self.c_hist)


                # Adding the character c and the number of cycles so plotting the histogram
                # only plots the most recent point.
                self.dv.add_parameter('hist'+str(i) + 'c' + str(int(self.cycles)), True, context = self.c_hist)
                break
        # Close shutter and turn LED on after experiment
        self.pulser.switch_manual('TTL8',True)

    def set_up_datavault(self):
        # set up folder
        date = datetime.datetime.now()
        year  = `date.year`
        month = '%02d' % date.month  # Padded with a zero if one digit
        day   = '%02d' % date.day    # Padded with a zero if one digit
        trunk = year + '_' + month + '_' + day

        # Open new data sets for prob and saving histogram data
        self.dv.cd(['',year,month,trunk],True, context = self.c_prob)
        dataset = self.dv.new('MicrowaveSweep_prob',[('freq', 'MHz')], [('Probability', 'Probability', 'num')], context = self.c_prob)
        # add dv params
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context = self.c_prob)

        self.dv.cd(['',year,month,trunk],True, context = self.c_hist)
        dataset1 = self.dv.new('MicrowaveSweep_hist',[('freq', 'MHz')], [('Counts', 'Counts', 'num')], context = self.c_hist)
        # add dv params
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context = self.c_hist)
        self.dv.add_parameter('Readout Threshold', self.disc, context = self.c_hist)

        #Hist with dc counts and sd counts
        self.dv.cd(['',year,month,trunk],True, context = self.c_dc_hist)
        dataset2 = self.dv.new('MicrowaveSweep_dc_hist',[('run', 'arb u')],\
                               [('Counts', 'DC_Hist', 'num'), ('Counts', 'SD_Hist', 'num')], context = self.c_dc_hist)

        # Set live plotting
        self.grapher.plot(dataset, 'qubit_freq_sweep', False)


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

    def program_pulse_sequence(self):
        pulse_sequence = main_sequence(self.p)
        pulse_sequence.programSequence(self.pulser)

    def set_hp_frequency(self):
        self.HPA.set_frequency(WithUnit(int(self.LO_freq['MHz']),'MHz'))
        dds_freq = WithUnit(30.- self.LO_freq['MHz']/2 + 10*int(self.LO_freq['MHz']/20),'MHz')
        self.pulser.frequency('LF DDS',dds_freq)

    def finalize(self, cxn, context):
        self.cxn.disconnect()
        self.cxnwlm.disconnect()

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = microwave_sweep(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)




