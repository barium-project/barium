import labrad
from twisted.internet.defer import inlineCallbacks, returnValue
from common.lib.servers.script_scanner.scan_methods import experiment
from barium.lib.scripts.pulse_sequences.MetastableRabiFlopping import metastable_rabi_flopping as main_sequence
from config.FrequencyControl_config import FrequencyControl_config
from config.multiplexerclient_config import multiplexer_config

import time
from labrad.units import WithUnit
import numpy as np
import datetime as datetime

class metastable_rabi_flopping(experiment):

    name = 'Metastable Rabi Flopping'

    exp_parameters = [('MetastableRabiExp','Sequences_Per_Point'),
                      ('MetastableRabiExp','Start_Time'),
                      ('MetastableRabiExp','Stop_Time'),
                      ('MetastableRabiExp','Time_Step'),
                      ('MetastableRabiExp','dc_threshold'),
                      ('MetastableRabiExp', 'E2_Amplitude'),
                      ('MetastableRabiExp', 'E2_Frequency'),
                      ('MetastableRabiExp', 'Mode'),
                      ]

    # Add the parameters from the required subsequences
    exp_parameters.extend(main_sequence.all_required_parameters())

    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.cxn = labrad.connect(name ='Metastable Rabi')
        self.cxnwlm = labrad.connect(multiplexer_config.ip, name = 'Metastable Rabi', password = 'lab')

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
        self.cycles = self.p.MetastableRabiExp.Sequences_Per_Point
        self.start_time = self.p.MetastableRabiExp.Start_Time
        self.stop_time = self.p.MetastableRabiExp.Stop_Time
        self.step_time = self.p.MetastableRabiExp.Time_Step
        self.dc_thresh = self.p.MetastableRabiExp.dc_threshold
        self.hp_freq = self.p.MetastableRabiExp.E2_Frequency
        self.hp_amp = self.p.MetastableRabiExp.E2_Amplitude
        self.disc = self.pv.get_parameter('StateReadout','state_readout_threshold')
        self.mode = self.p.MetastableRabiExp.Mode
        self.prep = self.p.PSMetastableRabi.prep_state
            
        self.total_exps = 0
        self.total_sd_counts = np.array([])

    # Define contexts for saving data sets
        self.c_prob= self.cxn.context()
        self.c_hist = self.cxn.context()

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

        self.set_hp_frequency(self.hp_freq)
        self.set_hp_amplitude(self.hp_amp)
        self.set_hp_rf_state(True)
        time.sleep(.3) # time to switch
        self.pulser.switch_auto('TTL8',False)

        for i in range(len(t)):
            if self.pause_or_stop():
                # Turn on LED if aborting experiment
                self.pulser.switch_manual('TTL8',True)
                return

            if self.mode == 'Normal':
                self.p.MetaStableRaman.raman_duration = WithUnit(t[i],'us')

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

                pmt_counts = self.pulser.get_readout_counts()
                
                # count 3 times
                dc_counts = pmt_counts[::3]
                herald_counts = pmt_counts[1::3]
                sd_counts = pmt_counts[2::3]
                
                
                # first throw away bad counts when DC
                ind = np.where(dc_counts < self.dc_thresh)
                hearld_counts_1 = np.delete(herald_counts,ind[0])
                sd_counts_1 = np.delete(sd_counts,ind[0])
                
                
                
                
                # now only keep counts where heralding measured dark
                self.disc = self.pv.get_parameter('StateReadout','state_readout_threshold')
                ind_1 = np.where(hearld_counts_1 > self.disc)
                sd_counts_2 = np.delete(sd_counts_1,ind_1[0])
                # keep track of how many successful exps we've done
                self.total_sd_counts = np.append(self.total_sd_counts,\
                                                 sd_counts_2)
                
                print "Herladed exps", len(sd_counts_2)
                
                # 1 (F=3) state is dark for shelving state detection
                dark_sd = np.where(sd_counts_2 <= self.disc)
                fid_sd = float(len(dark_sd[0]))/len(sd_counts_2)
                    
                    
                if self.prep == '1':
                    tot_dark = np.where(self.total_sd_counts <= self.disc)
                    tot_bright = np.where(self.total_sd_counts > self.disc)
                    tot_fid = float(len(tot_dark[0]))/len(self.total_sd_counts)
                    tot_err =  np.sqrt(float(len(tot_bright[0])))/len(self.total_sd_counts)
                    print "Fidelity 1 state: ", '{:.4f}'.format(tot_fid), '+/-',\
                            '{:.4e}'.format(tot_err)
                else:
                    tot_dark = np.where(self.total_sd_counts <= self.disc)
                    tot_bright = np.where(self.total_sd_counts > self.disc)
                    tot_fid = float(len(tot_bright[0]))/len(self.total_sd_counts)
                    tot_err =  np.sqrt(float(len(tot_dark[0])))/len(self.total_sd_counts)
                    print "Fidelity 0 state: ", '{:.4f}'.format(tot_fid), '+/-',\
                            '{:.4e}'.format(tot_err)
                    

                # We want to save all the experimental data, include dc as sd counts
                # SD histogram needs to be the last column for the 
                # histogram client to work correctly
                exp_list = np.arange(self.cycles)
                data = np.column_stack((exp_list, dc_counts, herald_counts, sd_counts))
                self.dv.add(data, context = self.c_hist)
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
                                    
                    self.dv.add(np.column_stack((i, fid_sd)), context = self.c_prob)
                    i = i + 1
                    continue

                # Not in repeat save time vs prob
                self.dv.add(np.column_stack((t[i], fid_sd)), context = self.c_prob)

                break
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
        dataset = self.dv.new('metastable_rabi_prob',[('num', 'arb')], \
                              [('Probability', 'prob', 'num')], context = self.c_prob)
        # add dv params
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context = self.c_prob)

        self.dv.add_parameter('1762 Frequency', self.bristol.get_frequency(), context = self.c_prob)

 
        #Hist with dc, herald, sd and ds counts
        self.dv.cd(['',year,month,trunk],True, context = self.c_hist)
        dataset2 = self.dv.new('metastable_rabi_hist',[('run', 'arb u')],\
                               [('Counts', 'DC_Hist', 'num'), \
                                ('Counts', 'Herald_Hist', 'num'),\
                                ('Counts', 'SD_Hist', 'num')], context = self.c_hist)

        self.dv.add_parameter('Readout Threshold', self.disc, context = self.c_hist)

        # Set live plotting
        self.grapher.plot(dataset, 'rabi_flopping', False)


    def set_wm_frequency(self, freq, chan):
        self.wm.set_pid_course(chan, freq)

    def get_device_map(self):
        gpib_listA = FrequencyControl_config.gpibA
        gpib_listB = FrequencyControl_config.gpibB
        gpib_listC = FrequencyControl_config.gpibC
        

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
                
        devices = self.HP3.list_devices()
        for i in range(len(gpib_listC)):
            for j in range(len(devices)):
                if devices[j][1].find(gpib_listC[i]) > 0:
                    self.device_mapC[gpib_listC[i]] = devices[j][0]
                    break

    def remove_protection_beam(self):
        for i in range(5):
            self.pb.protection_off()
            time.sleep(.3)
            print "trying to remove " + str(i) + "--" + str(self.pb.get_protection_state())
            if not self.pb.get_protection_state():
                return True
        print 'failed to remove protection beam'
        return False

    def program_pulse_sequence(self):
        pulse_sequence = main_sequence(self.p)
        pulse_sequence.programSequence(self.pulser)

        
    def set_hp_rf_state(self, state):
        self.HP3.rf_state(state)
                
    def set_hp_amplitude(self, amp):
        self.HP3.set_amplitude(amp)
                
    def set_hp_frequency(self, freq):
        self.HP3.set_frequency(freq)
        #self.HP3.set_frequency(WithUnit(int(freq),'MHz'))

    def finalize(self, cxn, context):
        self.cxn.disconnect()
        self.cxnwlm.disconnect()

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = metastable_rabi_flopping(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)








        
