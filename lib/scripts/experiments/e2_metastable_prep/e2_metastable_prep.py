import labrad
from twisted.internet.defer import inlineCallbacks, returnValue

from common.lib.servers.script_scanner.scan_methods import experiment
from barium.lib.scripts.pulse_sequences.E2MetastablePrep import e2_metastable_prep as main_sequence

from config.FrequencyControl_config import FrequencyControl_config
from config.multiplexerclient_config import multiplexer_config

import time
from labrad.units import WithUnit
import numpy as np
import datetime as datetime
from random import *

class e2_metastable_prep(experiment):

    name = 'E2_Metastable_Prep'

    exp_parameters = [('E2MetastablePrep','Sequences_Per_Point'),
                      ('E2MetastablePrep','Start_Time'),
                      ('E2MetastablePrep','Stop_Time'),
                      ('E2MetastablePrep','Time_Step'),
                      ('E2MetastablePrep','dc_threshold'),
                      ('E2MetastablePrep', 'HP_Amplitude'),
                      ('E2MetastablePrep', 'Mode'),
                      ]

    # Add the parameters from the required subsequences
    exp_parameters.extend(main_sequence.all_required_parameters())

    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.cxn = labrad.connect(name = 'E2 Metastable Prep')
        self.cxnwlm = labrad.connect(multiplexer_config.ip, name = 'E2 Metastable Prep', password = 'lab')

        self.wm = self.cxnwlm.multiplexerserver
        self.bristol = self.cxnwlm.bristolserver
        self.pulser = self.cxn.pulser
        self.grapher = self.cxn.real_simple_grapher
        self.dv = self.cxn.data_vault
        self.HPA = self.cxn.hp8672a_server
        self.HPB = self.cxn.hp8657b_server
        self.HP3 = self.cxn.hp8673server
        self.pv = self.cxn.parametervault
        self.shutter = self.cxn.arduinottl
        self.pb = self.cxn.protectionbeamserver

        # Define variables to be used
        self.p = self.parameters
        self.cycles = self.p.E2MetastablePrep.Sequences_Per_Point
        self.start_frequency = self.p.E2MetastablePrep.Start_Time
        self.stop_frequency = self.p.E2MetastablePrep.Stop_Time
        self.step_frequency = self.p.E2MetastablePrep.Time_Step
        self.state_detection = self.p.E2MetastablePrep.State_Detection
        self.dc_thresh = self.p.E2MetastablePrep.dc_threshold
        self.hp_amp = self.p.E2MetastablePrep.HP_Amplitude
        self.disc = self.pv.get_parameter('StateReadout','state_readout_threshold')
        self.disc_shelve = self.pv.get_parameter('StateReadout','state_readout_threshold_shelve')
        self.m_sequence = self.p.E2MetastablePrep.e2metastableprep_pulse_sequence
        self.mode = self.p.E2MetastablePrep.Mode
            
        self.total_exps = 0

    # Define contexts for saving data sets
        self.c_prob = self.cxn.context()
        self.c_hist = self.cxn.context()
        self.c_time_tags = self.cxn.context()

        # Need to map the gpib address to the labrad conection
        self.device_mapA = {}
        self.device_mapB = {}
        self.device_mapC = {}
        self.get_device_map()
        self.HPA.select_device(self.device_mapA['GPIB0::19'])
        self.HP3.select_device(self.device_mapC['GPIB0::1'])

        self.set_up_datavault()


    def run(self, cxn, context):

        t = np.linspace(self.start_time['us'],self.stop_time['us'],\
                    int((abs(self.stop_time['us']-self.start_time['us'])/self.step_time['us']) +1))

        self.set_hp_frequency()
        time.sleep(.3) # time to switch
        if self.state_detection == 'shelving':
            self.pulser.switch_auto('TTL8',False)

        for i in range(len(t)):
            if self.pause_or_stop():
                # Turn on LED if aborting experiment
                self.pulser.switch_manual('TTL8',True)
                return


            # for the protection beam we start a while loop and break it if we got the data,
            # continue if we didn't
            while True:
                if self.pause_or_stop():
                    # Turn on LED if aborting experiment
                    self.pulser.switch_manual('TTL8',True)
                    return

                self.program_pulse_sequence()
                self.pulser.reset_readout_counts()
                self.pulser.reset_timetags()
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
                        #self.shutter.ttl_output(10, False)
                        return

                # Here we look to see if the doppler cooling counts were low,
                # and throw out experiments that were below threshold
                pmt_counts = self.pulser.get_readout_counts()
                # We also want to grab the time tags in case we're correcting for D5/2 decay
                time_tags = self.pulser.get_timetags()
                dc_counts = pmt_counts[::3]
                shelve_sd_counts = pmt_counts[1::3]
                sd_counts = pmt_counts[2::3]
                
                ind = np.where(dc_counts < self.dc_thresh)
                counts = np.delete(sd_counts,ind[0])
                shelve_counts = np.delete(shelve_sd_counts,ind[0])
                self.total_exps = self.total_exps + len(counts)
                print len(dc_counts), len(counts), self.total_exps

                self.disc = self.pv.get_parameter('StateReadout','state_readout_threshold')
                self.disc_shelve = self.pv.get_parameter('StateReadout','shelving_state_readout_threshold')
                # 1 state is bright for standard state detection
                bright = np.where(counts >= self.disc)
                fid = float(len(bright[0]))/len(counts)
                # 1 state is dark for shelving state detection
                dark = np.where(shelve_counts <= self.disc_shelve)
                fid = float(len(dark[0]))/len(shelve_counts)



                # We want to save all the experimental data, include dc as sd counts
                exp_list = np.arange(self.cycles)
                data = np.column_stack((exp_list, dc_counts, shelve_sd_counts, sd_counts))
                self.dv.add(data, context = self.c_hist)

                # Now the time tags
                self.dv.add(np.column_stack((np.zeros(len(time_tags)),time_tags)), context = self.c_time_tags)
                # Adding the character c and the number of cycles so plotting the histogram
                # only plots the most recent point.
                self.dv.add_parameter('hist'+str(i) + 'c' + str(int(self.cycles)), \
                                      True, context = self.c_hist)
                if self.pause_or_stop():
                    # Turn on LED if aborting experiment
                    self.pulser.switch_manual('TTL8',True)
                    return
                # If we are in repeat save the data point and rerun the point in the while loop
                if self.mode == 'Repeat':
                    self.dv.add(i , fid, context = self.c_prob)
                    i = i + 1
                    continue

                # Not in repeat save time vs prob
                self.dv.add(t[i] , fid, context = self.c_prob)

                break
        self.pulser.switch_manual('TTL8',True)









        
