from barium.lib.clients.gui.HP6033A_gui import HP6033A_UI
from barium.lib.clients.gui.RGA_gui import RGA_UI
from barium.lib.clients.gui.Scalar_gui import Scalar_UI
from barium.lib.clients.gui.LabRADconnection_gui import LabRADconnection_UI

from barium.lib.clients.HP6033A_client.HP6033Aclient import HP6033A_Client
from barium.lib.clients.RGA_client.RGAclient import RGA_Client
from barium.lib.clients.Scalar_client.Scalarclient import SR430_Scalar_Client

from twisted.internet.defer import inlineCallbacks, returnValue
from PyQt4 import QtGui, QtCore
import time

class LabRADconnection_Client(LabRADconnection_UI):
    def __init__(self, reactor, parent = None):
        super(LabRADconnection_Client, self).__init__()
        self.initialize()
    @inlineCallbacks
    def initialize(self):
        self.setupUi()
        self.signal_connect()
        yield None
    @inlineCallbacks    
    def signal_connect(self):
        print 'connecting signal'
        self.autoconnect_button.toggled.connect(lambda :self.connect())
        print 'signal connected'
        yield None
    @inlineCallbacks
    def connect(self):
        host_ip = str(self.host_ip_text.currentText())
        host_name = str(self.host_name_text.currentText())

        #self.hpui = HP6033A_Client(reactor, host_ip, host_name)
        #self.hpui.show()
    
        #self.rgaui = RGA_Client())
        #self.rgawidget.show()
    
        #self.scaui = SR430_Scalar_Client(reactor, host_ip, host_name)
        #self.scaui.show()

        reactor.run()
    @inlineCallbacks
    def closeEvent(self, x):
        yield None
        reactor.stop()

import sys

if __name__ == "__main__":
    a = QtGui.QApplication ([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    client = LabRADconnection_Client(reactor)
    client.show()
    
    sys.exit(a.exec_())
