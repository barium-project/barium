import labrad
from labrad.units import WithUnit as U
from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
from twisted.internet.defer import inlineCallbacks, returnValue
import numpy as np
import time
import datetime as datetime
from config.FrequencyControl_config import FrequencyControl_config
from keysight import command_expert as kt


class loading_curve(experiment):
    '''
    This experiment is designed to take a loading curve by specifying an
    array of times to load for (filament on), and then look at the data.
    The camera will take a picture before and after loading. The PMT will
    will chop during or after loading based on user input.
    '''

    name = 'Loading Curve'

    exp_parameters = []

    exp_parameters.append(('Loading_Curve', 'Loading_Time'))
    exp_parameters.append(('Loading_Curve', 'Loading_Current'))
    exp_parameters.append(('Loading_Curve', 'Loading_Voltages'))
    exp_parameters.append(('Loading_Curve', 'A_Ramp'))
    exp_parameters.append(('Loading_Curve', 'A_Ramp_Voltage'))
    exp_parameters.append(('Loading_Curve', 'A_Ramp_Time'))
    exp_parameters.append(('Loading_Curve', 'Even_Isotope_Heating_While_Loading'))
    exp_parameters.append(('Loading_Curve', 'Source'))
    exp_parameters.append(('Loading_Curve', 'Subtract_BG'))
    exp_parameters.append(('Loading_Curve', 'Chop_While_Heating'))


    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters


    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.cxn = labrad.connect(name = 'Loading Curve')
        self.cxnHP = labrad.connect('bender', name = 'loading curve', password = 'lab')
        self.trap = self.cxn.trap_server
        self.hp = self.cxnHP.hp6033a_server
        self.hp.select_device(0)
        self.dv = self.cxn.data_vault
        #self.hpa = self.cxnHP.hp8672a_server
        #self.cam = self.cxn.andor_server
        #self.pmt = self.cxn.normalpmtflow
        #self.pulser = self.cxn.pulser

        # Need to map the gpib address to the labrad context number
        #self.device_mapA = {}
        #self.get_device_map()

    def run(self, cxn, context):
        self.set_up_parameters()
        self.set_up_datavault()

        # Get a background image if using the camera
        if self.source == 'Camera':
            self.bg_image = self.get_image()

        elif self.source == 'PMT':
            # Make sure PMT is recording data
            if not self.pmt.isrunning():
                self.pmt.record_data()

            # Start a new data set to watch on grapher
            self.pmt.start_new_dataset()

        for i in range(len(self.time_arr)):
            if self.pause_or_stop():
                break

            # Set the pmt mode
            if self.source == 'PMT':
                if int(self.chop_while_heating) == 1:
                    self.pmt.set_mode('Differential')
                else:
                    self.pmt.set_mode('Normal')
                    # Need to send a TTL high to the rf switch box
                    self.pulser.switch_manual('Internal866',True)

            # Turn on the sideband for even isotope heating
            if int(self.heating) == 1:
                self.hpa.select_device(self.device_mapA['GPIB0::19'])
                self.hpa.rf_state(True)


            # run the filament
            self.run_filament(self.time_arr[i])

            # turn off heating beam
            if int(self.heating) == 1:
                self.hpa.rf_state(False)

            # a ramp
            if int(self.a_ramp) == 1:
                self.a_param()
                time.sleep(1)


            time.sleep(3)

            if self.source == 'Camera':
                image_data = self.get_image()
                if int(self.subtract_bg) == 1:
                    image_data = image_data-self.bg_image

                counts = np.sum(np.sum(image_data))
                self.dv.add(self.time_arr[i],counts)
                time.sleep(1)
                self.trap.trigger_hv_pulse()

            elif self.source == 'PMT':
                # Start Chopping if we weren't
                if int(self.chop_while_heating) == 0:
                    # Switch the trigger back to auto
                    self.pulser.switch_auto('Internal866')
                    self.pmt.set_mode('Differential')

                for j in range(20):
                    counts_on = self.pmt.get_next_counts('ON', 1, False)
                    counts_off = self.pmt.get_next_counts('OFF', 1, False)
                    counts_diff = self.pmt.get_next_counts('DIFF', 1, False)
                    self.dv.add(self.time_arr[i],counts_on, counts_off, counts_diff)


        if self.source == 'PMT':
            self.pmt.set_mode('Normal')

    def set_up_datavault(self):
        # set up folder
        date = datetime.datetime.now()
        year  = `date.year`
        month = '%02d' % date.month  # Padded with a zero if one digit
        day   = '%02d' % date.day    # Padded with a zero if one digit
        trunk = year + '_' + month + '_' + day
        self.dv.cd(['',year,month,trunk],True)
        if self.source == 'PMT':
            dataset = self.dv.new('Loading_Curve',[('Time', 's')], [('KiloCounts/sec','Differential High','num'), \
                            ('KiloCounts/sec','Differential Low','num'),('KiloCounts/sec','Differential','num')])
        else:
            dataset = self.dv.new('Loading_Curve',[('Time', 's')], [('', 'Counts', 'a.b.u')])
        # add dv params
        self.dv.add_parameter('Loading_Current', self.parameters.Loading_Curve.Loading_Current)
        self.dv.add_parameter('Loading_Voltage',self.parameters.Loading_Curve.Loading_Voltages)
        self.dv.add_parameter('Loading_Time', self.parameters.Loading_Curve.Loading_Time)
        self.dv.add_parameter('Source', self.parameters.Loading_Curve.Source)

        self.dv.add_parameter('Subtract_BG', self.parameters.Loading_Curve.Subtract_BG)
        self.dv.add_parameter('A_Ramp',self.parameters.Loading_Curve.A_Ramp)
        self.dv.add_parameter('A_Ramp_Voltage', self.parameters.Loading_Curve.A_Ramp_Voltage)
        self.dv.add_parameter('A_Ramp_Time', self.parameters.Loading_Curve.A_Ramp_Time)
        self.dv.add_parameter('Even_Isotope_Heating', self.parameters.Loading_Curve.Even_Isotope_Heating_While_Loading)
        self.dv.add_parameter('Chop_While_Heating', self.parameters.Loading_Curve.Chop_While_Heating)

    def set_up_parameters(self):
        self.current = self.parameters.Loading_Curve.Loading_Current
        self.voltage = self.parameters.Loading_Curve.Loading_Voltages
        self.subtract_bg = self.parameters.Loading_Curve.Subtract_BG
        self.a_ramp = self.parameters.Loading_Curve.A_Ramp
        self.a_ramp_voltage = self.parameters.Loading_Curve.A_Ramp_Voltage
        self.a_ramp_time = self.parameters.Loading_Curve.A_Ramp_Time
        self.heating = self.parameters.Loading_Curve.Even_Isotope_Heating_While_Loading
        self.source = self.parameters.Loading_Curve.Source
        self.chop_while_heating = self.parameters.Loading_Curve.Chop_While_Heating

        self.min_time = self.parameters.Loading_Curve.Loading_Time[0]['s']
        self.max_time = self.parameters.Loading_Curve.Loading_Time[1]['s']
        self.num_steps = self.parameters.Loading_Curve.Loading_Time[2]

        self.time_arr = np.linspace(self.min_time,self.max_time,self.num_steps)

    def run_filament(self,load_time):
        self.hp.set_voltage(self.voltage)
        self.hp.set_current(self.current)
        self.trap.set_rf_state(False)
        time.sleep(30)
        self.trap.set_rf_state(True)
        time.sleep(int(load_time))
        self.hp.set_current(U(0,'A'))
        time.sleep(3)

    def get_device_map(self):
        gpib_listA = FrequencyControl_config.gpibA
        devices = self.hpa.list_devices()
        for i in range(len(gpib_listA)):
            for j in range(len(devices)):
                if devices[j][1].find(gpib_listA[i]) > 0:
                    self.device_mapA[gpib_listA[i]] = devices[j][0]
                    break

    def a_param(self):
        rod1_volt = self.trap.get_dc_rod(3)
        rod3_volt = self.trap.get_dc_rod(2)
        self.trap.set_dc_rod(self.a_ramp_voltage['V'],3)
        self.trap.set_dc_rod(self.a_ramp_voltage['V'],2)
        time.sleep(self.a_ramp_time['s'])
        self.trap.set_dc_rod(rod1_volt,3)
        self.trap.set_dc_rod(rod3_volt,2)

    def get_image(self):
        #self.cam.set_shutter_mode('Auto')
        #self.cam.set_acquisition_mode('Single Scan')
        #self.cam.start_acquisition()
        #self.cam.wait_for_acquisition()
        image = self.cam.get_most_recent_image(None)
        #self.cam.abort_acquisition()
        #self.cam.set_shutter_mode('Close')
        return image

    def finalize(self, cxn, context):
        self.cxn.disconnect()
        #self.cxnwlm.disconnect()
        self.cxnHP.disconnect()

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = loading_curve(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)


