#!/usr/bin/env python
#-*- coding:utf-8 -*-

from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks, returnValue
import socket
import os
from config.multiplexerclient_config import multiplexer_config
from common.lib.clients.qtui.q_custom_text_changing_button import \
    TextChangingButton
from barium.lib.clients.Software_Laser_Lock_Client.software_laser_lock_client import software_laser_lock_client
from barium.lib.clients.Current_Controller_Client.current_controller_client import CurrentControllerClient


SIGNALID1 = 445567


class laser_control_client(QtGui.QWidget):
    def __init__(self, reactor, parent=None):
        super(laser_control_client, self).__init__()
        #self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.reactor = reactor
        self.initializeGUI()


    def initializeGUI(self):
        self.layout = QtGui.QGridLayout()
        self.qBox = QtGui.QGroupBox('Laser Control Client')
        self.subLayout = QtGui.QGridLayout()
        self.qBox.setLayout(self.subLayout)
        self.layout.addWidget(self.qBox, 0, 0), returnValue

        self.software_lock = software_laser_lock_client(self.reactor)
        #self.cc_control = CurrentControllerClient(self.reactor)

        self.subLayout.addWidget(self.software_lock,0,0,4,1)
        #self.subLayout.addWidget(self.cc_control,2,1,1,1)
        self.setLayout(self.layout)

if __name__ == "__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    laser_control = laser_control_client(reactor)
    laser_control.show()
    reactor.run()
