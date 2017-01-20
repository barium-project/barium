from barium.lib.clients.gui.FrequencyControl_gui import Frequency_Ui
from twisted.internet.defer import inlineCallbacks, returnValue
from PyQt4 import QtGui

#try:
from config.FrequencyControl_config import FrequencyControl_config
#except:
#    from barium.lib.config.TrapControl_config import TrapControl_config

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
        self.default = FrequencyControl_config.default


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
        self.cxn6 = yield connectAsync(self.serverIP,
                                      name=self.name,
                                      password=self.password)
        self.hp8675b_6 = self.cxn6.hp8657b_server

        self.cxn7 = yield connectAsync(self.serverIP,
                                      name=self.name,
                                      password=self.password)
        self.hp8675b_7 = self.cxn7.hp8657b_server

        self.cxn8 = yield connectAsync(self.serverIP,
                                      name=self.name,
                                      password=self.password)
        self.hp8675b_8 = self.cxn8.hp8657b_server



        self.clients = [self.hp8675b_6, self.hp8675b_7, self.hp8675b_8]

        self.connectHPGUI()


    @inlineCallbacks
    def connectHPGUI(self):

        #gpib_listA = FrequencyControl_config.gpibA
        gpib_listB = FrequencyControl_config.gpibB
        '''
        devices = yield self.hp8672a_server.list_devices()
        for i in range(len(gpib_listA)):
            for j in range(len(devices)):
                if devices[j][1].find(gpib_listA[i]) > 0:
                    self.device_mapA[gpib_listA[i]] = devices[j][0]
                    break
        '''
        devices = yield self.clients[0].list_devices()
        for i in range(len(gpib_listB)):
            for j in range(len(devices)):
                if devices[j][1].find(gpib_listB[i]) > 0:
                    self.device_mapB[gpib_listB[i]] = devices[j][0]
                    self.clients[i].select_device(devices[j][1])
                    break

        #print self.device_mapA
        print self.device_mapB
        '''
        # set up hp8672a oscillators
        self.GPIB19spinFreq.valueChanged.connect(lambda freq = \
                self.GPIB19spinFreq.value(), device = self.device_mapA['GPIB0::19'] : self.freqChangedHPA(freq, device))


        self.GPIB19spinAmpDec.valueChanged.connect(lambda : self.ampChangedHPA19(self.device_mapA['GPIB0::19']))


        self.GPIB19spinAmpVer.valueChanged.connect(lambda : self.ampChangedHPA19(self.device_mapA['GPIB0::19']))


        self.GPIB21spinFreq.valueChanged.connect(lambda freq = \
                self.GPIB21spinFreq.value(), device = self.device_mapA['GPIB0::21'] : self.freqChangedHPA(freq, device))

        self.GPIB21spinAmpDec.valueChanged.connect(lambda : self.ampChangedHPA21(self.device_mapA['GPIB0::21']))

        self.GPIB21spinAmpVer.valueChanged.connect(lambda : self.ampChangedHPA21(self.device_mapA['GPIB0::21']))

        self.GPIB19switch.clicked.connect(lambda state = self.GPIB19switch.isChecked(), \
                device = self.device_mapA['GPIB0::19'] : self.setRFHPA(device, state))

        self.GPIB21switch.clicked.connect(lambda state = self.GPIB21switch.isChecked(), \
                device = self.device_mapA['GPIB0::21'] : self.setRFHPA(device, state))

        '''
        # set up hp8672b oscillators
        self.GPIB6spinFreq.valueChanged.connect(lambda freq = \
                self.GPIB6spinFreq.value(), client = self.clients[0] : self.freqChangedHPB(freq, client))

        self.GPIB6spinAmp.valueChanged.connect(lambda amp = self.GPIB6spinAmp.value(), \
                client = self.clients[0] : self.ampChangedHPB(amp, client))

        self.GPIB6switch.clicked.connect(lambda state = self.GPIB6switch.isChecked(), \
                client = self.clients[0] : self.setRFHPB(client, state))


        self.GPIB7spinFreq.valueChanged.connect(lambda freq = \
                self.GPIB7spinFreq.value(), client = self.clients[1] : self.freqChangedHPB(freq, client))

        self.GPIB7spinAmp.valueChanged.connect(lambda amp = self.GPIB7spinAmp.value(), \
                client = self.clients[1] : self.ampChangedHPB(amp, client))

        self.GPIB7switch.clicked.connect(lambda state = self.GPIB7switch.isChecked(), \
                client = self.clients[1] : self.setRFHPB(client, state))


        self.GPIB8spinFreq.valueChanged.connect(lambda freq = \
                self.GPIB8spinFreq.value(), client = self.clients[2] : self.freqChangedHPB(freq, client))

        self.GPIB8spinAmp.valueChanged.connect(lambda amp = self.GPIB8spinAmp.value(), \
                client = self.clients[2] : self.ampChangedHPB(amp, client))

        self.GPIB8switch.clicked.connect(lambda state = self.GPIB8switch.isChecked(), \
                client = self.clients[2] : self.setRFHPB(client, state))


        self.setDefault()

    def set19Default(self, params, state):
        self.GPIB19spinFreq.setValue(params['GPIB0::19'][0])
        #self.freqChangedHPA(params['GPIB0::19'][0],self.device_mapA['GPIB0::19'] )
        self.GPIB19spinAmpDec.setValue(params['GPIB0::19'][1])
        self.GPIB19spinAmpVer.setValue(params['GPIB0::19'][2])
        #self.ampChangedHPA19(self.device_mapA['GPIB0::19'])
        #self.setRFHPA(self.device_mapA['GPIB0::19'],state)

    def setDefault(self):
        '''
        self.GPIB21spinFreq.setValue(params['GPIB0::21'][0])
        #self.freqChangedHPA(params['GPIB0::21'][0],self.device_mapA['GPIB0::21'] )
        self.GPIB21spinAmpDec.setValue(params['GPIB0::21'][1])
        self.GPIB21spinAmpVer.setValue(params['GPIB0::21'][2])
        #self.ampChangedHPA21(self.device_mapA['GPIB0::21'])
        #self.setRFHPA(self.device_mapA['GPIB0::21'],state)
        '''


        self.GPIB6spinFreq.setValue(self.default['GPIB0::6'][0])
        self.GPIB6spinAmp.setValue(self.default['GPIB0::6'][1])
        self.setRFHPB(self.clients[0],False)

        self.GPIB7spinFreq.setValue(self.default['GPIB0::7'][0])
        self.GPIB7spinAmp.setValue(self.default['GPIB0::7'][1])
        self.setRFHPB(self.clients[1],False)



        self.GPIB8spinFreq.setValue(self.default['GPIB0::8'][0])
        self.GPIB8spinAmp.setValue(self.default['GPIB0::8'][1])
        self.setRFHPB(self.clients[2],False)

    @inlineCallbacks
    def freqChangedHPA(self, freq, device):
        from labrad.units import WithUnit as U
        frequency = U(freq,'MHz')
        yield self.hp8672a_server.select_device(device)
        yield self.hp8672a_server.set_frequency(frequency)

    @inlineCallbacks
    def ampChangedHPA19(self, device):
        from labrad.units import WithUnit as U
        yield self.hp8672a_server.select_device(device)
        output = self.GPIB19spinAmpDec.value()
        vernier = self.GPIB19spinAmpVer.value()
        out = U(output,'dBm')
        ver = U(vernier,'dBm')
        yield self.hp8672a_server.set_amplitude(out,ver)

    @inlineCallbacks
    def ampChangedHPA21(self, device):
        from labrad.units import WithUnit as U
        yield self.hp8672a_server.select_device(device)
        output = self.GPIB21spinAmpDec.value()
        vernier = self.GPIB21spinAmpVer.value()
        out = U(output,'dBm')
        ver = U(vernier,'dBm')
        yield self.hp8672a_server.set_amplitude(out,ver)

    @inlineCallbacks
    def setRFHPA(self, device, state):
        yield self.hp8672a_server.select_device(device)
        yield self.hp8672a_server.rf_state(state)


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
