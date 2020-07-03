import labrad
from twisted.internet.defer import inlineCallbacks, returnValue

from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
from barium.lib.scripts.pulse_sequences.RabiFlopping import rabi_flopping as main_sequence
from MaximumLikelihood import MaximumLikelihood

from config.FrequencyControl_config import FrequencyControl_config
from config.multiplexerclient_config import multiplexer_config

import time
from labrad.units import WithUnit
import numpy as np
import datetime as datetime


class high_fidelity(experiment):

    name = 'High Fidelity'

    exp_parameters = [('HighFidelity','Sequences_Per_Point'),
                      ('HighFidelity','dc_threshold'),
                      ('HighFidelity','MaximumLikelihood'),
                      ('HighFidelity','Mean_Bright'),
                      ('HighFidelity','Mean_Dark'),
                      ]

    # Add the parameters from the required subsequences
    exp_parameters.extend(main_sequence.all_required_parameters())

    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters


    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.cxn = labrad.connect(name = 'High Fidelity')
        self.cxnwlm = labrad.connect(multiplexer_config.ip, name = 'High Fidelity', password = 'lab')


        self.wm = self.cxnwlm.multiplexerserver
        self.pulser = self.cxn.pulser
        self.grapher = self.cxn.real_simple_grapher
        self.dv = self.cxn.data_vault
        self.HPA = self.cxn.hp8672a_server
        self.HPB = self.cxn.hp8657b_server
        self.pv = self.cxn.parametervault
        self.shutter = self.cxn.arduinottl
        self.pb = self.cxn.protectionbeamserver

        # Define variables to be used
        self.p = self.parameters
        self.cycles = self.p.HighFidelity.Sequences_Per_Point
        self.dc_thresh = self.p.HighFidelity.dc_threshold
        self.correct_ML = self.p.HighFidelity.MaximumLikelihood
        self.disc = self.pv.get_parameter('StateReadout','state_readout_threshold')
        self.state_detection = self.p.RabiFlopping.State_Detection
        self.m_sequence = self.p.RabiFlopping.microwave_pulse_sequence
        self.shelve_time = self.p.Shelving133_Sub.shelving_duration

        if self.m_sequence == 'single':
            self.LO_freq = self.p.Microwaves133.LO_frequency
            self.pi_time = self.p.Microwaves133.microwave_duration
            self.microwave_power = self.p.Microwaves133.amplitude_microwaves
        elif self.m_sequence == 'composite_1':
            self.LO_freq = self.p.Composite1.LO_frequency
            self.pi_time = self.p.Composite1.microwave_duration
            self.microwave_power = self.p.Composite1.amplitude_microwaves

        elif self.m_sequence == 'composite_2':
            self.LO_freq = self.p.Composite2.LO_frequency
            self.pi_time = self.p.Composite2.microwave_duration
            self.microwave_power = self.p.Composite2.amplitude_microwaves


        self.total_exps = 0
        #print self.disc
        # Define contexts for saving data sets
        self.c_prob = self.cxn.context()
        self.c_hist_bright = self.cxn.context()
        self.c_hist_dark = self.cxn.context()
        self.c_time_tags_bright = self.cxn.context()
        self.c_time_tags_dark = self.cxn.context()
        self.c_ML_prob = self.cxn.context()
        self.c_ML_hist_dark = self.cxn.context()
        self.c_ML_hist_bright = self.cxn.context()

        # Need to map the gpib address to the labrad conection
        self.device_mapA = {}
        self.device_mapB = {}
        self.get_device_map()
        self.HPA.select_device(self.device_mapA['GPIB0::19'])

        if self.correct_ML == 'True':
            self.ML = MaximumLikelihood()
            self.ML.detection_time = self.p.ShelvingStateDetection.state_detection_duration['s']
            self.ML.mean_dark = self.p.HighFidelity.Mean_Dark
            self.ML.mean_bright = self.p.HighFidelity.Mean_Bright

        self.set_up_datavault()

    def run(self, cxn, context):


        self.set_hp_frequency()
        time.sleep(.3) # time to switch
        if self.state_detection == 'shelving':
            self.pulser.switch_auto('TTL8',False)
        i = 0
        while True:
            if self.pause_or_stop():
                # Turn on LED if aborting experiment
                self.pulser.switch_manual('TTL8',True)
                return

            # Dark State
            if i % 2 == 0:
                if self.m_sequence == 'composite_1':
                    self.p.Composite1.microwave_duration = self.pi_time
                    self.p.Composite1.amplitude_micrwaves = self.microwave_power

                elif self.m_sequence == 'composite_2':
                    self.p.Composite2.microwave_duration = self.pi_time
                    self.p.Composite2.amplitude_micrwaves = self.microwave_power

                elif self.m_sequence == 'single':
                    self.p.Microwaves133.microwave_duration = self.pi_time
                    self.p.Microwaves133.amplitude_micrwaves = self.microwave_power
                    self.p.Shelving133_Sub.shelving_duration = self.shelve_time

            # Bright State
            else:
                if self.m_sequence == 'composite_1':
                    self.p.Composite1.microwave_duration = WithUnit(0.0,'us')
                    self.p.Composite1.amplitude_micrwaves = WithUnit(-48.0,'dBm')

                elif self.m_sequence == 'composite_2':
                    self.p.Composite2.microwave_duration = WithUnit(0.0,'us')
                    self.p.Composite2.amplitude_micrwaves = WithUnit(-48.0,'dBm')

                elif self.m_sequence == 'single':
                    self.p.Microwaves133.microwave_duration = WithUnit(0.0,'us')
                    self.p.Microwaves133.amplitude_micrwaves = WithUnit(-48.0,'dBm')
                    #self.p.Shelving133_Sub.shelving_duration = WithUnit(0.0,'us')

            self.program_pulse_sequence()
            if self.correct_ML == 'True':
                self.set_sd_time_window()
            self.pulser.reset_readout_counts()
            self.pulser.reset_timetags()
            self.pulser.start_number(int(self.cycles))
            self.pulser.wait_sequence_done()
            self.pulser.stop_sequence()
            self.pulser.switch_manual('TTL8',True)
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
            # We also want to grab the time tags in case we're correcting for D5/2 decay
            time_tags = self.pulser.get_timetags()
            dc_counts = pmt_counts[::2]
            sd_counts = pmt_counts[1::2]
            self.ind = np.where(dc_counts < self.dc_thresh)
            counts = np.delete(sd_counts,self.ind[0])
            self.total_exps = self.total_exps + len(counts)
            print len(counts), self.total_exps

            if np.sum(sd_counts) > 32000.0:
                print "Too many time tags. Reduce experiment number"
                return
            self.disc = self.pv.get_parameter('StateReadout','state_readout_threshold')
            # 1 state is bright for standard state detection
            if self.state_detection == 'spin-1/2':
                bright = np.where(counts >= self.disc)
                fid = float(len(bright[0]))/len(counts)# 1 state is dark for shelving state detection
            elif self.state_detection == 'shelving':
                dark = np.where(counts <= self.disc)
                fid = float(len(dark[0]))/len(counts)


            # Save time vs prob
            self.dv.add(i , fid, context = self.c_prob)
            # We want to save all the experimental data, include dc as sd counts
            exp_list = np.arange(self.cycles)
            data = np.column_stack((exp_list, dc_counts, sd_counts))
            # Save bright or dark
            if i % 2 == 0:
                self.dv.add(data, context = self.c_hist_dark)
                self.dv.add(np.column_stack((np.zeros(len(time_tags)),time_tags)), context = self.c_time_tags_dark)
                self.dv.add_parameter('hist'+str(i) + 'c' + str(int(self.cycles)), \
                                    True, context = self.c_hist_dark)

                if self.correct_ML == 'True':
                    p_bright_arr = np.array([])
                    p_dark_arr = np.array([])
                    for j in range(len(sd_counts)):
                        tt = time_tags[:sd_counts[j]]
                        time_tags = np.delete(time_tags, np.arange(sd_counts[j]))
                        if dc_counts[j] > self.dc_thresh:
                            bins, counts = self.ML.bin_time_tags(tt)
                            p_dark_r = self.ML.prob_dark_recursive(counts)
                            p_bright = self.ML.prob_bright(counts)
                            p_bright_arr = np.append(p_bright_arr, p_bright)
                            p_dark_arr = np.append(p_dark_arr, p_dark_r)

                    ratio = p_bright_arr/p_dark_arr
                    dark_ml = np.where(ratio < 1.0)
                    fid_ml = float(len(dark_ml[0]))/len(p_dark_arr)
                    ml_data = np.column_stack((ratio, p_bright_arr, p_dark_arr))

                    self.dv.add(i, fid_ml, context = self.c_ML_prob)
                    self.dv.add(ml_data, context = self.c_ML_hist_dark)

            else:
                self.dv.add(data, context = self.c_hist_bright)
                self.dv.add(np.column_stack((np.zeros(len(time_tags)),time_tags)), context = self.c_time_tags_bright)
                self.dv.add_parameter('hist'+str(i) + 'c' + str(int(self.cycles)), \
                                    True, context = self.c_hist_bright)

                if self.correct_ML == 'True':
                    p_bright_arr = np.array([])
                    p_dark_arr = np.array([])
                    for j in range(len(sd_counts)):
                        tt = time_tags[:sd_counts[j]]
                        time_tags = np.delete(time_tags, np.arange(sd_counts[j]))
                        if dc_counts[j] > self.dc_thresh:
                            bins, counts = self.ML.bin_time_tags(tt)
                            p_dark_r = self.ML.prob_dark_recursive(counts)
                            p_bright = self.ML.prob_bright(counts)
                            p_bright_arr = np.append(p_bright_arr, p_bright)
                            p_dark_arr = np.append(p_dark_arr, p_dark_r)

                    ratio = p_bright_arr/p_dark_arr
                    dark_ml = np.where(ratio < 1.0)
                    fid_ml = float(len(dark_ml[0]))/len(p_dark_arr)
                    ml_data = np.column_stack((ratio, p_bright_arr, p_dark_arr))

                    self.dv.add(i, fid_ml, context = self.c_ML_prob)
                    self.dv.add(ml_data, context = self.c_ML_hist_bright)
            self.pulser.switch_auto('TTL8',False)
            i = i + 1
            continue
        self.pulser.switch_manual('TTL8',True)
        #self.shutter.ttl_output(10, False)

    def set_up_datavault(self):
        # set up folder
        date = datetime.datetime.now()
        year  = `date.year`
        month = '%02d' % date.month  # Padded with a zero if one digit
        day   = '%02d' % date.day    # Padded with a zero if one digit
        trunk = year + '_' + month + '_' + day

        # Define data sets for probability and the associated histograms
        self.dv.cd(['',year,month,trunk],True, context = self.c_prob)
        # prob
        dataset = self.dv.new('High_Fid_prob',[('run', 'time')], [('num', 'prob', 'num')], context = self.c_prob)
        # add dv params
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context = self.c_prob)
        #Hist
        self.dv.cd(['',year,month,trunk],True, context = self.c_hist_bright)
        dataset1 = self.dv.new('High_Fid_hist_bright',[('run', 'arb u')], [('Counts', 'DC_Hist', 'num'),('Counts', 'SD_Hist', 'num')], context = self.c_hist_bright)

        #Hist
        self.dv.cd(['',year,month,trunk],True, context = self.c_hist_dark)
        dataset3 = self.dv.new('High_Fid_hist_dark',[('run', 'arb u')], [('Counts', 'DC_Hist', 'num'), ('Counts', 'SD_Hist', 'num')], context = self.c_hist_dark)

        #Hist time tags
        self.dv.cd(['',year,month,trunk],True, context = self.c_time_tags_bright)
        dataset2 = self.dv.new('High_Fid_Time_Tags_Bright',[('arb', 'arb')],[('Time', 'Time_Tags', 's')], context = self.c_time_tags_bright)

        # Time Tags
        self.dv.cd(['',year,month,trunk],True, context = self.c_time_tags_dark)
        dataset4 = self.dv.new('High_Fid_Time_Tags_Dark',[('arb', 'arb')],[('Time', 'Time_Tags', 's')], context = self.c_time_tags_dark)

        if self.correct_ML == 'True':
            # prob ML
            self.dv.cd(['',year,month,trunk],True, context = self.c_ML_prob)
            dataset5 = self.dv.new('High_Fid_prob_ML',[('run', 'time')], [('num', 'prob', 'num')], context = self.c_ML_prob)

            #ML Hist ml dark
            self.dv.cd(['',year,month,trunk],True, context = self.c_ML_hist_dark)
            dataset6 = self.dv.new('High_Fid_ML_hist_dark',[('Ratio', 'PB/PD')], \
                                [('Prob', 'P_Bright', 'num'), ('Prob', 'P_Dark', 'num')], context = self.c_ML_hist_dark)

            #ML Hist ml dark
            self.dv.cd(['',year,month,trunk],True, context = self.c_ML_hist_bright)
            dataset7 = self.dv.new('High_Fid_ML_hist_bright',[('Ratio', 'PB/PD')], \
                                [('Prob', 'P_Bright', 'num'), ('Prob', 'P_Dark', 'num')], context = self.c_ML_hist_bright)

            self.grapher.plot(dataset5, 'ML', False)
        # add dv params
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context = self.c_hist_dark)
        self.dv.add_parameter('Readout Threshold', self.disc, context = self.c_hist_dark)

        # Set live plotting
        self.grapher.plot(dataset, 'Threshold', False)


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

    def program_pulse_sequence(self):
        pulse_sequence = main_sequence(self.p)
        pulse_sequence.programSequence(self.pulser)

    def set_hp_frequency(self):
        self.HPA.set_frequency(WithUnit(int(self.LO_freq['MHz']),'MHz'))
        dds_freq = WithUnit(30.- self.LO_freq['MHz']/2 + 10*int(self.LO_freq['MHz']/20),'MHz')
        self.pulser.frequency('LF DDS',dds_freq)

    def set_sd_time_window(self):
        ttl = self.pulser.human_readable_ttl(True)
        print ttl
        for i in range(len(ttl)):
            if ttl[i][1][17] == '1':
                self.ML.t_start = float(ttl[i][0])
                print self.ML.t_start
                for j in range(i,len(ttl)):
                    if ttl[j][1][17] == '0':
                        self.ML.t_stop = float(ttl[j][0])
                        print self.ML.t_stop
                        return

    def finalize(self, cxn, context):
        self.cxn.disconnect()
        self.cxnwlm.disconnect()

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = high_fidelity(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)




