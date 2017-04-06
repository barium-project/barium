import labrad
from twisted.internet.defer import inlineCallbacks, returnValue

from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence

from barium.lib.scripts.pulse_sequences.sub_sequences.ProbeLaser import probe_laser as probe_laser
from barium.lib.scripts.pulse_sequences.sub_sequences.DopplerCooling import doppler_cooling as doppler_cooling
from barium.lib.scripts.pulse_sequences.sub_sequences.PhotonTimeTags import photon_timetags as photon_timetags

from config.FrequencyControl_config import FrequencyControl_config
from config.multiplexerclient_config import multiplexer_config

import time
from labrad.units import WithUnit
import numpy as np
import datetime as datetime


class probe_line_scan(experiment):

    name = 'Probe Line Scan'

    exp_parameters = []

    exp_parameters.append(('ProbeLineScan', 'Cooling_Frequency_493'))
    exp_parameters.append(('ProbeLineScan', 'Cooling_Frequency_650'))
    exp_parameters.append(('ProbeLineScan', 'Scan_Frequency_Start'))
    exp_parameters.append(('ProbeLineScan', 'Scan_Frequency_Stop'))
    exp_parameters.append(('ProbeLineScan', 'Scan_Frequency_Step'))
    exp_parameters.append(('ProbeLineScan', 'Probe_Cycles'))
    exp_parameters.append(('ProbeLineScan', 'Carrier_Frequency_493'))
    exp_parameters.append(('ProbeLineScan', 'Carrier_Frequency_650'))
    exp_parameters.append(('ProbeLineScan', 'Cooling_Oscillator'))
    exp_parameters.append(('ProbeLineScan', 'Probe_Oscillator'))

    # Add the parameters from the imported sequences
    exp_parameters.append(probe_laser.all_required_parameters())
    exp_parameters.append(doppler_cooling.all_required_parameters())
    exp_parameters.append(photon_timetags.all_required_parameters())

    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters


    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.cxn = labrad.connect(name = 'Probe Line Scan')
        self.cxnwlm = labrad.connect('10.97.111.8', name = 'Probe Line Scan', password = 'lab')

        self.HPA = self.cxn.hp8672a_server
        self.HPB = self.cxn.hp8657b_server
        self.wm = self.cxnwlm.multiplexerserver
        self.pulser = self.cxn.pulser
        self.grapher = self.cxn.grapher
        self.dv = self.cxn.data_vault

        # Need to map the gpib address to the labrad conection
        self.device_mapA = {}
        self.device_mapB = {}
        self.get_device_map()

        # Define variables to be used
        self.p = self.parameters

        self.frequency_493 = self.p.ProbeLineScan.Carrier_Frequency_493
        self.frequency_650 = self.p.ProbeLineScan.Carrier_Frequency_650
        self.cool_493 = self.p.ProbeLineScan.Cooling_Frequency_493
        self.cool_650 = self.p.ProbeLineScan.Cooling_Frequency_650
        self.start_frequency = self.p.ProbeLineScan.Frequency_Start
        self.stop_frequency = self.p.ProbeLineScan.Frequency_Stop
        self.step_frequency = self.p.ProbeLineScan.Frequency_Step
        self.cycles = self.p.ProbeLineScan.Probe_Cycles

        self.wm_p = multiplexer_config.info

        self.set_up_datavault()


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

        dataset = self.dv.new('ProbeLineScan',[('Frequency', 'MHz')], [('Counts/sec', 'Counts', 'num')])
        self.grapher.plot(dataset, 'spectrum', False)

        # add dv params
        for parameter in self.p:
            self.dv.add_paramter(parameter, self.p[parameter])

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




