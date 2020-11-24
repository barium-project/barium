from barium.lib.clients.gui.FrequencyControl_gui import Frequency_Ui
from twisted.internet.defer import inlineCallbacks, returnValue
from PyQt4 import QtGui

#try:
from config.FrequencyControl_config import FrequencyControl_config
#except:
#    from barium.lib.config.TrapControl_config import TrapControl_config
from config.multiplexerclient_config import multiplexer_config

import socket
import os
import numpy as np



class FrequencyControlClient(Frequency_Ui):

    def __init__(self, reactor, parent=None):
        """initialize the GUI creates the reactor

        """
        super(FrequencyControlClient, self).__init__()
        self.password = os.environ['LABRADPASSWORD']
        #self.setSizePolicy(QtGui.QSizePolicy..Minimum, QtGui.QSizePolicy.Fixed)
        self.reactor = reactor
        self.name = socket.gethostname() + ' Frequency Control Client'
        self.device_mapA = {}
        self.device_mapB = {}
        self.context_b = {}
        self.setupUi()
        self.connect()

        #load default parameters and initialize the devices off
        self.lasers = multiplexer_config.info
        self.default = FrequencyControl_config.default
        self.cool_130 = FrequencyControl_config.cool_130
        self.cool_132 = FrequencyControl_config.cool_132
        self.cool_133 = FrequencyControl_config.cool_133
        self.cool_134 = FrequencyControl_config.cool_134
        self.cool_135= FrequencyControl_config.cool_135
        self.cool_136 = FrequencyControl_config.cool_136
        self.cool_137 = FrequencyControl_config.cool_137
        self.cool_138 = FrequencyControl_config.cool_138
        self.heat_135 = FrequencyControl_config.heat_135

    def _check_window_size(self):
        """Checks screen size to make sure window fits in the screen. """
        desktop = QtGui.QDesktopWidget()
        screensize = desktop.availableGeometry()
        width = screensize.width()
        height = screensize.height()
        min_pixel_size = 1080
        if (width <= min_pixel_size or height <= min_pixel_size):
            self.showMaximized()

    @inlineCallbacks
    def connect(self):
        """Creates an Asynchronous connection to the frequency control computer and
        connects incoming signals to relevant functions

        """
        self.serverIP = FrequencyControl_config.ip
        self.wavemeterIP = multiplexer_config.ip


        from labrad.wrappers import connectAsync

        # Connect to wavemeter
        self.cxnWM = yield connectAsync(self.wavemeterIP,
                                      name=self.name,
                                      password=self.password)
        self.wm = self.cxnWM.multiplexerserver

        # Get a connection for each oscillator so the context
        # are different
        self.cxn6 = yield connectAsync(self.serverIP,
                                      name=self.name,
                                      password=self.password)

        self.hp8657b_6 = self.cxn6.hp8657b_server

        self.cxn7 = yield connectAsync(self.serverIP,
                                      name=self.name,
                                      password=self.password)

        self.hp8657b_7 = self.cxn7.hp8657b_server

        self.cxn8 = yield connectAsync(self.serverIP,
                                      name=self.name,
                                      password=self.password)

        self.hp8657b_8 = self.cxn8.hp8657b_server

        self.cxn19 = yield connectAsync(self.serverIP,
                                      name=self.name,
                                      password=self.password)

        self.hp8672a_19 = self.cxn19.hp8672a_server

        self.cxn1 = yield connectAsync(self.serverIP,
                                      name=self.name,
                                      password=self.password)

        self.hp8673_1 = self.cxn1.hp8673server

        self.cxn9 = yield connectAsync(self.serverIP,
                                      name=self.name,
                                      password=self.password)

        self.hp8673_9 = self.cxn9.hp8673server


        self.pulser = self.cxn1.pulser
        self.software_lock = self.cxn1.software_laser_lock_server

        self.clients_hpa = [self.hp8672a_19]
        self.clients_hpb = [self.hp8657b_6, self.hp8657b_7, self.hp8657b_8]
        self.clients_hpc = [self.hp8673_1, self.hp8673_9]

        self.pulser = self.cxn1.pulser
        self.connectHPGUI()


    @inlineCallbacks
    def connectHPGUI(self):

        gpib_listA = FrequencyControl_config.gpibA
        gpib_listB = FrequencyControl_config.gpibB
        gpib_list = FrequencyControl_config.gpibC

        devices = yield self.clients_hpa[0].list_devices()
        for i in range(len(gpib_listA)):
            for j in range(len(devices)):
                if devices[j][1].find(gpib_listA[i]) > 0:
                    self.device_mapA[gpib_listA[i]] = devices[j][0]
                    self.clients_hpa[i].select_device(devices[j][1])
                    break

        devices = yield self.clients_hpb[0].list_devices()
        for i in range(len(gpib_listB)):
            for j in range(len(devices)):
                if devices[j][1].find(gpib_listB[i]) > 0:
                    self.device_mapB[gpib_listB[i]] = devices[j][0]
                    self.clients_hpb[i].select_device(devices[j][1])
                    break
                
        devices = yield self.clients_hpc[0].list_devices()
        for i in range(len(gpib_listC)):
            for j in range(len(devices)):
                if devices[j][1].find(gpib_listC[i]) > 0:
                    self.device_mapC[gpib_listC[i]] = devices[j][0]
                    self.clients_hpb[i].select_device(devices[j][1])
                    break

        # l = yield self.hp8673.list_devices()
        # if len(l) != 0:
        #     self.hp8673.select_device()

        # set up hp8672a oscillators
        self.GPIB19spinFreq.valueChanged.connect(lambda freq = \
                self.GPIB19spinFreq.value(), client = self.clients_hpa[0] : self.freqChangedHPA(freq, client))


        self.GPIB19spinAmpDec.valueChanged.connect(lambda : self.ampChangedHPA19(self.clients_hpa[0]))


        self.GPIB19spinAmpVer.valueChanged.connect(lambda : self.ampChangedHPA19(self.clients_hpa[0]))

        self.GPIB19switch.clicked.connect(lambda state = self.GPIB19switch.isChecked(), \
                client = self.clients_hpa[0] : self.setRFHPA(client, state))


        self.GPIB1spinFreq.valueChanged.connect(lambda freq = \
                self.GPIB1spinFreq.value() : self.freqChangedHP8673(freq))

        self.GPIB1spinAmp.valueChanged.connect(lambda amp = self.GPIB1spinAmp.value() \
                                               : self.ampChangedHP8673(amp))

        self.GPIB1switch.clicked.connect(lambda state = self.GPIB1switch.isChecked(), \
                                         : self.setRFHP8673(state))


        # set up hp8672b oscillators
        self.GPIB6spinFreq.valueChanged.connect(lambda freq = \
                self.GPIB6spinFreq.value(), client = self.clients_hpb[0] : self.freqChangedHPB(freq, client))

        self.GPIB6spinAmp.valueChanged.connect(lambda amp = self.GPIB6spinAmp.value(), \
                client = self.clients_hpb[0] : self.ampChangedHPB(amp, client))

        self.GPIB6switch.clicked.connect(lambda state = self.GPIB6switch.isChecked(), \
                client = self.clients_hpb[0] : self.setRFHPB(client, state))


        self.GPIB7spinFreq.valueChanged.connect(lambda freq = \
                self.GPIB7spinFreq.value(), client = self.clients_hpb[1] : self.freqChangedHPB(freq, client))

        self.GPIB7spinAmp.valueChanged.connect(lambda amp = self.GPIB7spinAmp.value(), \
                client = self.clients_hpb[1] : self.ampChangedHPB(amp, client))

        self.GPIB7switch.clicked.connect(lambda state = self.GPIB7switch.isChecked(), \
                client = self.clients_hpb[1] : self.setRFHPB(client, state))

        '''
        self.GPIB8spinFreq.valueChanged.connect(lambda freq = \
                self.GPIB8spinFreq.value(), client = self.clients_hpb[2] : self.freqChangedHPB(freq, client))

        self.GPIB8spinAmp.valueChanged.connect(lambda amp = self.GPIB8spinAmp.value(), \
                client = self.clients_hpb[2] : self.ampChangedHPB(amp, client))

        self.GPIB8switch.clicked.connect(lambda state = self.GPIB8switch.isChecked(), \
                client = self.clients_hpb[2] : self.setRFHPB(client, state))
        '''

        # Connect push buttons to set freqs
        self.cool130.clicked.connect(lambda : self.cool_ba130())
        self.cool132.clicked.connect(lambda : self.cool_ba132())
        self.cool133.clicked.connect(lambda : self.cool_ba133())
        self.cool134.clicked.connect(lambda : self.cool_ba134())
        self.cool135.clicked.connect(lambda : self.cool_ba135())
        self.cool136.clicked.connect(lambda : self.cool_ba136())
        self.cool137.clicked.connect(lambda : self.cool_ba137())
        self.cool138.clicked.connect(lambda : self.cool_ba138())
        self.heat135.clicked.connect(lambda : self.heat_ba135())
        self.allOff.clicked.connect(lambda: self.all_off())


        #self.setDefault()


    def setDefault(self):

        self.GPIB19spinFreq.setValue(self.default['GPIB0::19'][0])

        self.GPIB19spinAmpDec.setValue(self.default['GPIB0::19'][1])
        self.GPIB19spinAmpVer.setValue(self.default['GPIB0::19'][2])
        self.GPIB19switch.setChecked(False)
        self.setRFHPA(self.clients_hpa[0],False)

        self.GPIB1spinFreq.setValue(self.default['GPIB0::1'][0])
        self.GPIB1spinAmp.setValue(self.default['GPIB0::1'][1])
        self.GPIB1switch.setChecked(False)
        self.setRFHP8673(False)
        '''
        self.GPIB6spinFreq.setValue(self.default['GPIB0::6'][0])
        self.GPIB6spinAmp.setValue(self.default['GPIB0::6'][1])
        self.GPIB6switch.setChecked(False)
        self.setRFHPB(self.clients_hpb[0],False)

        self.GPIB7spinFreq.setValue(self.default['GPIB0::7'][0])
        self.GPIB7spinAmp.setValue(self.default['GPIB0::7'][1])
        self.GPIB7switch.setChecked(False)
        self.setRFHPB(self.clients_hpb[1],False)


        self.GPIB8spinFreq.setValue(self.default['GPIB0::8'][0])
        self.GPIB8spinAmp.setValue(self.default['GPIB0::8'][1])
        self.GPIB8switch.setChecked(False)
        self.setRFHPB(self.clients_hpb[2],False)
        '''
    @inlineCallbacks
    def cool_ba130(self):

        #add the frequency shifts relative to 138
        freq_130_493 = float(self.lasers['493nm'][1]) + self.cool_130['493nm']
        freq_130_650 = float(self.lasers['650nm'][1]) + self.cool_130['650nm']

        yield self.wm.set_pid_course(int(self.lasers['493nm'][5]),freq_130_493)
        yield self.wm.set_pid_course(int(self.lasers['650nm'][5]),freq_130_650)

        self.GPIB19spinFreq.setValue(self.cool_130['GPIB0::19'][0])
        self.GPIB19spinAmpDec.setValue(self.cool_130['GPIB0::19'][1])
        self.GPIB19spinAmpVer.setValue(self.cool_130['GPIB0::19'][2])
        self.GPIB19switch.setChecked(False)
        self.setRFHPA(self.clients_hpa[0],False)

        self.GPIB1spinFreq.setValue(self.cool_130['GPIB0::1'][0])
        self.GPIB1spinAmp.setValue(self.cool_130['GPIB0::1'][1])
        self.GPIB1switch.setChecked(False)
        self.setRFHP8673(False)
        '''
        self.GPIB6spinFreq.setValue(self.cool_130['GPIB0::6'][0])
        self.GPIB6spinAmp.setValue(self.cool_130['GPIB0::6'][1])
        self.GPIB6switch.setChecked(False)
        self.setRFHPB(self.clients_hpb[0],False)

        self.GPIB7spinFreq.setValue(self.cool_130['GPIB0::7'][0])
        self.GPIB7spinAmp.setValue(self.cool_130['GPIB0::7'][1])
        self.GPIB7switch.setChecked(False)
        self.setRFHPB(self.clients_hpb[1],False)

        self.GPIB8spinFreq.setValue(self.cool_130['GPIB0::8'][0])
        self.GPIB8spinAmp.setValue(self.cool_130['GPIB0::8'][1])
        self.GPIB8switch.setChecked(False)
        self.setRFHPB(self.clients_hpb[2],False)
        '''
        # Switch the sidebands off
        yield self.pulser.switch_manual('TTL2',False)
        yield self.pulser.switch_manual('TTL3',False)

    @inlineCallbacks
    def cool_ba132(self):

        #add the frequency shifts relative to 138
        freq_132_493 = float(self.lasers['493nm'][1]) + self.cool_132['493nm']
        freq_132_650 = float(self.lasers['650nm'][1]) + self.cool_132['650nm']

        #yield self.wm.set_pid_course(int(self.lasers['493nm'][5]),freq_132_493)
        yield self.software_lock.set_lock_frequency(freq_132_493,'493nm')
        yield self.wm.set_pid_course(int(self.lasers['650nm'][5]),freq_132_650)

        self.GPIB19spinFreq.setValue(self.cool_132['GPIB0::19'][0])
        self.GPIB19spinAmpDec.setValue(self.cool_132['GPIB0::19'][1])
        self.GPIB19spinAmpVer.setValue(self.cool_132['GPIB0::19'][2])
        self.GPIB19switch.setChecked(False)
        self.setRFHPA(self.clients_hpa[0],False)

        self.GPIB1spinFreq.setValue(self.cool_132['GPIB0::1'][0])
        self.GPIB1spinAmp.setValue(self.cool_132['GPIB0::1'][1])
        self.GPIB1switch.setChecked(False)
        self.setRFHP8673(False)
        '''
        self.GPIB6spinFreq.setValue(self.cool_132['GPIB0::6'][0])
        self.GPIB6spinAmp.setValue(self.cool_132['GPIB0::6'][1])
        self.GPIB6switch.setChecked(False)
        self.setRFHPB(self.clients_hpb[0],False)

        self.GPIB7spinFreq.setValue(self.cool_132['GPIB0::7'][0])
        self.GPIB7spinAmp.setValue(self.cool_132['GPIB0::7'][1])
        self.GPIB7switch.setChecked(False)
        self.setRFHPB(self.clients_hpb[1],False)

        self.GPIB8spinFreq.setValue(self.cool_132['GPIB0::8'][0])
        self.GPIB8spinAmp.setValue(self.cool_132['GPIB0::8'][1])
        self.GPIB8switch.setChecked(False)
        self.setRFHPB(self.clients_hpb[2],False)
        '''
        # Switch the sidebands off
        yield self.pulser.switch_manual('TTL2',False)
        yield self.pulser.switch_manual('TTL3',False)
    @inlineCallbacks
    def cool_ba133(self):

        #add the frequency shifts relative to 138
        freq_133_493 = float(self.lasers['493nm'][1]) + self.cool_133['493nm']
        freq_133_650 = float(self.lasers['650nm'][1]) + self.cool_133['650nm']

        #yield self.wm.set_pid_course(int(self.lasers['493nm'][5]), freq_133_493)
        yield self.software_lock.set_lock_frequency(freq_133_493,'493nm')
        yield self.wm.set_pid_course(int(self.lasers['650nm'][5]), freq_133_650)

        self.GPIB19spinFreq.setValue(self.cool_133['GPIB0::19'][0])
        self.GPIB19spinAmpDec.setValue(self.cool_133['GPIB0::19'][1])
        self.GPIB19spinAmpVer.setValue(self.cool_133['GPIB0::19'][2])
        self.GPIB19switch.setChecked(True)
        self.setRFHPA(self.clients_hpa[0],True)

        self.GPIB1spinFreq.setValue(self.cool_133['GPIB0::1'][0])
        self.GPIB1spinAmp.setValue(self.cool_133['GPIB0::1'][1])
        self.GPIB1switch.setChecked(True)
        self.setRFHP8673(True)

        self.GPIB6spinFreq.setValue(self.cool_133['GPIB0::6'][0])
        self.GPIB6spinAmp.setValue(self.cool_133['GPIB0::6'][1])
        self.GPIB6switch.setChecked(True)
        self.setRFHPB(self.clients_hpb[0],True)

        self.GPIB7spinFreq.setValue(self.cool_133['GPIB0::7'][0])
        self.GPIB7spinAmp.setValue(self.cool_133['GPIB0::7'][1])
        self.GPIB7switch.setChecked(True)
        self.setRFHPB(self.clients_hpb[1],True)

        '''
        self.GPIB8spinFreq.setValue(self.cool_133['GPIB0::8'][0])
        self.GPIB8spinAmp.setValue(self.cool_133['GPIB0::8'][1])
        self.GPIB8switch.setChecked(True)
        self.setRFHPB(self.clients_hpb[2],True)
        '''
        # Switch the sidebands on
        yield self.pulser.switch_auto('TTL2',True)
        yield self.pulser.switch_auto('TTL3',True)
        # Make sure microwave switch is on
        yield self.pulser.switch_auto('TTL4',False)
        yield self.pulser.switch_auto('TTL6',True)
    @inlineCallbacks
    def cool_ba134(self):

        #add the frequency shifts relative to 138
        freq_134_493 = float(self.lasers['493nm'][1]) + self.cool_134['493nm']
        freq_134_650 = float(self.lasers['650nm'][1]) + self.cool_134['650nm']

        #yield self.wm.set_pid_course(int(self.lasers['493nm'][5]),freq_134_493)
        yield self.software_lock.set_lock_frequency(freq_134_493,'493nm')
        yield self.wm.set_pid_course(int(self.lasers['650nm'][5]),freq_134_650)

        self.GPIB19spinFreq.setValue(self.cool_134['GPIB0::19'][0])
        self.GPIB19spinAmpDec.setValue(self.cool_134['GPIB0::19'][1])
        self.GPIB19spinAmpVer.setValue(self.cool_134['GPIB0::19'][2])
        self.GPIB19switch.setChecked(False)
        self.setRFHPA(self.clients_hpa[0],False)

        self.GPIB1spinFreq.setValue(self.cool_134['GPIB0::1'][0])
        self.GPIB1spinAmp.setValue(self.cool_134['GPIB0::1'][1])
        self.GPIB1switch.setChecked(False)
        self.setRFHP8673(False)
        '''
        self.GPIB6spinFreq.setValue(self.cool_134['GPIB0::6'][0])
        self.GPIB6spinAmp.setValue(self.cool_134['GPIB0::6'][1])
        self.GPIB6switch.setChecked(False)
        self.setRFHPB(self.clients_hpb[0],False)

        self.GPIB7spinFreq.setValue(self.cool_134['GPIB0::7'][0])
        self.GPIB7spinAmp.setValue(self.cool_134['GPIB0::7'][1])
        self.GPIB7switch.setChecked(False)
        self.setRFHPB(self.clients_hpb[1],False)

        self.GPIB8spinFreq.setValue(self.cool_134['GPIB0::8'][0])
        self.GPIB8spinAmp.setValue(self.cool_134['GPIB0::8'][1])
        self.GPIB8switch.setChecked(False)
        self.setRFHPB(self.clients_hpb[2],False)
        '''
        # Switch the sidebands off
        yield self.pulser.switch_manual('TTL2',False)
        yield self.pulser.switch_manual('TTL3',False)

    @inlineCallbacks
    def cool_ba135(self):

        #add the frequency shifts relative to 138
        freq_135_493 = float(self.lasers['493nm'][1]) + self.cool_135['493nm']
        freq_135_650 = float(self.lasers['650nm'][1]) + self.cool_135['650nm']

        #yield self.wm.set_pid_course(int(self.lasers['493nm'][5]), freq_135_493)
        yield self.software_lock.set_lock_frequency(freq_135_493,'493nm')
        yield self.wm.set_pid_course(int(self.lasers['650nm'][5]), freq_135_650)

        self.GPIB19spinFreq.setValue(self.cool_135['GPIB0::19'][0])
        self.GPIB19spinAmpDec.setValue(self.cool_135['GPIB0::19'][1])
        self.GPIB19spinAmpVer.setValue(self.cool_135['GPIB0::19'][2])
        self.GPIB19switch.setChecked(True)
        self.setRFHPA(self.clients_hpa[0],True)

        self.GPIB1spinFreq.setValue(self.cool_135['GPIB0::1'][0])
        self.GPIB1spinAmp.setValue(self.cool_135['GPIB0::1'][1])
        self.GPIB1switch.setChecked(True)
        self.setRFHP8673(True)
        '''
        self.GPIB6spinFreq.setValue(self.cool_135['GPIB0::6'][0])
        self.GPIB6spinAmp.setValue(self.cool_135['GPIB0::6'][1])
        self.GPIB6switch.setChecked(True)
        self.setRFHPB(self.clients_hpb[0],True)

        self.GPIB7spinFreq.setValue(self.cool_135['GPIB0::7'][0])
        self.GPIB7spinAmp.setValue(self.cool_135['GPIB0::7'][1])
        self.GPIB7switch.setChecked(True)
        self.setRFHPB(self.clients_hpb[1],True)

        self.GPIB8spinFreq.setValue(self.cool_135['GPIB0::8'][0])
        self.GPIB8spinAmp.setValue(self.cool_135['GPIB0::8'][1])
        self.GPIB8switch.setChecked(True)
        self.setRFHPB(self.clients_hpb[2],True)
        '''

    @inlineCallbacks
    def heat_ba135(self):
        # changing this function to be our loading 
        #add the frequency shifts relative to 138
        freq_135_493 = float(self.lasers['493nm'][1]) - 200*1.e-6 #+ self.heat_135['493nm']
        freq_135_650 = float(self.lasers['650nm'][1]) - 200*1.e-6 #+ self.heat_135['650nm']

        #yield self.wm.set_pid_course(int(self.lasers['493nm'][5]), freq_135_493)
        yield self.software_lock.set_lock_frequency(freq_135_493,'493nm')
        yield self.wm.set_pid_course(int(self.lasers['650nm'][5]), freq_135_650)
        '''
        self.GPIB19spinFreq.setValue(self.cool_135['GPIB0::19'][0])
        self.GPIB19spinAmpDec.setValue(self.cool_135['GPIB0::19'][1])
        self.GPIB19spinAmpVer.setValue(self.cool_135['GPIB0::19'][2])
        self.GPIB19switch.setChecked(True)
        self.setRFHPA(self.clients_hpa[0],True)

        self.GPIB1spinFreq.setValue(self.cool_135['GPIB0::1'][0])
        self.GPIB1spinAmp.setValue(self.cool_135['GPIB0::1'][1])
        self.GPIB1switch.setChecked(True)
        self.setRFHP8673(True)

        self.GPIB6spinFreq.setValue(self.cool_135['GPIB0::6'][0])
        self.GPIB6spinAmp.setValue(self.cool_135['GPIB0::6'][1])
        self.GPIB6switch.setChecked(True)
        self.setRFHPB(self.clients_hpb[0],True)

        self.GPIB7spinFreq.setValue(self.cool_135['GPIB0::7'][0])
        self.GPIB7spinAmp.setValue(self.cool_135['GPIB0::7'][1])
        self.GPIB7switch.setChecked(True)
        self.setRFHPB(self.clients_hpb[1],True)

        self.GPIB8spinFreq.setValue(self.cool_135['GPIB0::8'][0])
        self.GPIB8spinAmp.setValue(self.cool_135['GPIB0::8'][1])
        self.GPIB8switch.setChecked(True)
        self.setRFHPB(self.clients_hpb[2],True)
        '''
    @inlineCallbacks
    def cool_ba136(self):

        #add the frequency shifts relative to 138
        freq_136_493 = float(self.lasers['493nm'][1]) + self.cool_136['493nm']
        freq_136_650 = float(self.lasers['650nm'][1]) + self.cool_136['650nm']

        #yield self.wm.set_pid_course(int(self.lasers['493nm'][5]),freq_136_493)
        yield self.software_lock.set_lock_frequency(freq_136_493,'493nm')
        yield self.wm.set_pid_course(int(self.lasers['650nm'][5]),freq_136_650)

        self.GPIB19spinFreq.setValue(self.cool_136['GPIB0::19'][0])
        self.GPIB19spinAmpDec.setValue(self.cool_136['GPIB0::19'][1])
        self.GPIB19spinAmpVer.setValue(self.cool_136['GPIB0::19'][2])
        self.GPIB19switch.setChecked(False)
        self.setRFHPA(self.clients_hpa[0],False)

        self.GPIB1spinFreq.setValue(self.cool_136['GPIB0::1'][0])
        self.GPIB1spinAmp.setValue(self.cool_136['GPIB0::1'][1])
        self.GPIB1switch.setChecked(False)
        self.setRFHP8673(False)
        '''
        self.GPIB6spinFreq.setValue(self.cool_136['GPIB0::6'][0])
        self.GPIB6spinAmp.setValue(self.cool_136['GPIB0::6'][1])
        self.GPIB6switch.setChecked(False)
        self.setRFHPB(self.clients_hpb[0],False)

        self.GPIB7spinFreq.setValue(self.cool_136['GPIB0::7'][0])
        self.GPIB7spinAmp.setValue(self.cool_136['GPIB0::7'][1])
        self.GPIB7switch.setChecked(False)
        self.setRFHPB(self.clients_hpb[1],False)

        self.GPIB8spinFreq.setValue(self.cool_136['GPIB0::8'][0])
        self.GPIB8spinAmp.setValue(self.cool_136['GPIB0::8'][1])
        self.GPIB8switch.setChecked(False)
        self.setRFHPB(self.clients_hpb[2],False)
        '''
        # Switch the sidebands off
        yield self.pulser.switch_manual('TTL2',False)
        yield self.pulser.switch_manual('TTL3',False)

    @inlineCallbacks
    def cool_ba137(self):

        #add the frequency shifts relative to 138
        freq_137_493 = float(self.lasers['493nm'][1]) + self.cool_137['493nm']
        freq_137_650 = float(self.lasers['650nm'][1]) + self.cool_137['650nm']

        #yield self.wm.set_pid_course(int(self.lasers['493nm'][5]), freq_137_493)
        yield self.software_lock.set_lock_frequency(freq_137_493,'493nm')
        yield self.wm.set_pid_course(int(self.lasers['650nm'][5]), freq_137_650)

        self.GPIB19spinFreq.setValue(self.cool_137['GPIB0::19'][0])
        self.GPIB19spinAmpDec.setValue(self.cool_137['GPIB0::19'][1])
        self.GPIB19spinAmpVer.setValue(self.cool_137['GPIB0::19'][2])
        self.GPIB19switch.setChecked(True)
        self.setRFHPA(self.clients_hpa[0],True)

        self.GPIB1spinFreq.setValue(self.cool_137['GPIB0::1'][0])
        self.GPIB1spinAmp.setValue(self.cool_137['GPIB0::1'][1])
        self.GPIB1switch.setChecked(True)
        self.setRFHP8673(True)
        '''
        self.GPIB6spinFreq.setValue(self.cool_137['GPIB0::6'][0])
        self.GPIB6spinAmp.setValue(self.cool_137['GPIB0::6'][1])
        self.GPIB6switch.setChecked(True)
        self.setRFHPB(self.clients_hpb[0],True)

        self.GPIB7spinFreq.setValue(self.cool_137['GPIB0::7'][0])
        self.GPIB7spinAmp.setValue(self.cool_137['GPIB0::7'][1])
        self.GPIB7switch.setChecked(True)
        self.setRFHPB(self.clients_hpb[1],True)

        self.GPIB8spinFreq.setValue(self.cool_137['GPIB0::8'][0])
        self.GPIB8spinAmp.setValue(self.cool_137['GPIB0::8'][1])
        self.GPIB8switch.setChecked(True)
        self.setRFHPB(self.clients_hpb[2],True)
        '''
    @inlineCallbacks
    def cool_ba138(self):

        #yield self.wm.set_pid_course(int(self.lasers['493nm'][5]),float(self.lasers['493nm'][1]))
        yield self.software_lock.set_lock_frequency(float(self.lasers['493nm'][1]),'493nm')
        yield self.wm.set_pid_course(int(self.lasers['650nm'][5]),float(self.lasers['650nm'][1]))

        self.GPIB19spinFreq.setValue(self.cool_138['GPIB0::19'][0])
        self.GPIB19spinAmpDec.setValue(self.cool_138['GPIB0::19'][1])
        self.GPIB19spinAmpVer.setValue(self.cool_138['GPIB0::19'][2])
        self.GPIB19switch.setChecked(False)
        self.setRFHPA(self.clients_hpa[0],False)

        self.GPIB1spinFreq.setValue(self.cool_138['GPIB0::1'][0])
        self.GPIB1spinAmp.setValue(self.cool_138['GPIB0::1'][1])
        self.GPIB1switch.setChecked(False)
        self.setRFHP8673(False)

        self.GPIB6spinFreq.setValue(self.cool_138['GPIB0::6'][0])
        self.GPIB6spinAmp.setValue(self.cool_138['GPIB0::6'][1])
        self.GPIB6switch.setChecked(False)
        self.setRFHPB(self.clients_hpb[0],False)

        self.GPIB7spinFreq.setValue(self.cool_138['GPIB0::7'][0])
        self.GPIB7spinAmp.setValue(self.cool_138['GPIB0::7'][1])
        self.GPIB7switch.setChecked(False)
        self.setRFHPB(self.clients_hpb[1],False)

        '''
        self.GPIB8spinFreq.setValue(self.cool_138['GPIB0::8'][0])
        self.GPIB8spinAmp.setValue(self.cool_138['GPIB0::8'][1])
        self.GPIB8switch.setChecked(False)
        self.setRFHPB(self.clients_hpb[2],False)
        '''
        # Switch the sidebands off
        yield self.pulser.switch_manual('TTL2',False)
        yield self.pulser.switch_manual('TTL3',False)

    def all_off(self):
        self.GPIB19switch.setChecked(False)
        self.setRFHPA(self.clients_hpa[0],False)
        self.GPIB1switch.setChecked(False)
        self.setRFHP8673(False)
        self.GPIB6switch.setChecked(False)
        self.setRFHPB(self.clients_hpb[0],False)
        self.GPIB7switch.setChecked(False)
        self.setRFHPB(self.clients_hpb[1],False)
        #self.GPIB8switch.setChecked(False)
        #self.setRFHPB(self.clients_hpb[2],False)
        # Switch the sidebands off


    @inlineCallbacks
    def freqChangedHPA(self, freq, client):
        from labrad.units import WithUnit as U
        # Now we use a DDS to set the freq. Need to calculate
        # the DDS freq (always between 20-30 MHz) that puts us
        # at the right spot. Use the HP freq manual to get formula
        dds_freq = U(30.- freq/2 + 10*int(freq/20),'MHz')
        hp_freq = int(freq)
        hp_freq = U(hp_freq,'MHz')
        yield self.pulser.frequency('LF DDS', dds_freq)
        yield client.set_frequency(hp_freq)


    @inlineCallbacks
    def freqChangedHP8673(self, freq):
        from labrad.units import WithUnit as U
        frequency = U(freq,'MHz')
        yield self.hp8673.set_frequency(frequency)

    @inlineCallbacks
    def ampChangedHPA19(self, client):
        from labrad.units import WithUnit as U
        output = self.GPIB19spinAmpDec.value()
        vernier = self.GPIB19spinAmpVer.value()
        out = U(output,'dBm')
        ver = U(vernier,'dBm')
        yield client.set_amplitude(out,ver)

    @inlineCallbacks
    def ampChangedHP8673(self, amp):
        from labrad.units import WithUnit as U
        out = U(amp,'dBm')
        yield self.hp8673.set_amplitude(out)

    @inlineCallbacks
    def setRFHPA(self, client, state):
        yield client.rf_state(state)

    @inlineCallbacks
    def setRFHP8673(self, state):
        yield self.hp8673.rf_state(state)

    #hp8657b
    @inlineCallbacks
    def freqChangedHPB(self, freq, client):
        from labrad.units import WithUnit as U
        frequency = U(freq,'MHz')
        yield client.set_frequency(frequency)

    @inlineCallbacks
    def ampChangedHPB(self, amp, client):
        from labrad.units import WithUnit as U
        amp = U(amp,'dBm')
        yield client.set_amplitude(amp)

    @inlineCallbacks
    def setRFHPB(self, client, state):
        yield client.rf_state(state)



if __name__ == "__main__":
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    FrequencyWidget = FrequencyControlClient(reactor)
    FrequencyWidget.show()
    reactor.run()
