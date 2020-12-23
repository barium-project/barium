import labrad
from twisted.internet.defer import inlineCallbacks, returnValue

from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
from barium.lib.scripts.pulse_sequences.E2LaserSweep import e2_laser_sweep as main_sequence

from config.FrequencyControl_config import FrequencyControl_config
from config.multiplexerclient_config import multiplexer_config

import time
from labrad.units import WithUnit
import numpy as np
import datetime as datetime


class e2_laser_sweep(experiment):

    name = 'E2 Laser Sweep'

    exp_parameters = [
                      ('E2LaserSweep', 'Sequences_Per_Point'),
                      ('E2LaserSweep', 'Start_Frequency'),
                      ('E2LaserSweep', 'Stop_Frequency'),
                      ('E2LaserSweep', 'Frequency_Step'),
                      ('E2LaserSweep', 'dc_threshold'),
                      ('E2LaserSweep', 'HP_Amplitude'),
                      ('E2LaserSweep', 'Mode'),
                      ('E2LaserSweep', 'exps_to_average'),

                      ]

    # Add the parameters from the required subsequences
    exp_parameters.extend(main_sequence.all_required_parameters())

    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters


    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.cxn = labrad.connect(name = 'E2 Laser Sweep')
        self.cxnwlm = labrad.connect(multiplexer_config.ip, name = 'E2 Laser Sweep', password = 'lab')


        self.wm = self.cxnwlm.multiplexerserver
        self.bristol = self.cxnwlm.bristolserver
        self.pulser = self.cxn.pulser
        self.grapher = self.cxn.real_simple_grapher
        self.dv = self.cxn.data_vault
        
        
#        self.HPA = self.cxn.hp8672a_server
        self.HP3 = self.cxn.hp8673server
        
        self.pv = self.cxn.parametervault
        self.shutter = self.cxn.arduinottl
        self.pb = self.cxn.protectionbeamserver

        # Define variables to be used
        self.p = self.parameters
        self.cycles = self.p.E2LaserSweep.Sequences_Per_Point
        self.averages = int(self.p.E2LaserSweep.exps_to_average)
        self.start_frequency = self.p.E2LaserSweep.Start_Frequency
        self.stop_frequency = self.p.E2LaserSweep.Stop_Frequency
        self.step_frequency = self.p.E2LaserSweep.Frequency_Step
        self.state_detection = self.p.E2LaserSweep.State_Detection
        self.dc_thresh = self.p.E2LaserSweep.dc_threshold
        self.hp_amp = self.p.E2LaserSweep.HP_Amplitude
        self.disc = self.pv.get_parameter('StateReadout','state_readout_threshold')
        self.mode = self.p.E2LaserSweep.Mode

        # Get contexts for saving the data sets
        self.c_prob = self.cxn.context()
        self.c_hist = self.cxn.context()
        self.c_dc_hist = self.cxn.context()

        # Need to map the gpib address to the labrad conection
        self.device_mapA = {}
        self.device_mapB = {}
        self.device_mapC = {}
        self.get_device_map()

        #self.HPA.select_device(self.device_mapA['GPIB0::19'])
    

##### We're using a different GPIB source from the microwaves (uwave_sweep code copied to make this experiment)
        self.HP3.select_device(self.device_mapC['GPIB0::1'])


        self.set_up_datavault()

    def run(self, cxn, context):

        freq = np.linspace(self.start_frequency['MHz'],self.stop_frequency['MHz'],\
                    int((abs(self.stop_frequency['MHz']-self.start_frequency['MHz'])/self.step_frequency['MHz']) +1))

        self.set_hp_frequency(self.start_frequency['MHz'])
        time.sleep(.3) # time to switch frequencies
        
        self.set_hp_amplitude(self.hp_amp['dBm'])
        time.sleep(.3) # time to switch amplitude

        self.set_hp_rf_state(True)


#        if self.state_detection == 'shelving':
#            self.pulser.switch_auto('TTL8',False)

        self.program_pulse_sequence()
        self.pulser.switch_auto('TTL8',False)
        
#        loop_iter = 0        
        for i in range(len(freq)):
            tot_dc_counts = np.array([])
            tot_sd_counts = np.array([])
            tot_counts = np.array([])
            for j in range(self.averages):
                if self.pause_or_stop():
                    # Turn on 614 if aborting experiment
                    self.pulser.stop_sequence()
                    self.pulser.switch_manual('TTL8',True)
                    return
                # for the protection beam we start a while loop and break it if we got the data,
                # continue if we didn't
                # Set the microwave frequency
                
                # If we are in repeat mode, don't change frequency
                if self.mode != 'Repeat':
                    self.set_hp_frequency(freq[i])
                    time.sleep(.3) # time to switch amplitude    
                                    
    
                # for the protection beam we start a while loop and break it if we got the data,
                # continue if we didn't
                while True:
                    if self.pause_or_stop():
                        # Turn on 614 if aborting experiment
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
                            self.set_hp_rf_state(False)
                            # Failed, abort experiment
                            self.pulser.switch_manual('TTL8',True)
                            return
    
                    # Here we look to see if the doppler cooling counts were low,
                    # and throw out experiments that were below threshold
                    pmt_counts = self.pulser.get_readout_counts()
                    dc_counts = pmt_counts[::2]
                    sd_counts = pmt_counts[1::2]
                    ind = np.where(dc_counts < self.dc_thresh)
                    tot_dc_counts = np.append(tot_dc_counts, dc_counts)
                    tot_sd_counts = np.append(tot_sd_counts, sd_counts)
                    counts = np.delete(sd_counts,ind[0])
                    tot_counts = np.append(tot_counts, counts)
                    print len(counts)
                    break
    
            self.disc = self.pv.get_parameter('StateReadout','state_readout_threshold')
            # 1 state is bright for standard state detection

            bright = np.where(tot_counts >= self.disc)
            fid = float(len(bright[0]))/len(tot_counts)

            # If we are in repeat save the data point and rerun the point in the while loop
            if self.mode == 'Repeat':
                self.dv.add(i , fid, context = self.c_prob)
                exp_list = np.arange(self.cycles)

                # Now the hist with the ones we threw away
                exp_list = np.delete(exp_list,ind[0])
                data = np.column_stack((exp_list,tot_counts))
                self.dv.add(data, context = self.c_hist)
                # Adding the character c and the number of cycles so plotting the histogram
                # only plots the most recent point.
                self.dv.add_parameter('hist'+str(i) + 'c' + str(int(self.cycles)), \
                              True, context = self.c_hist)
                i = i + 1
                continue



            # Save freq vs prob
            self.dv.add(freq[i] , fid, context = self.c_prob)
            # We want to save all the experimental data, include dc as sd counts
            exp_list = np.arange(self.cycles*self.averages)
            data = np.column_stack((exp_list, tot_dc_counts, tot_sd_counts))
            self.dv.add(data, context = self.c_dc_hist)

            # Now the hist with the ones we threw away
            exp_list = np.arange(len(tot_counts))
            data = np.column_stack((exp_list,tot_counts))
            self.dv.add(data, context = self.c_hist)


            # Adding the character c and the number of cycles so plotting the histogram
            # only plots the most recent point.
            self.dv.add_parameter('hist'+str(i) + 'c' + str(int(self.cycles)), True, context = self.c_hist)
                
        
        
        self.set_hp_rf_state(False)            
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
        dataset = self.dv.new('E2LaserSweep_prob',[('freq', 'MHz')], [('Probability', 'Probability', 'num')], context = self.c_prob)
        # add dv params
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context = self.c_prob)

        self.dv.add_parameter('1762 Frequency', self.bristol.get_frequency(), context = self.c_prob)

        self.dv.cd(['',year,month,trunk],True, context = self.c_hist)
        dataset1 = self.dv.new('E2LaserSweep_hist',[('freq', 'MHz')], [('Counts', 'Counts', 'num')], context = self.c_hist)
        # add dv params
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context = self.c_hist)
        self.dv.add_parameter('Readout Threshold', self.disc, context = self.c_hist)

        #Hist with dc counts and sd counts
        self.dv.cd(['',year,month,trunk],True, context = self.c_dc_hist)
        dataset2 = self.dv.new('E2LaserSweep_dc_hist',[('run', 'arb u')],\
                               [('Counts', 'DC_Hist', 'num'), ('Counts', 'SD_Hist', 'num')], context = self.c_dc_hist)

        # Set live plotting
        #self.grapher.plot(dataset, 'e2_laser_sweep', False)
        self.grapher.plot(dataset, 'qubit_freq_sweep', False)


    def set_wm_frequency(self, freq, chan):
        self.wm.set_pid_course(chan, freq)

    def get_device_map(self):
        gpib_listA = FrequencyControl_config.gpibA
        gpib_listB = FrequencyControl_config.gpibB
        gpib_listC = FrequencyControl_config.gpibC
        

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
        self.HP3.set_amplitude(WithUnit(amp,'dBm'))
                
    def set_hp_frequency(self, freq):
        self.HP3.set_frequency(WithUnit(freq,'MHz'))
        #self.HP3.set_frequency(WithUnit(int(freq),'MHz'))

    def finalize(self, cxn, context):
        self.cxn.disconnect()
        self.cxnwlm.disconnect()

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = e2_laser_sweep(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)




