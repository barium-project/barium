import labrad
from twisted.internet.defer import inlineCallbacks, returnValue

from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
from barium.lib.scripts.pulse_sequences.GreenLaserShelving import green_laser_shelving as main_sequence

from config.FrequencyControl_config import FrequencyControl_config
from config.multiplexerclient_config import multiplexer_config

import time
from labrad.units import WithUnit
import numpy as np
import datetime as datetime


class green_laser_shelving(experiment):

    name = 'Green Laser Shelving'

    exp_parameters = [
                      ('GreenLaserShelving', 'exps_to_average'),
                      ('GreenLaserShelving', 'Mode'),
                      ('GreenLaserShelving', 'Start_Time'),
                      ('GreenLaserShelving', 'Stop_Time'),
                      ('GreenLaserShelving', 'Time_Step'),
                      ('GreenLaserShelving', 'dc_threshold')
                      ]

    # Add the parameters from the required subsequences
    exp_parameters.extend(main_sequence.all_required_parameters())

    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters


    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.cxn = labrad.connect(name = 'Green Laser Shelving')
        self.cxnwlm = labrad.connect('wavemeter', name = 'Frequency Scan', password = 'lab')
        self.wm = self.cxnwlm.multiplexerserver
        #self.bristol = self.cxn.bristolserver
        self.pulser = self.cxn.pulser
        self.dv = self.cxn.data_vault
        self.grapher = self.cxn.real_simple_grapher
        self.pv = self.cxn.parametervault
        self.shutter = self.cxn.arduinottl
        self.pb = self.cxn.protectionbeamserver
        self.reg = self.cxn.registry

        # Define variables to be used
        self.p = self.parameters
        self.exps_to_average = self.p.GreenLaserShelving.exps_to_average
        self.start_time = self.p.GreenLaserShelving.Start_Time
        self.stop_time = self.p.GreenLaserShelving.Stop_Time
        self.step_time = self.p.GreenLaserShelving.Time_Step
        self.dc_thresh = self.p.GreenLaserShelving.dc_threshold
        self.disc = self.pv.get_parameter('StateReadout','state_readout_threshold')
        self.mode = self.p.GreenLaserShelving.Mode
        self.power_input= self.p.GreenLaser.amplitude_532


        # Get context for saving probability and histograms
        self.c_prob = self.cxn.context()
        self.c_hist = self.cxn.context()
        self.c_deshelve = self.cxn.context()

        self.set_up_datavault()

    def run(self, cxn, context):
        '''
        There is a limit to how long readout counts will run (count). Instead of producing an
        error it will just stop the pulse sequence and return the stored array.
        Leaving the print statement with length of counts to ensure the correct
        number of experiments is run.
        '''
        t = np.linspace(self.start_time['us'],self.stop_time['us'],\
                int((abs(self.stop_time['us']-self.start_time['us'])/self.step_time['us']) +1))
        for i in range(len(t)):
            if self.pause_or_stop():
                # Turn on LED if aborting experiment
                self.pulser.switch_auto('TTL8',True)
                return

            if self.mode == 'Normal':
                self.p.GreenLaser.laser_duration = WithUnit(t[i], 'us')

            self.program_pulse_sequence()
            self.pulser.switch_auto('TTL8',False)
            # for the protection beam we start a while loop and break it if we got the data,
            # continue if we didn't
            while True:
                if self.pause_or_stop():
                    # Turn on 614 if aborting experiment
                    self.pulser.switch_auto('TTL8',True)
                    return

                self.pulser.reset_readout_counts()
                self.pulser.start_number(int(self.exps_to_average))
                self.pulser.wait_sequence_done()
                self.pulser.stop_sequence()

                # First check if the protection was enabled, do nothing if not
                if not self.pb.get_protection_state():
                    pass
                # if it was enabled, try to fix, continue if successful
                # otherwise call return to break out of function
                else:
                    # Should turn on deshelving 614 while trying
                    self.pulser.switch_auto('TTL8',True)
                    if self.remove_protection_beam():
                        # If successful switch off 614 and return to top of loop
                        self.pulser.switch_auto('TTL8',False)
                        continue
                    else:
                        # Failed, abort experiment
                        self.pulser.switch_auto('TTL8',True)
                        return

                # Here we look to see if the doppler cooling counts were low,
                # and throw out experiments that were below threshold
                pmt_counts = self.pulser.get_readout_counts()
                dc_counts = pmt_counts[::2]
                sd_counts = pmt_counts[1::2]
                ind = np.where(dc_counts < self.dc_thresh)
                counts = np.delete(sd_counts,ind[0])
                print len(dc_counts), len(counts)

                self.disc = self.pv.get_parameter('StateReadout','state_readout_threshold')
                dark = np.where(counts <= self.disc)
                fid = float(len(dark[0]))/len(counts)

                # We want to save all the experimental data, include dc as sd counts
                exp_list = np.arange(len(sd_counts))
                data = np.column_stack((exp_list, dc_counts, sd_counts))
                self.dv.add(data, context = self.c_hist)
                

                # If we are in repeat save the data point and rerun the point in the while loop
                if self.mode == 'Repeat':
                    self.dv.add(i , fid, context = self.c_prob)
##                    exp_list = np.arange(self.exps_to_average)

##                    # Now the hist with the ones we threw away
##                    exp_list = np.delete(exp_list,ind[0])
##                    data = np.column_stack((exp_list,counts))
##                    self.dv.add(data, context = self.c_hist)
##                    # Adding the character c and the number of cycles so plotting the histogram
##                    # only plots the most recent point.
                    self.dv.add_parameter('hist'+str(i) + 'c' + str(int(self.exps_to_average)), \
                                  True, context = self.c_hist)
                    i = i + 1
                    continue
                if self.mode == 'Interweave':
                    self.dv.add(i , fid, context = self.c_prob)
##                    exp_list = np.arange(self.exps_to_average)

##                    # Now the hist with the ones we threw away
##                    exp_list = np.delete(exp_list,ind[0])
##                    data = np.column_stack((exp_list,counts))
##                    self.dv.add(data, context = self.c_hist)
##                    # Adding the character c and the number of cycles so plotting the histogram
##                    # only plots the most recent point.
                    self.dv.add_parameter('hist'+str(i) + 'c' + str(int(self.exps_to_average)), \
                                  True, context = self.c_hist)
                    i = i + 1
                    if i%2==0:
                        self.p.GreenLaser.amplitude_532=WithUnit(-48, 'dBm')
                    else:
                        self.p.GreenLaser.amplitude_532=self.power_input

                    continue

                self.dv.add(t[i], fid, context = self.c_prob)
##                # Save histogram
##                data = np.column_stack((np.arange(len(counts)),counts))
##                self.dv.add(data, context = self.c_hist)
                # Adding the character c and the number of cycles so plotting the histogram
                # only plots the most recent point.
                self.dv.add_parameter('hist'+str(i) + 'c' + str(int(self.exps_to_average)), True, context = self.c_hist)
                break
        self.pulser.switch_auto('TTL8',True)

 

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

    def set_up_datavault(self):
        # set up folder
        date = datetime.datetime.now()
        year  = `date.year`
        month = '%02d' % date.month  # Padded with a zero if one digit
        day   = '%02d' % date.day    # Padded with a zero if one digit
        trunk = year + '_' + month + '_' + day

        # Define data sets for probability and the associated histograms
        self.dv.cd(['',year,month,trunk],True, context = self.c_prob)


        
        dataset = self.dv.new('green_shelving_prob',[('time', 'us')], [('Probability', 'Probability', 'num')], context = self.c_prob)
        self.grapher.plot(dataset, 'shelving', False)



        
        # add dv params
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context = self.c_prob)


##        self.dv.cd(['',year,month,trunk],True, context = self.c_hist)
##        dataset1 = self.dv.new('green_shelving_hist',[('time', 'us')], [('Probability', 'Probability', 'num')], context = self.c_hist)
        
        #Hist with dc counts and sd counts
        self.dv.cd(['',year,month,trunk],True, context = self.c_hist)
        dataset2 = self.dv.new('green_shelving_hist',[('time', 'us')],[('Counts', 'DC_Hist', 'num'), ('Counts', 'SD_Hist', 'num')], context = self.c_hist)



        
        # add dv params
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context = self.c_hist)
        self.dv.add_parameter('Readout Threshold', self.disc, context = self.c_hist)


    def finalize(self, cxn, context):
        self.cxn.disconnect()


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = green_laser_shelving(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)




