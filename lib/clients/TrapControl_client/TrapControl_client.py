from barium.lib.clients.gui.TrapControl_gui import QCustomTrapGui
from barium.lib.clients.gui.Ablation_gui import QCustomAblationGui
from barium.lib.clients.gui.HVPulse_gui import QCustomHVPulseGui
from barium.lib.clients.gui.ARamp_gui import QCustomARampGui
from barium.lib.clients.HP6033A_client.HP6033Aclient import HP6033A_Client
from common.lib.clients.qtui.q_custom_text_changing_button import \
    TextChangingButton

from twisted.internet.defer import inlineCallbacks, returnValue
from PyQt4 import QtGui
#try:
from config.TrapControl_config import TrapControl_config
#except:
#    from barium.lib.config.TrapControl_config import TrapControl_config
import time
import socket
import os
import numpy as np
#from keysight import command_expert as kt

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
        """Creates an Asynchronous connection to the trap control computer and
        connects incoming signals to relevant functions

        """
        self.serverIP = TrapControl_config.ip
        self.dc_IP = TrapControl_config.dc_ip

        from labrad.wrappers import connectAsync
        # connect to manager with motion control board
        self.cxn = yield connectAsync(self.serverIP,
                                      name=self.name,
                                      password=self.password)
        
        #self.tof = yield self.cxn.tof_server
        self.server = yield self.cxn.trapserver

        # connect to pc with piezo box for rod dc
        self.cxn_dc = yield connectAsync(self.dc_IP,
                                      name=self.name,
                                      password=self.password)
        
        self.piezo = yield self.cxn_dc.piezo_controller

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
        self.rf_map = np.loadtxt('C:/Users/barium133/Code/barium/lib/clients/TrapControl_client/rf_map.txt')

        # Get channel numbers for each electrode
        self.rods = TrapControl_config.rods
        self.dc_rods = TrapControl_config.dc_rods
        self.endCaps = TrapControl_config.endCaps
        self.eLens = TrapControl_config.eLens
        self.setWindowTitle('Trap Control')

        # Create widgets and lay them out.
        # Create general lock button to disable all buttons
        self.lockSwitch = TextChangingButton(('Locked','Unlocked'))
        # Start Unlocked
        self.lockSwitch.toggled.connect(self.set_lock)
        self.subLayout.addWidget(self.lockSwitch, 0, 4, 1, 2)
        #self.lockSwitch.setChecked(False)

        # Create a button to initialize trap params
        self.init_trap = QtGui.QPushButton('Set Default Values')
        self.init_trap.setMaximumHeight(30)
        self.init_trap.setFont(QtGui.QFont('MS Shell Dlg 2', pointSize=12))
        self.init_trap.clicked.connect(lambda : self.init_state())
        self.subLayout.addWidget(self.init_trap, 0, 0, 1, 2)

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

        # Right now the piezo box hardwarw was modified to be 0-5 V
        # but the software still thinks it's 0-150 V
        # map our 0-5 to 0-150
  
        #init_dc1 = yield self.server.get_dc_rod(self.rods['1'])
        init_dc1 = yield self.piezo.get_voltage(self.dc_rods['1'])
        init_dc1 = init_dc1/150.*5
        self.trap.spinDC1.setValue(init_dc1)
        self.trap.spinDC1.valueChanged.connect(lambda dc = self.trap.spinDC1.value(), channel = self.dc_rods['1'] : self.dcChanged(dc, channel))
        #init_dc2 = yield self.server.get_dc_rod(self.rods['2'])
        init_dc2 = yield self.piezo.get_voltage(self.dc_rods['2'])
        init_dc2 = init_dc2/150.*5
        self.trap.spinDC2.setValue(init_dc2)
        self.trap.spinDC2.valueChanged.connect(lambda dc = self.trap.spinDC2.value(), channel = self.dc_rods['2'] : self.dcChanged(dc, channel))
        #init_dc3 = yield self.server.get_dc_rod(self.rods['3'])
        init_dc3 = yield self.piezo.get_voltage(self.dc_rods['3'])
        init_dc3 = init_dc3/150.*5
        self.trap.spinDC3.setValue(init_dc3)
        self.trap.spinDC3.valueChanged.connect(lambda dc = self.trap.spinDC3.value(), channel = self.dc_rods['3'] : self.dcChanged(dc, channel))
        #init_dc4 = yield self.server.get_dc_rod(self.rods['4'])
        init_dc4 = yield self.piezo.get_voltage(self.dc_rods['4'])
        init_dc4 = init_dc4/150.*5
        self.trap.spinDC4.setValue(init_dc4)
        self.trap.spinDC4.valueChanged.connect(lambda dc = self.trap.spinDC4.value(), channel = self.dc_rods['4'] : self.dcChanged(dc, channel))
        init_hv1 = yield self.server.get_hv(self.rods['1'])
        self.trap.spinHV1.setValue(init_hv1)
        self.trap.spinHV1.valueChanged.connect(lambda hv = self.trap.spinHV1.value(), channel = self.rods['1'] : self.hvChanged(hv, channel))
        init_hv2 = yield self.server.get_hv(self.rods['2'])
        self.trap.spinHV2.setValue(init_hv2)
        self.trap.spinHV2.valueChanged.connect(lambda hv = self.trap.spinHV2.value(), channel = self.rods['2'] : self.hvChanged(hv, channel))
        init_hv3 = yield self.server.get_hv(self.rods['3'])
        self.trap.spinHV3.setValue(init_hv3)
        self.trap.spinHV3.valueChanged.connect(lambda hv = self.trap.spinHV3.value(), channel = self.rods['3'] : self.hvChanged(hv, channel))
        init_hv4 = yield self.server.get_hv(4)
        self.trap.spinHV4.setValue(init_hv4)
        self.trap.spinHV4.valueChanged.connect(lambda hv = self.trap.spinHV4.value(), channel = 4 : self.hvChanged(hv, channel))

        init_ec1 = yield self.server.get_dc(self.endCaps['1'])
        self.trap.spinEndCap1.setValue(init_ec1)
        self.trap.spinEndCap1.valueChanged.connect(lambda voltage = self.trap.spinEndCap1.value(), channel = self.endCaps['1'] : self.endCapChanged(voltage, channel))
        init_ec2 = yield self.server.get_dc(self.endCaps['2'])
        self.trap.spinEndCap2.setValue(init_ec2)
        self.trap.spinEndCap2.valueChanged.connect(lambda voltage = self.trap.spinEndCap2.value(), channel = self.endCaps['2'] : self.endCapChanged(voltage, channel))

        init_eL1 = yield self.server.get_hv(self.eLens['1'])
        self.trap.E1Spin.setValue(init_eL1)
        self.trap.E1Spin.valueChanged.connect(lambda voltage = self.trap.E1Spin.value(), channel = self.eLens['1'] : self.hvChanged(voltage, channel))
        init_eL2 = yield self.server.get_hv(self.eLens['2'])
        self.trap.E2Spin.setValue(init_eL2)
        self.trap.E2Spin.valueChanged.connect(lambda voltage = self.trap.E2Spin.value(), channel = self.eLens['2'] : self.hvChanged(voltage, channel))


        init_rf = yield self.server.get_rf_map_state()
        self.trap.useRFMap.setCheckState(init_rf)
        self.trap.useRFMap.stateChanged.connect(lambda state = self.trap.useRFMap.isChecked() : self.rfMapChanged(state))

        init_rf_en = yield self.server.get_rf_state()
        self.trap.enableRF.setCheckState(init_rf_en)
        self.trap.enableRF.stateChanged.connect(lambda state = self.trap.enableRF.isChecked() : self.enableRFChanged(state))

        init_bat = yield self.server.get_battery_charging()
        self.trap.setCharging.setCheckState(init_bat)
        self.trap.setCharging.stateChanged.connect(lambda state = self.trap.setCharging.isChecked() : self.chargingChanged(state))


        self.trap.update_rf.clicked.connect(lambda : self.update_rf())
        self.trap.update_dc.clicked.connect(lambda : self.update_dc())
        self.trap.clearPhase.clicked.connect(lambda : self.clear_phase())

        # Get the current state of the trap and set the gui
        #self.set_current_state()
        self.subLayout.addWidget(self.trap, 1, 0, 1, 6)

        self.ablation = QCustomAblationGui()
        self.ablation.loading_time_spin.valueChanged.connect(lambda time = self.ablation.loading_time_spin.value() : self.delayChanged(time))
        self.ablation.loading_time_spin.setValue(self.init_params['Loading Time'])
        self.ablation.trigger_loading.clicked.connect(lambda : self.triggerLoading())

        self.subLayout.addWidget(self.ablation, 2, 0, 1, 2)

        # HV Gui
        '''
        self.hvGUI = QCustomHVPulseGui()
        self.hvGUI.hv_pulse.clicked.connect(lambda : self.hv_pulse())
        self.hvGUI.hv_graph.clicked.connect(lambda : self.hv_graph())

        self.subLayout.addWidget(self.hvGUI, 2, 5, 1, 1)
        '''
        # Add current controler
        #self.HP = HP6033A_Client(self.reactor)
        #self.HP.self_connect('bender',"HP6033A Client",0)

        #self.subLayout.addWidget(self.HP, 2, 2, 1, 2)

        self.ARampGUI = QCustomARampGui()
        self.ARampGUI.ARamp.clicked.connect(lambda: self.a_ramp())

        self.subLayout.addWidget(self.ARampGUI, 2, 4, 1, 1)

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
    def delayChanged(self, time):
        yield self.server.set_loading_time(172, int(time))

    @inlineCallbacks
    def chargingChanged(self, state):
        if state >= 1:
            yield self.server.set_battery_charging(True)
        else:
            yield self.server.set_battery_charging(False)


    @inlineCallbacks
    def triggerLoading(self):
        yield self.server.trigger_loading()

    @inlineCallbacks
    def setAmpRFMap(self, amp):
        index = np.where(self.rf_map[:,0] == amp)
        index = index[0][0]
        yield self.server.set_amplitude(self.rf_map[index,0],self.rods['3'])
        #self.trap.spinAmp3.setValue(self.rf_map[index,0])
        self.trap.spinPhase1.setValue(self.rf_map[index,2])
        self.trap.spinAmp1.setValue(self.rf_map[index,1])
        self.trap.update_rf.setStyleSheet("background-color: red")

    def dcChanged(self, dc, channel):
        self.dc[str(len(self.dc) +1)] = [dc, channel]
        self.trap.update_dc.setStyleSheet("background-color: red")

    @inlineCallbacks
    def hvChanged(self, hv, channel):
        yield self.server.set_hv(hv, channel)

    @inlineCallbacks
    def hv_pulse(self):
        kt.run_sequence('C:/Users/barium133/Code/barium/lib/scripts/Oscilloscope/set_run')
        yield self.server.trigger_hv_pulse()

    @inlineCallbacks
    def hv_graph(self):
        kt.run_sequence('C:/Users/barium133/Code/barium/lib/scripts/Oscilloscope/set_single')
        yield self.server.trigger_hv_pulse()
        yield self.tof.get_trace()


    def endCapChanged(self, endCap, channel):
        self.endCap[str(len(self.endCap) +1)] = [endCap, channel]
        self.trap.update_dc.setStyleSheet("background-color: red")

    @inlineCallbacks
    def update_rf(self):
        yield self.server.update_rf()
        self.trap.update_rf.setStyleSheet("background-color: green")

    @inlineCallbacks
    def update_dc(self):
        from labrad.units import WithUnit as U
        for key in self.dc:
            # use below for motion dc
            #yield self.server.set_dc_rod(self.dc[key][0], self.dc[key][1])
            
            # Right now the piezo box hardwarw was modified to be 0-5 V
            # but the software still thinks it's 0-150 V
            # map our 0-5 to 0-150
            voltage = U(self.dc[key][0]/5*150,'V')
            yield self.piezo.set_voltage(self.dc[key][1],voltage)
            self.trap.update_dc.setStyleSheet("background-color: green")
        self.dc = {}
        for key in self.endCap:
            yield self.server.set_dc(self.endCap[key][0], self.endCap[key][1])
            self.trap.update_dc.setStyleSheet("background-color: green")
        self.endCap = {}

    @inlineCallbacks
    def clear_phase(self):
        yield self.server.clear_phase_accumulator()

    @inlineCallbacks
    def rfMapChanged(self, state):
        if state >= 1:
            self.trap.spinAmp1.setEnabled(False)
            self.trap.spinPhase1.setEnabled(False)
            self.trap.spinAmp3.valueChanged.disconnect()
            self.trap.spinAmp3.valueChanged.connect(lambda amp = self.trap.spinAmp3.value() : self.setAmpRFMap(amp))
            yield self.server.set_rf_map_state(True)

        elif state == 0:
            self.trap.spinAmp1.setEnabled(True)
            self.trap.spinPhase1.setEnabled(True)
            self.trap.spinAmp3.valueChanged.disconnect()
            self.trap.spinAmp3.valueChanged.connect(lambda amp = self.trap.spinAmp3.value(), channel = self.rods['3'] : self.ampChanged(amp, channel))
            yield self.server.set_rf_map_state(False)

    @inlineCallbacks
    def enableRFChanged(self, state):
        if state >= 1:
            yield self.server.set_rf_state(True)
        else:
            yield self.server.set_rf_state(False)

    def set_lock(self, state):
        self.trap.setEnabled(not state)
        self.init_trap.setEnabled(not state)

    def closeEvent(self, x):
        self.reactor.stop()


    #@inlineCallbacks
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

        self.trap.E1Spin.setValue(self.init_params['eLens'][0])
        self.trap.E2Spin.setValue(self.init_params['eLens'][1])

        self.trap.useRFMap.setCheckState(False)

        self.piezo.set_output_state(self.dc_rods['1'],True)
        self.piezo.set_output_state(self.dc_rods['2'],True)
        self.piezo.set_output_state(self.dc_rods['3'],True)
        self.piezo.set_output_state(self.dc_rods['4'],True)
        self.piezo.set_remote_state(True)

    @inlineCallbacks
    def a_ramp(self):
        from labrad.units import WithUnit as U
        #Get current settings
        oldRod1 = self.trap.spinDC1.value()
        oldRod2 = self.trap.spinDC2.value()
        oldRod3 = self.trap.spinDC3.value()
        oldRod4 = self.trap.spinDC4.value()

        # Get a-ramp settings
        a1 = self.ARampGUI.spinDC1.value()
        a2 = self.ARampGUI.spinDC2.value()
        a3 = self.ARampGUI.spinDC3.value()
        a4 = self.ARampGUI.spinDC4.value()



        self.ARampGUI.ARamp.setStyleSheet("background-color: red")
        # Add the a-ramp
        # using the pizeo box now
        v1 = U((oldRod1 + a1)/5*150,'V')
        v2 = U((oldRod2 + a2)/5*150,'V')
        v3 = U((oldRod3 + a3)/5*150,'V')
        v4 = U((oldRod4 + a4)/5*150,'V')
        
        
        
        yield self.piezo.set_voltage(self.dc_rods['1'],v1)
        yield self.piezo.set_voltage(self.dc_rods['2'],v2)
        yield self.piezo.set_voltage(self.dc_rods['3'],v3)
        yield self.piezo.set_voltage(self.dc_rods['4'],v4)
        
        '''
        yield self.server.set_dc_rod(oldRod1+a1, self.rods['1'])
        yield self.server.set_dc_rod(oldRod2+a2, self.rods['2'])
        yield self.server.set_dc_rod(oldRod3+a3, self.rods['3'])
        yield self.server.set_dc_rod(oldRod4+a4, self.rods['4'])
        '''
        
        yield time.sleep(int(self.ARampGUI.waitTime.value()))

        # Return to current settings
        v1 = U((oldRod1)/5*150,'V')
        v2 = U((oldRod2)/5*150,'V')
        v3 = U((oldRod3)/5*150,'V')
        v4 = U((oldRod4)/5*150,'V')
        
        
        yield self.piezo.set_voltage(self.dc_rods['1'],v1)
        yield self.piezo.set_voltage(self.dc_rods['2'],v2)
        yield self.piezo.set_voltage(self.dc_rods['3'],v3)
        yield self.piezo.set_voltage(self.dc_rods['4'],v4)
        
        '''
        yield self.server.set_dc_rod(oldRod1, self.rods['1'])
        yield self.server.set_dc_rod(oldRod2, self.rods['2'])
        yield self.server.set_dc_rod(oldRod3, self.rods['3'])
        yield self.server.set_dc_rod(oldRod4, self.rods['4'])
        '''
        
        self.ARampGUI.ARamp.setStyleSheet("background-color: green")

if __name__ == "__main__":
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    TrapWidget = TrapControlClient(reactor)
    TrapWidget.show()
    reactor.run()
