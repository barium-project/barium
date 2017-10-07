from barium.lib.clients.gui.shutter import QCustomSwitchChannel
from twisted.internet.defer import inlineCallbacks
from common.lib.clients.connection import connection
from PyQt4 import QtGui, QtCore
import os,socket
import time
from config.shutter_client_config import shutter_config


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
        self.threshold = 1000
        self.protection_state = False

    @inlineCallbacks
    def connect(self):

        if self.cxn is None:
            self.cxn = connection(name="Protection Beam Client")
            yield self.cxn.connect()

        self.arduino = yield self.cxn.get_server('arduinottl')
        self.pmt = yield self.cxn.get_server('normalpmtflow')

        self.chaninfo = shutter_config.info
        self.initializeGUI()

    @inlineCallbacks
    def initializeGUI(self):

        layout = QtGui.QGridLayout()

        qBox = QtGui.QGroupBox('Laser Shutters')
        subLayout = QtGui.QGridLayout()
        qBox.setLayout(subLayout)
        layout.addWidget(qBox, 0, 0)

        for chan in self.chaninfo:
            if 'Protection Beam' == chan:
                self.port = self.chaninfo[chan][0]
                position = self.chaninfo[chan][1]
                self.inverted = self.chaninfo[chan][2]
                self.enable = self.chaninfo[chan][3]

                self.widget = QCustomSwitchChannel(chan, ('Closed', 'Open'))
                self.widget.TTLswitch.setChecked(False)
                self.widget.TTLswitch.toggled.connect(lambda state=self.widget.TTLswitch.isDown(),
                                             port = self.port, chan=chan, inverted= self.inverted:
                                             self.changeState(state, port, chan, inverted))

                self.widget.enableSwitch.clicked.connect(lambda state=self.widget.enableSwitch.isChecked(),
                                             port=self.enable, chan=chan, inverted=self.inverted:
                                             self.enableState(state, port, chan, inverted))

                self.d[self.port] = self.widget
                subLayout.addWidget(self.d[self.port], position[0], position[1])



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
        self.spinThreshold.setValue(self.threshold)

        self.enableProtection = QtGui.QCheckBox('Enable Protection')
        self.enableProtection.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=16))

        init  = yield self.arduino.ttl_read(self.enable)

        self.enableProtection.setCheckState(init)

        layout.addWidget(self.spinThreshold, 3,0)
        layout.addWidget(thresholdName, 2,0)
        layout.addWidget(self.enableProtection, 1,0)


        ### Connect to functions
        self.spinThreshold.valueChanged.connect(self.thresholdChanged)
        self.enableProtection.clicked.connect(self.protection)
        from twisted.internet.reactor import callLater
        self.setLayout(layout)
        self.protectionLoop()
        yield None

    @inlineCallbacks
    def changeState(self, state, port, chan, inverted):
        if inverted:
            state = not state
        yield self.arduino.ttl_output(port, state)

    @inlineCallbacks
    def enableState(self, state, port, chan, inverted):
        yield self.arduino.ttl_output(port, state)

    def thresholdChanged(self, threshold):
        self.threshold = threshold

    def protection(self, state):
        self.protection_state = bool(state)

    @inlineCallbacks
    def protectionLoop(self):
        running = yield self.pmt.isrunning()
        if self.protection_state and running:
            counts = yield self.pmt.get_next_counts('ON',1)
            if counts < self.threshold:
                if self.inverted:
                    self.widget.TTLswitch.setChecked(True)

                else:
                    #self.arduino.ttl_output(self.port,True)
                    self.widget.TTLswitch.setChecked(False)
            '''
            else:
                if self.inverted:
                    self.widget.TTLswitch.setChecked(False)
                else:
                    self.widget.TTLswitch.setChecked(True)
                    print 'greater'
            '''
        self.reactor.callLater(.1, self.protectionLoop)


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
