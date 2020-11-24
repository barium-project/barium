import labrad
from twisted.internet.defer import inlineCallbacks, returnValue

from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
from barium.lib.scripts.pulse_sequences.Shelving import shelving as main_sequence

from config.FrequencyControl_config import FrequencyControl_config
from config.multiplexerclient_config import multiplexer_config

import time
from labrad.units import WithUnit
import numpy as np
import datetime as datetime


class shelving(experiment):

    name = 'shelving'

    exp_parameters = [
                      ('Shelving', 'cycles'),
                      ('Shelving', 'Frequency_Start'),
                      ('Shelving', 'Frequency_Stop'),
                      ('Shelving', 'Frequency_Step'),
                      ('Shelving', 'Start_Time'),
                      ('Shelving', 'Stop_Time'),
                      ('Shelving', 'Time_Step'),
                      ('Shelving', 'dc_threshold'),
                      ('Shelving', 'Mode'),
                      ]

    # Add the parameters from the required subsequences
    exp_parameters.extend(main_sequence.all_required_parameters())

    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters


    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.cxn = labrad.connect(name = 'Shelving')
        self.cxnwlm = labrad.connect('wavemeter', name = 'Frequency Scan', password = 'lab')
        self.wm = self.cxnwlm.multiplexerserver
        #self.bristol = self.cxn.bristolserver
        self.pulser = self.cxn.pulser
        self.dv = self.cxn.data_vault
        self.grapher = self.cxn.real_simple_grapher
        self.single_lock = self.cxn.software_laser_lock_server
        self.pv = self.cxn.parametervault
        self.shutter = self.cxn.arduinottl
        self.pb = self.cxn.protectionbeamserver
        self.reg = self.cxn.registry

        # Define variables to be used
        self.p = self.parameters
        self.cycles = self.p.Shelving.cycles
        self.start_time = self.p.Shelving.Start_Time
        self.stop_time = self.p.Shelving.Stop_Time
        self.step_time = self.p.Shelving.Time_Step
        self.start_freq = self.parameters.Shelving.Frequency_Start
        self.stop_freq = self.parameters.Shelving.Frequency_Stop
        self.step_freq = self.parameters.Shelving.Frequency_Step
        self.scan = self.parameters.Shelving.Scan
        self.scan_laser = self.parameters.Shelving.Scan_Laser
        self.dc_thresh = self.p.Shelving.dc_threshold
        self.disc = self.pv.get_parameter('StateReadout','state_readout_threshold')
        self.mode = self.p.Shelving.Mode


        # Get software laser lock info
        self.reg.cd(['Servers','software_laser_lock'])
        laser = self.reg.get(self.scan_laser)
        # Returns tuple which is not itterable
        laser = list(laser)
        self.scan_laser_chan = laser[1]

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

        if self.scan == 'time':

            t = np.linspace(self.start_time['us'],self.stop_time['us'],\
                    int((abs(self.stop_time['us']-self.start_time['us'])/self.step_time['us']) +1))
            for i in range(len(t)):
                if self.pause_or_stop():
                    # Turn on LED if aborting experiment
                    self.pulser.switch_auto('TTL8',True)
                    return

                if self.mode == 'Normal':
                    if self.scan_laser == '455nm':
                        self.p.Shelving133_Sub.shelving_duration = WithUnit(t[i], 'us')
                    if self.scan_laser == '585nm':
                        self.p.Shelving133_585_Sub.shelving_duration = WithUnit(t[i], 'us')
                    elif self.scan_laser == '1762nm':
                        self.p.Shelving1762.shelving_duration = WithUnit(t[i], 'us')

                self.program_pulse_sequence()
                self.pulser.switch_auto('TTL8',False)
                # for the protection beam we start a while loop and break it if we got the data,
                # continue if we didn't
                while True:
                    if self.pause_or_stop():
                        # Turn on LED if aborting experiment
                        self.pulser.switch_auto('TTL8',True)
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
                        self.pulser.switch_auto('TTL8',True)
                        if self.remove_protection_beam():
                            # If successful switch off LED and return to top of loop
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

                    # If we are in repeat save the data point and rerun the point in the while loop
                    if self.mode == 'Repeat':
                        self.dv.add(i , fid, context = self.c_prob)
                        exp_list = np.arange(self.cycles)

                        # Now the hist with the ones we threw away
                        exp_list = np.delete(exp_list,ind[0])
                        data = np.column_stack((exp_list,counts))
                        self.dv.add(data, context = self.c_hist)
                        # Adding the character c and the number of cycles so plotting the histogram
                        # only plots the most recent point.
                        self.dv.add_parameter('hist'+str(i) + 'c' + str(int(self.cycles)), \
                                      True, context = self.c_hist)
                        i = i + 1
                        continue

                    self.dv.add(t[i] , fid, context = self.c_prob)
                    # Save histogram
                    data = np.column_stack((np.arange(len(counts)),counts))
                    self.dv.add(data, context = self.c_hist)
                    # Adding the character c and the number of cycles so plotting the histogram
                    # only plots the most recent point.
                    self.dv.add_parameter('hist'+str(i) + 'c' + str(int(self.cycles)), True, context = self.c_hist)
                    break
            self.pulser.switch_auto('TTL8',True)

        if self.scan == 'frequency':

            freq = np.linspace(self.start_freq['THz'],self.stop_freq['THz'],\
                    np.round(abs(self.stop_freq['THz']-self.start_freq['THz'])/self.step_freq['THz'],0) +1)


            self.program_pulse_sequence()
            for i in range(len(freq)):
                if self.pause_or_stop():
                    # Turn on LED if aborting experiment
                    self.pulser.switch_auto('TTL8',True)
                    return
                # for the protection beam we start a while loop and break it if we got the data,
                # continue if we didn't
                self.single_lock.set_lock_frequency(freq[i], self.scan_laser)
                time.sleep(5)
                self.pulser.switch_auto('TTL8',False)
                while True:

                    if self.pause_or_stop():
                        # Turn on LED if aborting experiment
                        self.pulser.switch_auto('TTL8',True)
                        return

                    if self.scan_laser == '1762nm':
                        frequency = self.bristol.get_frequency()
                    else:
                        frequency = self.wm.get_frequency(self.scan_laser_chan)


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
                    bright = np.where(counts >= self.disc)
                    fid = float(len(bright[0]))/len(counts)


                    self.dv.add(freq[i] , fid, context = self.c_prob)
                    # Save histogram
                    data = np.column_stack((np.arange(len(counts)),counts))
                    self.dv.add(data, context = self.c_hist)
                    # Adding the character c and the number of cycles so plotting the histogram
                    # only plots the most recent point.
                    self.dv.add_parameter('hist'+str(i) + 'c' + str(int(self.cycles)), True, context = self.c_hist)
                    break
                # since switching frequencies is slow, close shutter and turn LED on while waiting
                self.pulser.switch_manual('TTL8',True)

            self.pulser.switch_manual('TTL8',True)

        if self.scan == 'deshelve':

            t = np.linspace(self.start_time['us'],self.stop_time['us'],\
                    int((abs(self.stop_time['us']-self.start_time['us'])/self.step_time['us']) +1))
            # Open shelving laser shutting and turn LED off
            for i in range(len(t)):
                if self.pause_or_stop():
                    # Turn on LED if aborting experiment
                    self.pulser.switch_auto('TTL8',True)
                    return
                if self.mode == 'Normal':
                    self.p.Deshelving133.deshelving_duration = WithUnit(t[i], 'us')
                self.program_pulse_sequence()
                self.pulser.switch_auto('TTL8',False)
                # for the protection beam we start a while loop and break it if we got the data,
                # continue if we didn't
                while True:
                    if self.pause_or_stop():
                        # Turn on LED if aborting experiment
                        self.pulser.switch_auto('TTL8',True)
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
                        self.pulser.switch_auto('TTL8',True)
                        if self.remove_protection_beam():
                            # If successful switch off LED and return to top of loop
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
                    bright = np.where(counts >= self.disc)
                    fid = float(len(bright[0]))/len(counts)

                 # If we are in repeat save the data point and rerun the point in the while loop
                    if self.mode == 'Repeat':
                        self.dv.add(i , fid, context = self.c_deshelve)
                        exp_list = np.arange(self.cycles)

                        # Now the hist with the ones we threw away
                        exp_list = np.delete(exp_list,ind[0])
                        data = np.column_stack((exp_list,counts))
                        self.dv.add(data, context = self.c_hist)
                        # Adding the character c and the number of cycles so plotting the histogram
                        # only plots the most recent point.
                        self.dv.add_parameter('hist'+str(i) + 'c' + str(int(self.cycles)), \
                                      True, context = self.c_hist)
                        i = i + 1
                        continue
                    self.dv.add(t[i] , fid, context = self.c_deshelve)
                    # Save histogram
                    data = np.column_stack((np.arange(len(counts)),counts))
                    self.dv.add(data, context = self.c_hist)
                    # Adding the character c and the number of cycles so plotting the histogram
                    # only plots the most recent point.
                    self.dv.add_parameter('hist'+str(i) + 'c' + str(int(self.cycles)), True, context = self.c_hist)
                    break
            self.pulser.switch_auto('TTL8',True)

        if self.scan == 'shelve585':
            
            print 'shelve585'
            t = np.linspace(self.start_time['us'],self.stop_time['us'],\
                    int((abs(self.stop_time['us']-self.start_time['us'])/self.step_time['us']) +1))
            for i in range(len(t)):
                if self.pause_or_stop():
                    # Turn on LED if aborting experiment
                    self.pulser.switch_auto('TTL8',True)
                    return


                self.p.Shelving133_Sub.shelving_duration = WithUnit(t[i], 'us')

                # if self.mode == 'Normal':
                #     if self.scan_laser == '455nm':
                #         self.p.Shelving133_Sub.shelving_duration = WithUnit(t[i], 'us')
                #     if self.scan_laser == '585nm':
                #         self.p.Shelving133_Sub.shelving_duration = WithUnit(t[i], 'us')
                #     elif self.scan_laser == '1762nm':
                #         self.p.Shelving1762.shelving_duration = WithUnit(t[i], 'us')

                self.program_pulse_sequence()
                self.pulser.switch_auto('TTL8',False)
                # for the protection beam we start a while loop and break it if we got the data,
                # continue if we didn't
                while True:
                    if self.pause_or_stop():
                        # Turn on LED if aborting experiment
                        self.pulser.switch_auto('TTL8',True)
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
                        self.pulser.switch_auto('TTL8',True)
                        if self.remove_protection_beam():
                            # If successful switch off LED and return to top of loop
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

                    # If we are in repeat save the data point and rerun the point in the while loop
                    if self.mode == 'Repeat':
                        self.dv.add(i , fid, context = self.c_prob)
                        exp_list = np.arange(self.cycles)

                        # Now the hist with the ones we threw away
                        exp_list = np.delete(exp_list,ind[0])
                        data = np.column_stack((exp_list,counts))
                        self.dv.add(data, context = self.c_hist)
                        # Adding the character c and the number of cycles so plotting the histogram
                        # only plots the most recent point.
                        self.dv.add_parameter('hist'+str(i) + 'c' + str(int(self.cycles)), \
                                      True, context = self.c_hist)
                        i = i + 1
                        continue

                    self.dv.add(t[i] , fid, context = self.c_prob)
                    # Save histogram
                    data = np.column_stack((np.arange(len(counts)),counts))
                    self.dv.add(data, context = self.c_hist)
                    # Adding the character c and the number of cycles so plotting the histogram
                    # only plots the most recent point.
                    self.dv.add_parameter('hist'+str(i) + 'c' + str(int(self.cycles)), True, context = self.c_hist)
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

        if self.scan == 'deshelve':
            self.dv.cd(['',year,month,trunk],True, context = self.c_deshelve)
            dataset2 = self.dv.new('deshelving',[('time', 'us')], [('Counts', 'Counts', 'num')], context = self.c_deshelve)
            self.grapher.plot(dataset2, 'shelving', False)
            # add dv params
            for parameter in self.p:
                self.dv.add_parameter(parameter, self.p[parameter], context = self.c_deshelve)

        else:
            self.dv.cd(['',year,month,trunk],True, context = self.c_prob)
            dataset = self.dv.new('shelving_prob',[('time', 'us')], [('Probability', 'Probability', 'num')], context = self.c_prob)
            self.grapher.plot(dataset, 'shelving', False)
            # add dv params
            for parameter in self.p:
                self.dv.add_parameter(parameter, self.p[parameter], context = self.c_prob)


        self.dv.cd(['',year,month,trunk],True, context = self.c_hist)
        dataset1 = self.dv.new('shelving_hist',[('time', 'us')], [('Probability', 'Probability', 'num')], context = self.c_hist)
        # add dv params
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context = self.c_hist)
        self.dv.add_parameter('Readout Threshold', self.disc, context = self.c_hist)


    def finalize(self, cxn, context):
        self.cxn.disconnect()


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = shelving(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)




