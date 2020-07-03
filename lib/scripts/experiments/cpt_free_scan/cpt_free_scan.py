import labrad
from twisted.internet.defer import inlineCallbacks, returnValue

from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
#from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence

from barium.lib.scripts.pulse_sequences.sub_sequences.ProbeLaser import probe_laser as probe_laser
from barium.lib.scripts.pulse_sequences.sub_sequences.DopplerCooling import doppler_cooling as doppler_cooling
from barium.lib.scripts.pulse_sequences.sub_sequences.PhotonTimeTags import photon_timetags as photon_timetags
from barium.lib.scripts.pulse_sequences.CPTFreeScan import cpt_free_scan as main_sequence


from config.FrequencyControl_config import FrequencyControl_config
from config.multiplexerclient_config import multiplexer_config

import time
from labrad.units import WithUnit
import numpy as np
import datetime as datetime


class cpt_free_scan(experiment):

    name = 'CPT Free Scan'

    exp_parameters = []

    exp_parameters.append(('CPTFreeScan', 'Cooling_Sideband_Frequency'))
    exp_parameters.append(('CPTFreeScan', 'Repump_Sideband_Frequency'))
    exp_parameters.append(('CPTFreeScan', 'Probe_Frequency_Start'))
    exp_parameters.append(('CPTFreeScan', 'Probe_Frequency_Stop'))
    exp_parameters.append(('CPTFreeScan', 'Probe_Frequency_Step'))
    exp_parameters.append(('CPTFreeScan', 'Probe_Cycles'))
    exp_parameters.append(('CPTFreeScan', 'Repump_Cycles'))
    exp_parameters.append(('CPTFreeScan', 'Carrier_Frequency_493'))
    exp_parameters.append(('CPTFreeScan', 'Carrier_Frequency_650'))
    exp_parameters.append(('CPTFreeScan', 'Cooling_Oscillator'))
    exp_parameters.append(('CPTFreeScan', 'Probe_Oscillator'))
    exp_parameters.append(('CPTFreeScan', 'Repump_Oscillator'))
    exp_parameters.append(('CPTFreeScan', 'Repeats_Per_Point'))
    exp_parameters.append(('CPTFreeScan', 'Repump_Duration'))

    # Add the parameters from the required subsequences
    exp_parameters.extend(probe_laser.all_required_parameters())
    exp_parameters.extend(doppler_cooling.all_required_parameters())
    exp_parameters.extend(photon_timetags.all_required_parameters())

    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters


    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.wm_p = multiplexer_config.info
        self.cxn = labrad.connect(name = 'CPT Free Scan')
        self.cxnwlm = labrad.connect(self.wm_p.ip, name = 'CPT Free Scan', password = 'lab')

        self.HPA_cool = self.cxn.hp8672a_server
        self.HPB_cool = self.cxn.hp8657b_server
        self.HPA_probe = self.cxn.hp8672a_server
        self.HPB_probe = self.cxn.hp8657b_server
        self.wm = self.cxnwlm.multiplexerserver
        self.pulser = self.cxn.pulser
        self.grapher = self.cxn.real_simple_grapher
        self.dv = self.cxn.data_vault

        # Need to map the gpib address to the labrad conection
        self.device_mapA = {}
        self.device_mapB = {}
        self.get_device_map()

        # Define variables to be used
        self.p = self.parameters


        self.frequency_493 = self.p.CPTFreeScan.Carrier_Frequency_493
        self.frequency_650 = self.p.CPTFreeScan.Carrier_Frequency_650
        self.cool_sb = self.p.CPTFreeScan.Cooling_Sideband_Frequency
        self.repump_sb = self.p.CPTFreeScan.Repump_Sideband_Frequency
        self.start_frequency = self.p.CPTFreeScan.Probe_Frequency_Start
        self.stop_frequency = self.p.CPTFreeScan.Probe_Frequency_Stop
        self.step_frequency = self.p.CPTFreeScan.Probe_Frequency_Step
        self.probe_cycles = self.p.CPTFreeScan.Probe_Cycles
        self.repump_cycles = self.p.CPTFreeScan.Repump_Cycles
        self.cooling_oscillator = self.p.CPTFreeScan.Cooling_Oscillator
        self.probe_oscillator = self.p.CPTFreeScan.Probe_Oscillator
        self.repump_oscillator = self.p.CPTFreeScan.Repump_Oscillator
        self.repeats = self.p.CPTFreeScan.Repeats_Per_Point



        self.set_up_datavault()
        self.set_init_frequencies()

    def run(self, cxn, context):

        freq = np.linspace(self.start_frequency['MHz'],self.stop_frequency['MHz'],\
                    int((abs(self.stop_frequency['MHz']-self.start_frequency['MHz'])/self.step_frequency['MHz']) +1))


        # program sequence to be repeated
        pulse_sequence = main_sequence(self.p)
        pulse_sequence.programSequence(self.pulser)

        # Select probe oscillator
        if self.probe_oscillator == 'GPIB0::19':
            self.HPA_probe.select_device(self.device_mapA[self.probe_oscillator])

            for i in range(len(freq)):
                if self.pause_or_stop():
                    break

                self.HPA.set_frequency(WithUnit(freq[i],'MHz'))
                time.sleep(.5) # time to switch frequencies
                counts = 0
                for j in range(int(self.repeats)):
                    self.pulser.start_number(int(self.probe_cycles))
                    self.pulser.wait_sequence_done()
                    self.pulser.stop_sequence()
                    time_tags = self.pulser.get_timetags()
                    frequency = (self.wm.get_frequency(self.wm_p['493nm'][0]) - self.frequency_493['THz'])*1e6 # MHz
                    counts = counts + len(time_tags)
                    self.pulser.reset_timetags()
                self.dv.add(frequency+freq[i],counts)
        else:
            self.HPB_probe.select_device(self.device_mapB[self.probe_oscillator])

            for i in range(len(freq)):
                if self.pause_or_stop():
                    break

                self.HPB.set_frequency(WithUnit(freq[i],'MHz'))
                counts = 0
                for j in range(int(self.repeats)):
                    self.pulser.start_number(int(self.probe_cycles))
                    self.pulser.wait_sequence_done()
                    self.pulser.stop_sequence()
                    time_tags = self.pulser.get_timetags()
                    frequency = (self.wm.get_frequency(self.wm_p['650nm'][0]) - self.frequency_650['THz'])*1e6 # MHz
                    counts = counts + len(time_tags)
                    self.pulser.reset_timetags()
                self.dv.add(frequency+freq[i],counts)



    def set_init_frequencies(self):

        # First set laser carriers
        self.set_wm_frequency(self.frequency_493['THz'], self.wm_p['493nm'][5])
        self.set_wm_frequency(self.frequency_650['THz'], self.wm_p['650nm'][5])
        time.sleep(5)

        # Set cooling and repump oscillators

        #self.HPA_cool.select_device(self.device_mapA['GPIB0::21'])
        #self.HPA_cool.set_frequency(self.cool_sb)
        self.HPB_cool.select_device(self.device_mapB['GPIB::6'])
        self.HPB_cool.set_frequency(self.repump_sb)



        # time to switch oscillators
        time.sleep(.5)

    def set_up_datavault(self):
        # set up folder
        date = datetime.datetime.now()
        year  = `date.year`
        month = '%02d' % date.month  # Padded with a zero if one digit
        day   = '%02d' % date.day    # Padded with a zero if one digit
        trunk = year + '_' + month + '_' + day
        self.dv.cd(['',year,month,trunk],True)
        dataset = self.dv.new('CPTFreeScan',[('Frequency', 'MHz')], [('Counts/sec', 'Counts', 'num')])
        # add dv params
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter])

        # Set live plotting
        self.grapher.plot(dataset, 'spectrum', False)

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
    exprt = cpt_free_scan(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)




