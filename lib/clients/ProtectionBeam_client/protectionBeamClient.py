from barium.lib.clients.gui.shutter import QCustomSwitchChannel
from twisted.internet.defer import inlineCallbacks
from common.lib.clients.connection import connection
from PyQt4 import QtGui, QtCore
import os,socket
import time


class protectionBeamClient(QtGui.QFrame):

    def __init__(self, reactor, cxn=None):
        """initializes the GUI creates the reactor
            and empty dictionary for channel widgets to
            be stored for iteration. also grabs chan info
            from switch_config file
        """
        super(protectionBeamClient, self).__init__()
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.setFrameStyle(QtGui.QFrame.Panel  | QtGui.QFrame.Sunken)
        self.reactor = reactor
        self.cxn = cxn
        self.d = {}
        self.connect()
        self.threshold = 0.0
        self.protection_state = False

    @inlineCallbacks
    def connect(self):

        from labrad.wrappers import connectAsync

        self.cxn = yield connectAsync()
        self.server = self.cxn.protectionbeamserver
        self.initializeGUI()

    @inlineCallbacks
    def initializeGUI(self):

        layout = QtGui.QGridLayout()

        qBox = QtGui.QGroupBox('Laser Shutters')
        subLayout = QtGui.QGridLayout()
        qBox.setLayout(subLayout)
        layout.addWidget(qBox, 0, 0)



        self.widget = QCustomSwitchChannel('Protection Beam', ('Open', 'Closed'))
        self.widget.TTLswitch.setChecked(False)
        self.widget.TTLswitch.toggled.connect(lambda state=self.widget.TTLswitch.isDown() : self.changeState(state))
        self.widget.enableSwitch.clicked.connect(lambda state=self.widget.enableSwitch.isChecked():self.enableShutter(state))

        init_state = yield self.server.get_shutter_enabled()
        self.widget.enableSwitch.setCheckState(init_state)
        subLayout.addWidget(self.widget, 0, 0)



        ### Add a button to change to protection mode and a spin box to set pmt threshold
        shell_font = 'MS Shell Dlg 2'
        thresholdName = QtGui.QLabel('Threshold PMT Counts (kcounts/sec)')
        thresholdName.setFont(QtGui.QFont(shell_font, pointSize=14))
        thresholdName.setAlignment(QtCore.Qt.AlignCenter)

        self.spinThreshold = QtGui.QDoubleSpinBox()
        self.spinThreshold.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.spinThreshold.setDecimals(1)
        self.spinThreshold.setSingleStep(1)
        self.spinThreshold.setRange(0, 500e6)
        self.spinThreshold.setKeyboardTracking(False)

        self.threshold = yield self.server.get_threshold()
        self.spinThreshold.setValue(self.threshold)

        self.enableProtection = QtGui.QCheckBox('Enable Protection')
        self.enableProtection.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=16))

        init_state = yield self.server.get_protection_enabled()
        self.enableProtection.setCheckState(init_state)

        layout.addWidget(self.spinThreshold, 3,0)
        layout.addWidget(thresholdName, 2,0)
        layout.addWidget(self.enableProtection, 1,0)


        ### Connect to functions
        self.spinThreshold.valueChanged.connect(self.thresholdChanged)
        self.enableProtection.clicked.connect(self.protection)

        self.setLayout(layout)

    @inlineCallbacks
    def changeState(self, state):
        yield self.server.change_shutter_state(state)

    @inlineCallbacks
    def enableShutter(self, state):
        yield self.server.enable_protection_shutter(state)

    @inlineCallbacks
    def thresholdChanged(self, threshold):
        yield self.server.set_threshold(threshold)

    @inlineCallbacks
    def protection(self, state):
        yield self.server.set_protection_enabled(state)


    def closeEvent(self, x):
        self.reactor.stop()


if __name__ == "__main__":
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    protectionBeamClient = protectionBeamClient(reactor)
    protectionBeamClient.show()
    reactor.run()
