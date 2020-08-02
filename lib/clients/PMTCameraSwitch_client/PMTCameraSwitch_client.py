from twisted.internet.defer import inlineCallbacks, returnValue
from PyQt4 import QtGui
from common.lib.clients.PMT_Control.PMT_CONTROL import pmtWidget
from common.lib.clients.Pulser2_DDS.DDS_CONTROL import DDS_CONTROL
from barium.lib.clients.ProtectionBeam_client.protectionBeamClient import protectionBeamClient
from barium.lib.clients.Shutter_client.shutterClient import shutterclient


import socket
import os
import numpy as np




class PMTCameraSwitchClient(QtGui.QWidget):

    def __init__(self, reactor, parent=None):
        """initializels the GUI creates the reactor

        """
        super(PMTCameraSwitchClient, self).__init__()
        self.password = os.environ['LABRADPASSWORD']
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.reactor = reactor
        self.name = socket.gethostname() + ' PMT Camera Switch Client'
        self.connect()

    @inlineCallbacks
    def connect(self):
        """Creates an Asynchronous connection to the trap control computer and
        connects incoming signals to relevant functions

        """
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync(
                                      name=self.name,
                                      password=self.password)

        self.server = yield self.cxn.pulser
        self.initializeGUI()

    #@inlineCallbacks
    def initializeGUI(self):

        # initialize main Gui
        self.layout = QtGui.QGridLayout()
        self.qBox = QtGui.QGroupBox('Switches')
        self.subLayout = QtGui.QGridLayout()
        self.qBox.setLayout(self.subLayout)
        self.layout.addWidget(self.qBox, 0, 0)

        # Add PMT control
        pmt = pmtWidget(self.reactor)
        self.subLayout.addWidget(pmt, 0,0, 1, 2)

        # Add camera switch
        self.cam_switch = QtGui.QPushButton('PMT/Camera')
        self.cam_switch.setMinimumHeight(100)
        self.cam_switch.setMinimumWidth(100)
        self.cam_switch.setMaximumWidth(100)
        self.cam_switch.clicked.connect(self.switchCamera)
        self.subLayout.addWidget(self.cam_switch, 1,0)

        # Add 614 RF Switch
        self.led_switch = QtGui.QPushButton('614 TTL')
        self.led_switch.setMinimumHeight(100)
        self.led_switch.setMinimumWidth(100)
        self.led_switch.setMaximumWidth(100)
        self.led_switch.setCheckable(True)
        self.led_switch.toggled.connect(lambda  state = self.led_switch.isDown() , chan = 'TTL8',\
                                         :self.switchState(state, chan))
        self.subLayout.addWidget(self.led_switch, 1,1)

        # Add 455 RF Switch
        self.shelve_switch = QtGui.QPushButton('455 TTL')
        self.shelve_switch.setMinimumHeight(100)
        self.shelve_switch.setMinimumWidth(100)
        self.shelve_switch.setMaximumWidth(100)
        self.shelve_switch.setCheckable(True)
        self.shelve_switch.toggled.connect(lambda  state = self.shelve_switch.isDown() , chan = 'TTL7',\
                                         :self.switchState(state, chan))

        self.subLayout.addWidget(self.shelve_switch, 2,0)

        # Add 614 EOM Switch
        self.eom_switch = QtGui.QPushButton('1762 EOM TTL')
        self.eom_switch.setMinimumHeight(100)
        self.eom_switch.setMinimumWidth(126)
        self.eom_switch.setMaximumWidth(145)
        self.eom_switch.setCheckable(True)
        self.eom_switch.toggled.connect(lambda  state = self.eom_switch.isDown() , chan = 'TTL9',\
                                         :self.switchState(state, chan))

        self.subLayout.addWidget(self.eom_switch, 2,1)




        # Add Protection Beam Control
        prot = protectionBeamClient(self.reactor)
        self.subLayout.addWidget(prot ,3,0,1,2)

        # Add shutter control
        shutters = shutterclient(self.reactor)
        self.subLayout.addWidget(shutters,0,2)

        # Add DDS Controls
        dds = DDS_CONTROL(self.reactor)
        self.subLayout.addWidget(dds,1,2,3,1)

        self.setLayout(self.layout)


    @inlineCallbacks
    def switchCamera(self,state):
        yield self.server.switch_auto('PMT/Camera', True)
        yield self.server.switch_auto('PMT/Camera', False)

    @inlineCallbacks
    def switchState(self,state, chan):
        yield self.server.switch_auto(chan, state)


if __name__ == "__main__":
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    PMTCameraWidget = PMTCameraSwitchClient(reactor)
    PMTCameraWidget.show()
    reactor.run()
