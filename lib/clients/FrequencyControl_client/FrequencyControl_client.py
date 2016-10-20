from barium.lib.clients.gui.FrequencyControl_gui import Ui_Form
from twisted.internet.defer import inlineCallbacks, returnValue
from PyQt4 import QtGui

#try:
from config.FrequencyControl_config import FrequencyControl_config
#except:
#    from barium.lib.config.TrapControl_config import TrapControl_config

import socket
import os
import numpy as np



class FrequencyControlClient(QtGui.QWidget):

    def __init__(self, reactor, parent=None):
        """initializels the GUI creates the reactor

        """
        super(FrequencyControlClient, self).__init__()
        self.password = os.environ['LABRADPASSWORD']
        #self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.gui = Ui_Form()
        self.gui.setupUi(self)
        self.reactor = reactor
        self.name = socket.gethostname() + ' Trap Control Client'
        self.connect()
        #self._check_window_size()


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
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync(self.serverIP,
                                      name=self.name,
                                      password=self.password)

        self.hp8672a_server = yield self.cxn.hp8672a_server
        self.hp8657b_server = yield self.cxn.hp8657b_server
        self.connectGUI()

    @inlineCallbacks
    def connectGUI(self):
        self.device_mapA = {}
        self.device_mapB = {}
        gpib_listA = FrequencyControl_config.gpibA
        gpib_listB = FrequencyControl_config.gpibB

        devices = yield self.hp8672a_server.list_devices()
        for i in range(len(gpib_listA)):
            for j in range(len(devices)):
                if devices[j][1].find(gpib_listA[i]) > 0:
                    self.device_mapA[gpib_listA[i]] = devices[j][0]
                    break

        devices = yield self.hp8657b_server.list_devices()
        for i in range(len(gpib_listB)):
            for j in range(len(devices)):
                if devices[j][1].find(gpib_listB[i]) > 0:
                    self.device_mapB[gpib_listB[i]] = devices[j][0]
                    break

        # set up hp8672a oscillators
        self.gui.GPIB19spinFreq.valueChanged.connect(lambda freq = \
                self.gui.GPIB19spinFreq.value(), device = self.device_mapA['GPIB0::19'] : self.freqChangedHPA(freq, device))

        self.gui.GPIB19spinAmpDec.valueChanged.connect(lambda output = self.gui.GPIB19spinAmpDec.value(), vernier = self.gui.GPIB19spinAmpVer.value(), \
                device = self.device_mapA['GPIB0::19'] : self.ampChangedHPA(output, vernier, device))

        self.gui.GPIB21spinFreq.valueChanged.connect(lambda freq = \
                self.gui.GPIB21spinFreq.value(), device = self.device_mapA['GPIB0::21'] : self.freqChangedHPA(freq, device))

        self.gui.GPIB21spinAmpDec.valueChanged.connect(lambda output = self.gui.GPIB21spinAmpDec.value(), vernier = self.gui.GPIB21spinAmpVer.value(), \
                device = self.device_mapA['GPIB0::21'] : self.ampChangedHPA(output, vernier, device))

        self.gui.GPIB19switch.clicked.connect(lambda state = self.gui.GPIB19switch.isChecked(), \
                device = self.device_mapA['GPIB0::19'] : self.setRFHPA(device, state))

        self.gui.GPIB21switch.clicked.connect(lambda state = self.gui.GPIB21switch.isChecked(), \
                device = self.device_mapA['GPIB0::21'] : self.setRFHPA(device, state))


        # set up hp8672b oscillators
        self.gui.GPIB6spinFreq.valueChanged.connect(lambda freq = \
                self.gui.GPIB6spinFreq.value(), device = self.device_mapB['GPIB0::6'] : self.freqChangedHPB(freq, device))

        self.gui.GPIB6spinAmp.valueChanged.connect(lambda amp = self.gui.GPIB6spinAmp.value(), \
                device = self.device_mapB['GPIB0::6'] : self.ampChangedHPB(amp, device))

        self.gui.GPIB6switch.clicked.connect(lambda state = self.gui.GPIB6switch.isChecked(), \
                device = self.device_mapB['GPIB0::6'] : self.setRFHPB(device, state))


        self.gui.GPIB7spinFreq.valueChanged.connect(lambda freq = \
                self.gui.GPIB7spinFreq.value(), device = self.device_mapB['GPIB0::7'] : self.freqChangedHPB(freq, device))

        self.gui.GPIB7spinAmp.valueChanged.connect(lambda amp = self.gui.GPIB7spinAmp.value(), \
                device = self.device_mapB['GPIB0::7'] : self.ampChangedHPB(amp, device))

        self.gui.GPIB7switch.clicked.connect(lambda state = self.gui.GPIB7switch.isChecked(), \
                device = self.device_mapB['GPIB0::7'] : self.setRFHPB(device, state))


        self.gui.GPIB8spinFreq.valueChanged.connect(lambda freq = \
                self.gui.GPIB8spinFreq.value(), device = self.device_mapB['GPIB0::8'] : self.freqChangedHPB(freq, device))

        self.gui.GPIB8spinAmp.valueChanged.connect(lambda amp = self.gui.GPIB8spinAmp.value(), \
                device = self.device_mapB['GPIB0::8'] : self.ampChangedHPB(amp, device))

        self.gui.GPIB8switch.clicked.connect(lambda state = self.gui.GPIB8switch.isChecked(), \
                device = self.device_mapB['GPIB0::8'] : self.setRFHPB(device, state))


    @inlineCallbacks
    def freqChangedHPA(self, freq, device):
        from labrad.units import WithUnit as U
        frequency = U(freq,'MHz')
        yield self.hp8672a_server.select_device(device)
        yield self.hp8672a_server.set_frequency(frequency)

    @inlineCallbacks
    def ampChangedHPA(self, output, vernier, device):
        from labrad.units import WithUnit as U
        yield self.hp8672a_server.select_device(device)
        out = U(output,'dBm')
        ver = U(vernier,'dBm')
        yield self.hp8672a_server.set_amplitude(out,ver)

    @inlineCallbacks
    def setRFHPA(self, device, state):
        yield self.hp8672a_server.select_device(device)
        yield self.hp8672a_server.rf_state(state)


    #hp8657b
    @inlineCallbacks
    def freqChangedHPB(self, freq, device):
        from labrad.units import WithUnit as U
        frequency = U(freq,'MHz')
        yield self.hp8657b_server.select_device(device)
        yield self.hp8657b_server.set_frequency(frequency)

    @inlineCallbacks
    def ampChangedHPB(self, amp, device):
        from labrad.units import WithUnit as U
        yield self.hp8657b_server.select_device(device)
        amp = U(amp,'dBm')
        yield self.hp8657b_server.set_amplitude(amp)

    @inlineCallbacks
    def setRFHPB(self, device, state):
        yield self.hp8657b_server.select_device(device)
        yield self.hp8657b_server.rf_state(state)



if __name__ == "__main__":
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    FrequencyWidget = FrequencyControlClient(reactor)
    FrequencyWidget.show()
    reactor.run()
