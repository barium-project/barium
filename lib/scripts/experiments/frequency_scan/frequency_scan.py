import labrad
from labrad.units import WithUnit as U
from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
import datetime as datetime
from twisted.internet.defer import inlineCallbacks, returnValue
import numpy as np
from config.FrequencyControl_config import FrequencyControl_config
from config.multiplexerclient_config import multiplexer_config
import time

class frequency_scan(experiment):

    name = 'Frequency Scan'

    exp_parameters = []

    exp_parameters.append(('Frequency_Scan', 'Frequency'))
    exp_parameters.append(('Frequency_Scan', 'Frequency_Start'))
    exp_parameters.append(('Frequency_Scan', 'Frequency_Stop'))
    exp_parameters.append(('Frequency_Scan', 'Frequency_Step'))
    exp_parameters.append(('Frequency_Scan', 'Time_Step'))
    exp_parameters.append(('Frequency_Scan', 'Center_Frequency_493'))
    exp_parameters.append(('Frequency_Scan', 'Center_Frequency_650'))
    exp_parameters.append(('Frequency_Scan', 'Center_Frequency_455'))
    exp_parameters.append(('Frequency_Scan', 'Center_Frequency_1762'))
    exp_parameters.append(('Frequency_Scan', 'Return'))
    exp_parameters.append(('Frequency_Scan', 'Return_Frequency'))
    exp_parameters.append(('Frequency_Scan', 'Source'))
    exp_parameters.append(('Frequency_Scan', 'Points'))

    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters


    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.cxn = labrad.connect(name = 'Frequency Scan')
        self.cxnwlm = labrad.connect('wavemeter', name = 'Frequency Scan', password = 'lab')
        #self.cxn = labrad.connect('bender', name = 'Frequency Scan', password = 'lab')

        self.HPA = self.cxn.hp8672a_server
        self.HPB = self.cxn.hp8657b_server
        self.wm = self.cxnwlm.multiplexerserver
        self.pmt = self.cxn.normalpmtflow
        self.grapher = self.cxn.real_simple_grapher
        self.dv = self.cxn.data_vault
        self.cam = self.cxn.andor_server
        self.single_lock = self.cxn.software_laser_lock_server
        self.bristol = self.cxn.bristolserver
        self.shutter = cxn.arduinottl
        self.pulser = cxn.pulser
        self.sls    = cxn.slsserver

        # Need to map the gpib address to the labrad context number
        self.device_mapA = {}
        self.device_mapB = {}

        self.get_device_map()


        self.frequency_493 = self.parameters.Frequency_Scan.Center_Frequency_493
        self.frequency_650 = self.parameters.Frequency_Scan.Center_Frequency_650
        self.frequency_455 = self.parameters.Frequency_Scan.Center_Frequency_455
        self.frequency_1762 = self.parameters.Frequency_Scan.Center_Frequency_1762
        self.frequency = self.parameters.Frequency_Scan.Frequency
        self.start_frequency = self.parameters.Frequency_Scan.Frequency_Start
        self.stop_frequency = self.parameters.Frequency_Scan.Frequency_Stop
        self.step_frequency = self.parameters.Frequency_Scan.Frequency_Step
        self.time_step = self.parameters.Frequency_Scan.Time_Step
        self.return_bool = self.parameters.Frequency_Scan.Return
        self.return_frequency = self.parameters.Frequency_Scan.Return_Frequency
        self.source = self.parameters.Frequency_Scan.Source
        self.points = self.parameters.Frequency_Scan.Points

        self.wm_p = multiplexer_config.info

        # Make sure PMT is recording data
        if not self.pmt.isrunning():
            self.pmt.record_data()
        self.pmt.set_mode('Normal')

        self.set_up_datavault()

        self.binx, self.biny, self.startx, self.stopx, self.starty, self.stopy = self.cam.get_image_region(None)
        self.pixels_x = (self.stopx - self.startx + 1) / self.binx
        self.pixels_y = (self.stopy - self.starty + 1) / self.biny

    def run(self, cxn, context):

        freq = np.linspace(self.start_frequency['THz'],self.stop_frequency['THz'],\
                    int((abs(self.stop_frequency['THz']-self.start_frequency['THz'])/self.step_frequency['THz']) +1))

        freq1 = np.linspace(self.start_frequency['MHz'],self.stop_frequency['MHz'],\
                    int((abs(self.stop_frequency['MHz']-self.start_frequency['MHz'])/self.step_frequency['MHz']) +1))

        if self.frequency == '493':
            # Set and hold to give wm time to move
            self.set_wm_frequency(self.frequency_493['THz'] + freq[0], self.wm_p['493nm'][5])
            time.sleep(5)
            for i in range(len(freq)):
                if self.pause_or_stop():
                    break
                self.set_wm_frequency(self.frequency_493['THz'] + freq[i], self.wm_p['493nm'][5])
                time.sleep(self.time_step['s'])
                frequency = self.wm.get_frequency(self.wm_p['493nm'][0]) - self.frequency_493['THz']
                if self.source == 'pmt':
                    counts = self.pmt.get_next_counts('ON', 1, False)
                else:
                    image = self.cam.get_most_recent_image(None)
                    image_data = np.reshape(image, (self.pixels_y, self.pixels_x))
                    counts = np.sum(np.sum(image_data))
                self.dv.add(frequency*1e6,counts)

            if int(self.return_bool) == 1:
                self.set_wm_frequency(self.frequency_493['THz'] , self.wm_p['493nm'][5])

        if self.frequency == '650':
            self.set_wm_frequency(self.frequency_650['THz'] + freq[0], self.wm_p['650nm'][5])
            time.sleep(5)
            for i in range(len(freq)):
                if self.pause_or_stop():
                    break
                self.set_wm_frequency(self.frequency_650['THz'] + freq[i], self.wm_p['650nm'][5])
                time.sleep(self.time_step['s'])
                frequency = self.wm.get_frequency(self.wm_p['650nm'][0]) - self.frequency_650['THz']
                if self.source == 'pmt':
                    counts = self.pmt.get_next_counts('ON', 1, False)
                else:
                    image = self.cam.get_most_recent_image(None)
                    image_data = np.reshape(image, (self.pixels_y, self.pixels_x))
                    counts = np.sum(np.sum(image_data))
                self.dv.add(frequency*1e6,counts)

            if int(self.return_bool) == 1:
                self.set_wm_frequency(self.frequency_650['THz'] , self.wm_p['650nm'][5])

        if self.frequency == '455':
            print '455'
            self.single_lock.set_lock_frequency(self.frequency_455['THz'] + freq[0])
            time.sleep(5)
            for i in range(len(freq)):
                if self.pause_or_stop():
                    break
                self.single_lock.set_lock_frequency(self.frequency_455['THz'] + freq[i])
                time.sleep(self.time_step['s'])
                frequency = self.wm.get_frequency(self.wm_p['455nm'][0]) - self.frequency_455['THz']
                if self.source == 'pmt':
                    counts = self.pmt.get_next_counts('ON', 1, False)
                else:
                    image = self.cam.get_most_recent_image(None)
                    image_data = np.reshape(image, (self.pixels_y, self.pixels_x))
                    counts = np.sum(np.sum(image_data))
                self.dv.add(frequency*1e6,counts)

            if int(self.return_bool) == 1:
                self.single_lock.set_point(self.frequency_455['THz'])

        if self.frequency == '1762':
            # self.sls.set_frequency(U(freq1[0],'MHz'))
            # use pulser to shutter aom
            #self.pulser.amplitude()
            for i in range(len(freq)):
                if self.pause_or_stop():
                    return
                all_freq = np.array([])
                all_counts = np.array([])
                self.sls.set_frequency(U(freq1[0],'MHz'))

                for j in range(int(self.points)):
                    if self.pause_or_stop():
                    #    self.shutter.ttl_output(10, False)
                        return
                    #time.sleep(self.time_step['s'])
                    frequency = self.bristol.get_frequency()
                    counts = self.pmt.get_next_counts('ON', 1, False)
                    all_freq = np.append(all_freq, frequency)
                    all_counts = np.append(all_counts, counts)

                self.dv.add(np.mean(all_freq)*1e6,np.mean(all_counts))
                #np.mean  -> offset frequency
            #self.shutter.ttl_output(10, False)
        if self.frequency == 'GPIB0::19':
            self.HPA.select_device(self.device_mapA['GPIB0::19'])
            for i in range(len(freq)):
                if self.pause_or_stop():
                    break
                self.HPA.set_frequency(WithUnit(freq1[i],'MHz'))
                time.sleep(self.time_step['s'])
                if self.source == 'pmt':
                    counts = self.pmt.get_next_counts('ON', 1, False)
                else:
                    image = self.cam.get_most_recent_image(None)
                    image_data = np.reshape(image, (self.pixels_y, self.pixels_x))
                    counts = np.sum(np.sum(image_data))
                self.dv.add(freq[i]*1e6,counts)

            if int(self.return_bool) == 1:
                self.HPA.set_frequency(self.return_frequency)


        if self.frequency == 'GPIB0::21':
            self.HPA.select_device(self.device_mapA['GPIB0::21'])
            for i in range(len(freq)):
                if self.pause_or_stop():
                    break
                self.HPA.set_frequency(WithUnit(freq1[i],'MHz'))
                time.sleep(self.time_step['s'])
                if self.source == 'pmt':
                    counts = self.pmt.get_next_counts('ON', 1, False)
                else:
                    image = self.cam.get_most_recent_image(None)
                    image_data = np.reshape(image, (self.pixels_y, self.pixels_x))
                    counts = np.sum(np.sum(image_data))
                self.dv.add(freq[i]*1e6,counts)

            if int(self.return_bool) == 1:
                self.HPA.set_frequency(self.return_frequency)

        if self.frequency == 'GPIB0::6':
            self.HPB.select_device(self.device_mapB['GPIB0::6'])
            for i in range(len(freq)):
                if self.pause_or_stop():
                    break
                self.HPB.set_frequency(WithUnit(freq1[i],'MHz'))
                time.sleep(self.time_step['s'])
                if self.source == 'pmt':
                    counts = self.pmt.get_next_counts('ON', 1, False)
                else:
                    image = self.cam.get_most_recent_image(None)
                    image_data = np.reshape(image, (self.pixels_y, self.pixels_x))
                    counts = np.sum(np.sum(image_data))
                self.dv.add(freq[i]*1e6,counts)

            if int(self.return_bool) == 1:
                self.HPB.set_frequency(self.return_frequency)

        if self.frequency == 'GPIB0::7':
            self.HPB.select_device(self.device_mapB['GPIB0::7'])
            for i in range(len(freq)):
                if self.pause_or_stop():
                    break
                self.HPB.set_frequency(WithUnit(freq1[i],'MHz'))
                time.sleep(self.time_step['s'])
                if self.source == 'pmt':
                    counts = self.pmt.get_next_counts('ON', 1, False)
                else:
                    image = self.cam.get_most_recent_image(None)
                    image_data = np.reshape(image, (self.pixels_y, self.pixels_x))
                    counts = np.sum(np.sum(image_data))
                self.dv.add(freq[i]*1e6,counts)
            if int(self.return_bool) == 1:
                self.HPB.set_frequency(self.return_frequency)

        if self.frequency == 'GPIB0::8':
            self.HPB.select_device(self.device_mapB['GPIB0::8'])
            for i in range(len(freq)):
                if self.pause_or_stop():
                    break
                self.HPB.set_frequency(WithUnit(freq1[i],'MHz'))
                time.sleep(self.time_step['s'])
                if self.source == 'pmt':
                    counts = self.pmt.get_next_counts('ON', 1, False)
                else:
                    image = self.cam.get_most_recent_image(None)
                    image_data = np.reshape(image, (self.pixels_y, self.pixels_x))
                    counts = np.sum(np.sum(image_data))
                self.dv.add(freq[i]*1e6,counts)

            if int(self.return_bool) == 1:
                self.HPB.set_frequency(self.return_frequency)

    def set_up_datavault(self):
        # set up folder
        date = datetime.datetime.now()
        year  = `date.year`
        month = '%02d' % date.month  # Padded with a zero if one digit
        day   = '%02d' % date.day    # Padded with a zero if one digit
        trunk = year + '_' + month + '_' + day
        self.dv.cd(['',year,month,trunk],True)

        dataset = self.dv.new('Line_Scan',[('Frequency', 'MHz')], [('KiloCounts/sec', 'Counts', 'num')])
        #dataset = self.dv.new('Line_Scan',[('Frequency', 'MHz')],('Frequency', 'MHz')], [('KiloCounts/sec', 'Counts', 'num')])
        #cf eg . Rabi Flopping experiment
        self.grapher.plot(dataset, 'spectrum', False)

        # add dv params
        self.dv.add_parameter('Frequency', self.frequency)
        self.dv.add_parameter('Frequency_Start',self.start_frequency)
        self.dv.add_parameter('Frequency_Stop', self.stop_frequency)
        self.dv.add_parameter('Frequency_Step', self.step_frequency)
        self.dv.add_parameter('Time_Step', self.time_step)
        self.dv.add_parameter('Center_Frequency_493',self.frequency_493)
        self.dv.add_parameter('Center_Frequency_650', self.frequency_650)
        self.dv.add_parameter('Return', self.return_bool)
        self.dv.add_parameter('Return_Frequency', self.return_frequency)
        self.dv.add_parameter('493_Start_Frequency', self.wm.get_frequency(self.wm_p['493nm'][0]))
        self.dv.add_parameter('650_Start_Frequency', self.wm.get_frequency(self.wm_p['650nm'][0]))

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

    def set_wm_frequency(self, freq, chan):
        self.wm.set_pid_course(chan, freq)


    def finalize(self, cxn, context):
        self.cxn.disconnect()
        self.cxnwlm.disconnect()

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = frequency_scan(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)




