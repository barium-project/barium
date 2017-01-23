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
        self.cool_133 = FrequencyControl_config.cool_133
        self.cool_135= FrequencyControl_config.cool_135
        self.cool_138 = FrequencyControl_config.cool_138

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

        self.cxn21 = yield connectAsync(self.serverIP,
                                      name=self.name,
                                      password=self.password)

        self.hp8672a_21 = self.cxn21.hp8672a_server

        self.clients_hpa = [self.hp8672a_19, self.hp8672a_21]
        self.clients_hpb = [self.hp8657b_6, self.hp8657b_7, self.hp8657b_8]

        self.connectHPGUI()


    @inlineCallbacks
    def connectHPGUI(self):

        gpib_listA = FrequencyControl_config.gpibA
        gpib_listB = FrequencyControl_config.gpibB

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



        # set up hp8672a oscillators
        self.GPIB19spinFreq.valueChanged.connect(lambda freq = \
                self.GPIB19spinFreq.value(), client = self.clients_hpa[0] : self.freqChangedHPA(freq, client))


        self.GPIB19spinAmpDec.valueChanged.connect(lambda : self.ampChangedHPA19(self.clients_hpa[0]))


        self.GPIB19spinAmpVer.valueChanged.connect(lambda : self.ampChangedHPA19(self.clients_hpa[0]))


        self.GPIB21spinFreq.valueChanged.connect(lambda freq = \
                self.GPIB21spinFreq.value(), client = self.clients_hpa[1] : self.freqChangedHPA(freq, client))

        self.GPIB21spinAmpDec.valueChanged.connect(lambda : self.ampChangedHPA21(self.clients_hpa[1]))

        self.GPIB21spinAmpVer.valueChanged.connect(lambda : self.ampChangedHPA21(self.clients_hpa[1]))

        self.GPIB19switch.clicked.connect(lambda state = self.GPIB19switch.isChecked(), \
                client = self.clients_hpa[0] : self.setRFHPA(client, state))

        self.GPIB21switch.clicked.connect(lambda state = self.GPIB21switch.isChecked(), \
                client = self.clients_hpa[1] : self.setRFHPA(client, state))


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


        self.GPIB8spinFreq.valueChanged.connect(lambda freq = \
                self.GPIB8spinFreq.value(), client = self.clients_hpb[2] : self.freqChangedHPB(freq, client))

        self.GPIB8spinAmp.valueChanged.connect(lambda amp = self.GPIB8spinAmp.value(), \
                client = self.clients_hpb[2] : self.ampChangedHPB(amp, client))

        self.GPIB8switch.clicked.connect(lambda state = self.GPIB8switch.isChecked(), \
                client = self.clients_hpb[2] : self.setRFHPB(client, state))


        # Connect push buttons to set freqs
        self.cool133.clicked.connect(lambda : self.cool_ba133())
        self.cool135.clicked.connect(lambda : self.cool_ba135())
        self.cool138.clicked.connect(lambda : self.cool_ba138())
        self.allOff.clicked.connect(lambda: self.all_off())


        self.setDefault()


    def setDefault(self):

        self.GPIB19spinFreq.setValue(self.default['GPIB0::19'][0])

        self.GPIB19spinAmpDec.setValue(self.default['GPIB0::19'][1])
        self.GPIB19spinAmpVer.setValue(self.default['GPIB0::19'][2])
        self.GPIB19switch.setChecked(False)
        self.setRFHPA(self.clients_hpa[0],False)

        self.GPIB21spinFreq.setValue(self.default['GPIB0::21'][0])
        self.GPIB21spinAmpDec.setValue(self.default['GPIB0::21'][1])
        self.GPIB21spinAmpVer.setValue(self.default['GPIB0::21'][2])
        self.GPIB21switch.setChecked(False)
        self.setRFHPA(self.clients_hpa[1],False)

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

    @inlineCallbacks
    def cool_ba133(self):

        #add the frequency shifts relative to 138
        freq_133_493 = float(self.lasers['493nm'][1]) + self.cool_133['493nm']
        freq_133_650 = float(self.lasers['650nm'][1]) + self.cool_133['650nm']

        yield self.wm.set_pid_course(int(self.lasers['493nm'][5]), freq_133_493)
        yield self.wm.set_pid_course(int(self.lasers['650nm'][5]), freq_133_650)

        self.GPIB19spinFreq.setValue(self.cool_133['GPIB0::19'][0])
        self.GPIB19spinAmpDec.setValue(self.cool_133['GPIB0::19'][1])
        self.GPIB19spinAmpVer.setValue(self.cool_133['GPIB0::19'][2])
        self.GPIB19switch.setChecked(True)
        self.setRFHPA(self.clients_hpa[0],True)

        self.GPIB21spinFreq.setValue(self.cool_133['GPIB0::21'][0])
        self.GPIB21spinAmpDec.setValue(self.cool_133['GPIB0::21'][1])
        self.GPIB21spinAmpVer.setValue(self.cool_133['GPIB0::21'][2])
        self.GPIB21switch.setChecked(True)
        self.setRFHPA(self.clients_hpa[1],True)

        self.GPIB6spinFreq.setValue(self.cool_133['GPIB0::6'][0])
        self.GPIB6spinAmp.setValue(self.cool_133['GPIB0::6'][1])
        self.GPIB6switch.setChecked(True)
        self.setRFHPB(self.clients_hpb[0],True)

        self.GPIB7spinFreq.setValue(self.cool_133['GPIB0::7'][0])
        self.GPIB7spinAmp.setValue(self.cool_133['GPIB0::7'][1])
        self.GPIB7switch.setChecked(True)
        self.setRFHPB(self.clients_hpb[1],True)

        self.GPIB8spinFreq.setValue(self.cool_133['GPIB0::8'][0])
        self.GPIB8spinAmp.setValue(self.cool_133['GPIB0::8'][1])
        self.GPIB8switch.setChecked(True)
        self.setRFHPB(self.clients_hpb[2],True)


    @inlineCallbacks
    def cool_ba135(self):

        #add the frequency shifts relative to 138
        freq_135_493 = float(self.lasers['493nm'][1]) + self.cool_135['493nm']
        freq_135_650 = float(self.lasers['650nm'][1]) + self.cool_135['650nm']

        yield self.wm.set_pid_course(int(self.lasers['493nm'][5]), freq_135_493)
        yield self.wm.set_pid_course(int(self.lasers['650nm'][5]), freq_135_650)

        self.GPIB19spinFreq.setValue(self.cool_135['GPIB0::19'][0])
        self.GPIB19spinAmpDec.setValue(self.cool_135['GPIB0::19'][1])
        self.GPIB19spinAmpVer.setValue(self.cool_135['GPIB0::19'][2])
        self.GPIB19switch.setChecked(True)
        self.setRFHPA(self.clients_hpa[0],True)

        self.GPIB21spinFreq.setValue(self.cool_135['GPIB0::21'][0])
        self.GPIB21spinAmpDec.setValue(self.cool_135['GPIB0::21'][1])
        self.GPIB21spinAmpVer.setValue(self.cool_135['GPIB0::21'][2])
        self.GPIB21switch.setChecked(True)
        self.setRFHPA(self.clients_hpa[1],True)

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


    @inlineCallbacks
    def cool_ba138(self):

        yield self.wm.set_pid_course(int(self.lasers['493nm'][5]),float(self.lasers['493nm'][1]))
        yield self.wm.set_pid_course(int(self.lasers['650nm'][5]),float(self.lasers['650nm'][1]))

        self.GPIB19spinFreq.setValue(self.cool_138['GPIB0::19'][0])
        self.GPIB19spinAmpDec.setValue(self.cool_138['GPIB0::19'][1])
        self.GPIB19spinAmpVer.setValue(self.cool_138['GPIB0::19'][2])
        self.GPIB19switch.setChecked(False)
        self.setRFHPA(self.clients_hpa[0],False)

        self.GPIB21spinFreq.setValue(self.cool_138['GPIB0::21'][0])
        self.GPIB21spinAmpDec.setValue(self.cool_138['GPIB0::21'][1])
        self.GPIB21spinAmpVer.setValue(self.cool_138['GPIB0::21'][2])
        self.GPIB21switch.setChecked(False)
        self.setRFHPA(self.clients_hpa[1],False)

        self.GPIB6spinFreq.setValue(self.cool_138['GPIB0::6'][0])
        self.GPIB6spinAmp.setValue(self.cool_138['GPIB0::6'][1])
        self.GPIB6switch.setChecked(False)
        self.setRFHPB(self.clients_hpb[0],False)

        self.GPIB7spinFreq.setValue(self.cool_138['GPIB0::7'][0])
        self.GPIB7spinAmp.setValue(self.cool_138['GPIB0::7'][1])
        self.GPIB7switch.setChecked(False)
        self.setRFHPB(self.clients_hpb[1],False)

        self.GPIB8spinFreq.setValue(self.cool_138['GPIB0::8'][0])
        self.GPIB8spinAmp.setValue(self.cool_138['GPIB0::8'][1])
        self.GPIB8switch.setChecked(False)
        self.setRFHPB(self.clients_hpb[2],False)


    def all_off(self):
        self.GPIB19switch.setChecked(False)
        self.setRFHPA(self.clients_hpa[0],False)
        self.GPIB21switch.setChecked(False)
        self.setRFHPA(self.clients_hpa[1],False)
        self.GPIB6switch.setChecked(False)
        self.setRFHPB(self.clients_hpb[0],False)
        self.GPIB7switch.setChecked(False)
        self.setRFHPB(self.clients_hpb[1],False)
        self.GPIB8switch.setChecked(False)
        self.setRFHPB(self.clients_hpb[2],False)


    @inlineCallbacks
    def freqChangedHPA(self, freq, client):
        from labrad.units import WithUnit as U
        frequency = U(freq,'MHz')
        yield client.set_frequency(frequency)

    @inlineCallbacks
    def ampChangedHPA19(self, client):
        from labrad.units import WithUnit as U
        output = self.GPIB19spinAmpDec.value()
        vernier = self.GPIB19spinAmpVer.value()
        out = U(output,'dBm')
        ver = U(vernier,'dBm')
        yield client.set_amplitude(out,ver)

    @inlineCallbacks
    def ampChangedHPA21(self, client):
        from labrad.units import WithUnit as U
        output = self.GPIB21spinAmpDec.value()
        vernier = self.GPIB21spinAmpVer.value()
        out = U(output,'dBm')
        ver = U(vernier,'dBm')
        yield client.set_amplitude(out,ver)

    @inlineCallbacks
    def setRFHPA(self, client, state):
        yield client.rf_state(state)


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
