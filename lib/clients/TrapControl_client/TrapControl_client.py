from barium.lib.clients.gui.TrapControl_gui import QCustomTrapGui
from common.lib.clients.qtui.q_custom_text_changing_button import \
    TextChangingButton
from twisted.internet.defer import inlineCallbacks, returnValue
from PyQt4 import QtGui
#try:
from config.TrapControl_config import TrapControl_config
#except:
#    from barium.lib.config.TrapControl_config import TrapControl_config

import socket
import os
import numpy as np

SIGNALID1 = 445566
SIGNALID2 = 143533
SIGNALID3 = 111221
SIGNALID4 = 549210
SIGNALID5 = 190909
SIGNALID6 = 102588
SIGNALID7 = 148323
SIGNALID8 = 238883


class TrapControlClient(QtGui.QWidget):

    def __init__(self, reactor, parent=None):
        """initializels the GUI creates the reactor

        """
        super(TrapControlClient, self).__init__()
        self.password = os.environ['LABRADPASSWORD']
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.reactor = reactor
        self.name = socket.gethostname() + ' Trap Control Client'
        self.connect()
        self._check_window_size()

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
        """Creates an Asynchronous connection to the trap control computer and
        connects incoming signals to relavent functions

        """
        self.serverIP = TrapControl_config.ip
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync(self.serverIP,
                                      name=self.name,
                                      password=self.password)

        self.server = yield self.cxn.trap_server
        self.initializeGUI()

    @inlineCallbacks
    def initializeGUI(self):

        self.layout = QtGui.QGridLayout()
        self.qBox = QtGui.QGroupBox('Trap Settings')
        self.subLayout = QtGui.QGridLayout()
        self.qBox.setLayout(self.subLayout)
        self.layout.addWidget(self.qBox, 0, 0)
        # Define dic for storting into
        self.dc = {}
        self.endCap = {}

        # Get config information
        self.init_params = TrapControl_config.params

        # Load RF Map
        self.rf_map = np.loadtxt('rf_map.txt')

        # Get channel numbers for each electrode
        self.rods = TrapControl_config.rods
        self.endCaps = TrapControl_config.endCaps
        self.eLens = TrapControl_config.eLens
        self.setWindowTitle('Trap Control')

        # Create widgets and lay them out.
        # Create general lock button to disable all buttons
        self.lockSwitch = TextChangingButton(('Locked','Unlocked'))
        # Start Unlocked
        self.lockSwitch.setChecked(False)
        #self.lockSwitch.toggled.connect(self.setLock)
        self.subLayout.addWidget(self.lockSwitch, 0, 2)

        # Create a button to initialize trap params
        self.init_trap = QtGui.QPushButton('Set Default Values')
        self.init_trap.setMaximumHeight(30)
        self.init_trap.setFont(QtGui.QFont('MS Shell Dlg 2', pointSize=12))
        self.init_trap.clicked.connect(lambda : self.init_state())
        self.subLayout.addWidget(self.init_trap, 0, 0)
        # initialize main Gui
        self.trap = QCustomTrapGui()

        init_freq1 = yield self.server.get_frequency(self.rods['1'])
        self.trap.spinFreq1.setValue(init_freq1)
        self.trap.spinFreq1.valueChanged.connect(lambda freq = self.trap.spinFreq1.value(), channel = self.rods['1'] : self.freqChanged(freq, channel))
        init_freq2 = yield self.server.get_frequency(self.rods['2'])
        self.trap.spinFreq2.setValue(init_freq2)
        self.trap.spinFreq2.valueChanged.connect(lambda freq = self.trap.spinFreq2.value(), channel = self.rods['2'] : self.freqChanged(freq, channel))
        init_freq3 = yield self.server.get_frequency(self.rods['3'])
        self.trap.spinFreq3.setValue(init_freq3)
        self.trap.spinFreq3.valueChanged.connect(lambda freq = self.trap.spinFreq3.value(), channel = self.rods['3'] : self.freqChanged(freq, channel))
        init_freq4 = yield self.server.get_frequency(self.rods['4'])
        self.trap.spinFreq4.setValue(init_freq4)
        self.trap.spinFreq4.valueChanged.connect(lambda freq = self.trap.spinFreq4.value(), channel = self.rods['4'] : self.freqChanged(freq, channel))

        init_phase1 = yield self.server.get_phase(self.rods['1'])
        self.trap.spinPhase1.setValue(init_phase1)
        self.trap.spinPhase1.valueChanged.connect(lambda phase = self.trap.spinPhase1.value(), channel = self.rods['1'] : self.phaseChanged(phase, channel))
        init_phase2 = yield self.server.get_phase(self.rods['2'])
        self.trap.spinPhase2.setValue(init_phase2)
        self.trap.spinPhase2.valueChanged.connect(lambda phase = self.trap.spinPhase2.value(), channel = self.rods['2'] : self.phaseChanged(phase, channel))
        init_phase3 = yield self.server.get_phase(self.rods['3'])
        self.trap.spinPhase3.setValue(init_phase3)
        self.trap.spinPhase3.valueChanged.connect(lambda phase = self.trap.spinPhase3.value(), channel = self.rods['3'] : self.phaseChanged(phase, channel))
        init_phase4 = yield self.server.get_phase(self.rods['4'])
        self.trap.spinPhase4.setValue(init_phase4)
        self.trap.spinPhase4.valueChanged.connect(lambda phase = self.trap.spinPhase4.value(), channel = self.rods['4'] : self.phaseChanged(phase, channel))

        init_amp1 = yield self.server.get_amplitude(self.rods['1'])
        self.trap.spinAmp1.setValue(init_amp1)
        self.trap.spinAmp1.valueChanged.connect(lambda amp = self.trap.spinAmp1.value(), channel = self.rods['1'] : self.ampChanged(amp, channel))
        init_amp2 = yield self.server.get_amplitude(self.rods['2'])
        self.trap.spinAmp2.setValue(init_amp2)
        self.trap.spinAmp2.valueChanged.connect(lambda amp = self.trap.spinAmp2.value(), channel = self.rods['2'] : self.ampChanged(amp, channel))
        init_amp3 = yield self.server.get_amplitude(self.rods['3'])
        self.trap.spinAmp3.setValue(init_amp3)
        self.trap.spinAmp3.valueChanged.connect(lambda amp = self.trap.spinAmp3.value(), channel = self.rods['3'] : self.ampChanged(amp, channel))
        init_amp4 = yield self.server.get_amplitude(self.rods['4'])
        self.trap.spinAmp4.setValue(init_amp4)
        self.trap.spinAmp4.valueChanged.connect(lambda amp = self.trap.spinAmp4.value(), channel = self.rods['4'] : self.ampChanged(amp, channel))

        init_dc1 = yield self.server.get_dc_rod(self.rods['1'])
        self.trap.spinDC1.setValue(init_dc1)
        self.trap.spinDC1.valueChanged.connect(lambda dc = self.trap.spinDC1.value(), channel = self.rods['1'] : self.dcChanged(dc, channel))
        init_dc2 = yield self.server.get_dc_rod(self.rods['2'])
        self.trap.spinDC2.setValue(init_dc2)
        self.trap.spinDC2.valueChanged.connect(lambda dc = self.trap.spinDC2.value(), channel = self.rods['2'] : self.dcChanged(dc, channel))
        init_dc3 = yield self.server.get_dc_rod(self.rods['3'])
        self.trap.spinDC3.setValue(init_dc3)
        self.trap.spinDC3.valueChanged.connect(lambda dc = self.trap.spinDC3.value(), channel = self.rods['3'] : self.dcChanged(dc, channel))
        init_dc4 = yield self.server.get_dc_rod(self.rods['4'])
        self.trap.spinDC4.setValue(init_dc4)
        self.trap.spinDC4.valueChanged.connect(lambda dc = self.trap.spinDC4.value(), channel = self.rods['4'] : self.dcChanged(dc, channel))

        init_hv1 = yield self.server.get_hv(self.rods['1'])
        self.trap.spinHV1.setValue(init_hv1)
        self.trap.spinHV1.valueChanged.connect(lambda hv = self.trap.spinHV1.value(), channel = self.rods['1'] : self.hvChanged(hv, channel))
        init_hv2 = yield self.server.get_hv(self.rods['2'])
        self.trap.spinHV2.setValue(init_hv2)
        self.trap.spinHV2.valueChanged.connect(lambda hv = self.trap.spinHV2.value(), channel = self.rods['2'] : self.hvChanged(hv, channel))
        init_hv3 = yield self.server.get_hv(self.rods['3'])
        self.trap.spinHV3.setValue(init_hv3)
        self.trap.spinHV3.valueChanged.connect(lambda hv = self.trap.spinHV3.value(), channel = self.rods['3'] : self.hvChanged(hv, channel))
        init_hv4 = yield self.server.get_hv(self.rods['4'])
        self.trap.spinHV4.setValue(init_hv4)
        self.trap.spinHV4.valueChanged.connect(lambda hv = self.trap.spinHV4.value(), channel = self.rods['4'] : self.hvChanged(hv, channel))

        init_ec1 = yield self.server.get_dc(self.endCaps['1'])
        self.trap.spinEndCap1.setValue(init_ec1)
        self.trap.spinEndCap1.valueChanged.connect(lambda endCap = self.trap.spinEndCap1.value(), channel = self.endCaps['1'] : self.endCapChanged(endCap, channel))
        init_ec2 = yield self.server.get_dc(self.endCaps['2'])
        self.trap.spinEndCap2.setValue(init_ec2)
        self.trap.spinEndCap2.valueChanged.connect(lambda endCap = self.trap.spinEndCap2.value(), channel = self.endCaps['2'] : self.endCapChanged(endCap, channel))


        init_rf = yield self.server.get_rf_map_state()

        self.trap.useRFMap.setCheckState(init_rf)
        self.trap.useRFMap.stateChanged.connect(lambda state = self.trap.useRFMap.isChecked() : self.rfMapChanged(state))

        self.trap.update_rf.clicked.connect(lambda : self.update_rf())
        self.trap.update_dc.clicked.connect(lambda : self.update_dc())

        # Get the current state of the trap and set the gui
        #self.set_current_state()
        self.subLayout.addWidget(self.trap, 1, 1)

        self.setLayout(self.layout)


    @inlineCallbacks
    def freqChanged(self, freq, channel):
        yield self.server.set_frequency(freq, channel)
        self.trap.update_rf.setStyleSheet("background-color: red")

    @inlineCallbacks
    def phaseChanged(self, phase, channel):
        yield self.server.set_phase(phase, channel)
        self.trap.update_rf.setStyleSheet("background-color: red")

    @inlineCallbacks
    def ampChanged(self, amp, channel):
        yield self.server.set_amplitude(amp, channel)
        self.trap.update_rf.setStyleSheet("background-color: red")

    @inlineCallbacks
    def setAmpRFChanged(self, amp):
        index = np.where(self.rf_map[:,0] == amp)
        index = index[0][0]
        yield self.server.set_amplitude(amp,2)
        yield self.server.set_amplitude(self.rf_map[index,1],3)
        yield self.server.set_phase(self.rf_map[index,2],3)
        self.trap.update_rf.setStyleSheet("background-color: red")

    @inlineCallbacks
    def dcChanged(self, dc, channel):
        self.dc[str(len(self.dc) +1)] = [dc, channel]
        self.trap.update_dc.setStyleSheet("background-color: red")

    @inlineCallbacks
    def hvChanged(self, hv, channel):
        yield self.server.set_hv(hv, channel)

    @inlineCallbacks
    def endCapChanged(self, endCap, channel):
        self.endCap[str(len(self.endCap) +1)] = [endCap, channel]
        self.trap.update_rf.setStyleSheet("background-color: red")

    @inlineCallbacks
    def update_rf(self):
        yield self.server.update_rf()
        self.trap.update_rf.setStyleSheet("background-color: green")

    @inlineCallbacks
    def update_dc(self):
        for value in self.dc:
               yield self.server.set_dc_rod(self.dc[item][0], self.dc[item][1])
        for value in self.endCap:
               yield self.server.set_dc(self.endCap[item][0], self.endCap[item][1])
        self.trap.update_rf.setStyleSheet("background-color: green")

    @inlineCallbacks
    def rfMapChanged(self, state):
        if state == True:
            self.trap.spinAmp1.setEnabled(False)
            self.trap.spinAmp3.valueChanged.connect(lambda amp = self.trap.spinAmp3.value() : self.setAmpRFMap(amp))

        else:
            self.trap.spinAmp1.setEnabled(True)
            self.trap.spinAmp1.valueChanged.connect(lambda amp = self.trap.spinAmp1.value(), channel = self.rods['1'] : self.ampChanged(amp, channel))

    def closeEvent(self, x):
        self.reactor.stop()


    @inlineCallbacks
    def init_state(self):

        self.trap.spinFreq1.setValue(self.init_params['Frequency'][0])
        self.trap.spinFreq2.setValue(self.init_params['Frequency'][1])
        self.trap.spinFreq3.setValue(self.init_params['Frequency'][2])
        self.trap.spinFreq4.setValue(self.init_params['Frequency'][3])

        self.trap.spinPhase1.setValue(self.init_params['Phase'][0])
        self.trap.spinPhase2.setValue(self.init_params['Phase'][1])
        self.trap.spinPhase3.setValue(self.init_params['Phase'][2])
        self.trap.spinPhase4.setValue(self.init_params['Phase'][3])

        self.trap.spinAmp1.setValue(self.init_params['Voltage'][0])
        self.trap.spinAmp2.setValue(self.init_params['Voltage'][1])
        self.trap.spinAmp3.setValue(self.init_params['Voltage'][2])
        self.trap.spinAmp4.setValue(self.init_params['Voltage'][3])

        self.trap.spinDC1.setValue(self.init_params['DC'][0])
        self.trap.spinDC2.setValue(self.init_params['DC'][1])
        self.trap.spinDC3.setValue(self.init_params['DC'][2])
        self.trap.spinDC4.setValue(self.init_params['DC'][3])

        self.trap.spinHV1.setValue(self.init_params['HV'][0])
        self.trap.spinHV2.setValue(self.init_params['HV'][1])
        self.trap.spinHV3.setValue(self.init_params['HV'][2])
        self.trap.spinHV4.setValue(self.init_params['HV'][3])

        self.trap.spinEndCap1.setValue(self.init_params['endCap'][0])
        self.trap.spinEndCap2.setValue(self.init_params['endCap'][1])

        self.trap.spinEndCap1.setValue(self.init_params['eLens'][0])
        self.trap.spinEndCap2.setValue(self.init_params['eLens'][1])

        self.trap.useRFMap.setCheckState(False)

        self.server.update_rf()
        self.server.update_dc()

if __name__ == "__main__":
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    TrapWidget = TrapControlClient(reactor)
    TrapWidget.show()
    reactor.run()
