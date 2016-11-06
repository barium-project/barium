from twisted.internet.defer import inlineCallbacks, returnValue
from PyQt4 import QtGui


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
        self.cxn = yield connectAsync('bender',
                                      name=self.name,
                                      password=self.password)

        self.server = yield self.cxn.pulser
        self.initializeGUI()

    #@inlineCallbacks
    def initializeGUI(self):

        self.layout = QtGui.QGridLayout()
        self.qBox = QtGui.QGroupBox('PMT/Camera Switch')
        self.subLayout = QtGui.QGridLayout()
        self.qBox.setLayout(self.subLayout)
        self.layout.addWidget(self.qBox, 0, 0)

        # initialize main Gui
        self.switch = QtGui.QPushButton('PMT/Camera')

        self.switch.clicked.connect(self.switchState)


        self.subLayout.addWidget(self.switch, 0,0)

        self.setLayout(self.layout)


    @inlineCallbacks
    def switchState(self,state):
        yield self.server.switch_auto('PMT/Camera', True)
        yield self.server.switch_auto('PMT/Camera', False)



if __name__ == "__main__":
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    PMTCameraWidget = PMTCameraSwitchClient(reactor)
    PMTCameraWidget.show()
    reactor.run()
