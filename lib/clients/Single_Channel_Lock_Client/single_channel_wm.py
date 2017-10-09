#!/usr/bin/env python
#-*- coding:utf-8 -*-

from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks, returnValue
import socket
import os
from config.multiplexerclient_config import multiplexer_config
from common.lib.clients.qtui.q_custom_text_changing_button import \
    TextChangingButton
from common.lib.clients.qtui.QCustomSlideIndicator import SlideIndicator

SIGNALID1 = 445567


class single_channel_wm(QtGui.QWidget):
    def __init__(self, reactor, parent=None):
        super(single_channel_wm, self).__init__()
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.reactor = reactor
        self.connect()

    @inlineCallbacks
    def connect(self):
        """Creates an Asynchronous connection to the wavemeter computer and
        connects incoming signals to relavent functions
        """
        from labrad.wrappers import connectAsync
        self.password = os.environ['LABRADPASSWORD']
        self.wm_cxn = yield connectAsync(multiplexer_config.ip, name = socket.gethostname() + ' Single Channel Lock', password=self.password)
        self.wm = yield self.wm_cxn.multiplexerserver
        self.cxn = yield connectAsync('bender', name = socket.gethostname() + ' Single Channel Lock', password=self.password)
        self.lock_server = yield self.cxn.single_channel_lock_server
        yield self.wm.signal__frequency_changed(SIGNALID1)
        yield self.wm.addListener(listener = self.updateFrequency, source = None, ID = SIGNALID1)
        self.initializeGUI()

    @inlineCallbacks
    def initializeGUI(self):
        layout = QtGui.QGridLayout()
        qBox = QtGui.QGroupBox('Single Channel Software Lock')
        subLayout = QtGui.QGridLayout()
        qBox.setLayout(subLayout)
        layout.addWidget(qBox, 0, 0), returnValue
        self.centralwidget = QtGui.QWidget(self)
        self.wavelength = QtGui.QLabel('freq')
        self.wavelength.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=70))
        self.wavelength.setAlignment(QtCore.Qt.AlignCenter)
        self.wavelength.setStyleSheet('color: blue')
        subLayout.addWidget(self.wavelength, 1,0, 7, 2)
        shell_font = 'MS Shell Dlg 2'

        # Create lock button
        self.lockSwitch = TextChangingButton(('Locked','Unlocked'))
        self.lockSwitch.toggled.connect(self.set_lock)
        subLayout.addWidget(self.lockSwitch, 1, 3, 1, 1)

        #frequency switch label
        lockName = QtGui.QLabel('Lock Frequency')
        lockName.setFont(QtGui.QFont(shell_font, pointSize=16))
        lockName.setAlignment(QtCore.Qt.AlignCenter)
        subLayout.addWidget(lockName, 8, 0, 1, 1)

        # frequency
        self.spinFreq1 = QtGui.QDoubleSpinBox()
        self.spinFreq1.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinFreq1.setDecimals(6)
        self.spinFreq1.setSingleStep(1e-6)
        self.spinFreq1.setRange(0, 1e4)
        self.spinFreq1.setKeyboardTracking(False)

        subLayout.addWidget(self.spinFreq1, 9, 0, 1, 1)

        init_freq1 = yield self.lock_server.get_lock_frequency()
        self.spinFreq1.setValue(init_freq1)
        self.spinFreq1.valueChanged.connect(lambda freq = self.spinFreq1.value(), \
                                            : self.freqChanged(freq))

        #exposure label
        exposureName = QtGui.QLabel('Exposure')
        exposureName.setFont(QtGui.QFont(shell_font, pointSize=16))
        exposureName.setAlignment(QtCore.Qt.AlignCenter)
        subLayout.addWidget(exposureName, 8, 1, 1, 1)

        # exposure
        self.spinExposure = QtGui.QDoubleSpinBox()
        self.spinExposure.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinExposure.setDecimals(0)
        self.spinExposure.setSingleStep(1)
        self.spinExposure.setRange(0, 2000)
        self.spinExposure.setKeyboardTracking(False)

        subLayout.addWidget(self.spinExposure, 9, 1, 1, 1)

        init_exp = yield self.wm.get_exposure(multiplexer_config.info['455nm'][0])
        self.spinExposure.setValue(init_exp)
        self.spinExposure.valueChanged.connect(lambda exp = self.spinExposure.value(), \
                                            : self.expChanged(exp))


        #gain  label
        gainName = QtGui.QLabel('Gain (V/MHz)')
        gainName.setFont(QtGui.QFont(shell_font, pointSize=16))
        gainName.setAlignment(QtCore.Qt.AlignCenter)
        subLayout.addWidget(gainName, 2, 3, 1, 1)

        # frequency
        self.spinGain = QtGui.QDoubleSpinBox()
        self.spinGain.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinGain.setDecimals(3)
        self.spinGain.setSingleStep(1e-3)
        self.spinGain.setRange(1e-3, 1)
        self.spinGain.setKeyboardTracking(False)
        subLayout.addWidget(self.spinGain, 3, 3, 1, 1)

        init_gain = yield self.lock_server.get_gain()
        self.spinGain.setValue(init_gain)
        self.spinGain.valueChanged.connect(lambda gain = self.spinGain.value(), \
                                            : self.gainChanged(gain))

        #rails  label
        lowRail = QtGui.QLabel('Low Rail')
        lowRail.setFont(QtGui.QFont(shell_font, pointSize=16))
        lowRail.setAlignment(QtCore.Qt.AlignCenter)
        subLayout.addWidget(lowRail, 4, 3, 1, 1)

        # low rail
        self.spinLowRail = QtGui.QDoubleSpinBox()
        self.spinLowRail.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinLowRail.setDecimals(0)
        self.spinLowRail.setSingleStep(1)
        self.spinLowRail.setRange(0 , 50)
        self.spinLowRail.setKeyboardTracking(False)
        subLayout.addWidget(self.spinLowRail, 5, 3, 1, 1)

        init_rails = yield self.lock_server.get_rails()
        self.spinLowRail.setValue(init_rails[0])
        self.spinLowRail.valueChanged.connect(lambda : self.railsChanged())

        #high rails  label
        highRail = QtGui.QLabel('High Rail')
        highRail.setFont(QtGui.QFont(shell_font, pointSize=16))
        highRail.setAlignment(QtCore.Qt.AlignCenter)
        subLayout.addWidget(highRail, 6, 3, 1, 1)

        # high rail
        self.spinHighRail = QtGui.QDoubleSpinBox()
        self.spinHighRail.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinHighRail.setDecimals(0)
        self.spinHighRail.setSingleStep(1)
        self.spinHighRail.setRange(0 , 50)
        self.spinHighRail.setKeyboardTracking(False)
        subLayout.addWidget(self.spinHighRail, 7, 3, 1, 1)

        init_rails = yield self.lock_server.get_rails()
        self.spinHighRail.setValue(init_rails[1])
        self.spinHighRail.valueChanged.connect(lambda : self.railsChanged())

        # Too lazy to add signals to the server so
        # will update and display dac voltage every time
        # frequency updates
        self.dacLabel = QtGui.QLabel('Dac Voltage')
        self.dacLabel.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=30))
        self.dacLabel.setAlignment(QtCore.Qt.AlignCenter)
        subLayout.addWidget(self.dacLabel, 8,3, 1, 1)

        self.dacVoltage = QtGui.QLabel('0.0')
        self.dacVoltage.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=30))
        self.dacVoltage.setAlignment(QtCore.Qt.AlignCenter)
        subLayout.addWidget(self.dacVoltage, 9,3, 1, 1)

        self.setLayout(layout)


    @inlineCallbacks
    def freqChanged(self, freq):
        yield self.lock_server.set_point(freq)

    @inlineCallbacks
    def expChanged(self, exp):
        yield self.wm.set_exposure_time(multiplexer_config.info['455nm'][0],int(exp))

    @inlineCallbacks
    def gainChanged(self, gain):
        yield self.lock_server.set_gain(gain)

    @inlineCallbacks
    def railsChanged(self):
        yield self.lock_server.set_low_rail(self.spinLowRail.value())
        yield self.lock_server.set_high_rail(self.spinHighRail.value())

    @inlineCallbacks
    def updateFrequency(self, c, signal):
        if signal[0] == multiplexer_config.info['455nm'][0]:
            self.wavelength.setText(str(signal[1])[0:10])
            voltage = yield self.lock_server.get_dac_voltage()
            self.dacVoltage.setText(str(voltage))

    def set_lock(self, state):
        self.lock_server.toggle(state)


if __name__ == "__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    single_chan_Widget = single_channel_wm(reactor)
    single_chan_Widget.show()
    reactor.run()
