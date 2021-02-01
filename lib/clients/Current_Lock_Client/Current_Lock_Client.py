#!/usr/bin/env python
#-*- coding:utf-8 -*-

from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks, returnValue
import socket
import os
from common.lib.clients.qtui.q_custom_text_changing_button import \
    TextChangingButton
from barium.lib.clients.gui.current_lock_gui import current_lock

SIGNALID1 = 445567



class current_lock_client(QtGui.QWidget):
    def __init__(self, reactor, parent=None):
        super(current_lock_client, self).__init__()
        #self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.reactor = reactor
        self.connect()

    @inlineCallbacks
    def connect(self):
        """Creates an Asynchronous connection to the current controller and
        connects incoming signals to relavent functions
        """
        from labrad.wrappers import connectAsync
        self.password = os.environ['LABRADPASSWORD']
        self.cxn = yield connectAsync('flexo', name = socket.gethostname() + ' Single Channel Lock', password=self.password)
        self.lock_server = yield self.cxn.current_lock_server
        self.server = yield cxn.current_controller_server
        yield self.server.signal_current_changed(SIGNALID1)
        yield self.server.addListener(listener = self.updateCurrent, source = None, ID = SIGNALID1)

        self.registry = self.cxn.registry
        self.d = {}
        

        # Get gain from registry
        yield self.registry.cd(['Servers','current_lock'])
        gain = yield self.registry.get('gain')

        self.initializeGUI()

    @inlineCallbacks
    def initializeGUI(self):
        layout = QtGui.QGridLayout()
        qBox = QtGui.QGroupBox('Current Lock')
        subLayout = QtGui.QGridLayout()
        qBox.setLayout(subLayout)
        layout.addWidget(qBox, 0, 0)#, returnValue
        from common.lib.clients.qtui import RGBconverter as RGB
        RGB = RGB.RGBconverter()
        color = int(2.998e8/(float(493*1e3))
        color = RGB.wav2RGB(color)
        color = tuple(color)
        current.setStyleSheet('color: rgb' + str(color))

        widget = current_lock_gui("Injection Lock Laser")
        self.d[0] = widget       
        init_current1 = yield self.lock_server.get_current()
        self.c.

        state = yield self.lock_server.get_lock_state(chan)
        laser.lockSwitch.setChecked(state)
        laser.lockSwitch.toggled.connect(lambda state = laser.lockSwitch.isDown(), chan = chan  \
                                             : self.set_lock(state, chan))


        init_gain = yield self.lock_server.get_gain(chan)
        laser.spinGain.valueChanged.connect(lambda gain = laser.spinGain.value(), \
                                        chan = chan : self.gainChanged(gain, chan))

        self.channel_GUIs[chan] = laser
        subLayout.addWidget(spin, self.lasers[chan][2][0], self.lasers[chan][2][1] , 1, 1)
        self.setLayout(layout)


        self.set_signal_listeners()


    @inlineCallbacks
    def currentChanged(self, current):
        yield self.lock_server.set_lock_current(current)

    @inlineCallbacks
    def gainChanged(self, gain):
        yield self.lock_server.set_gain(gain)

    @inlineCallbacks
    def updateCurrent(self, c, signal):
        current = signal
        self.d[0].current.setText(str(current))

    @inlineCallbacks
    def set_lock(self, state):
        yield self.lock_server.lock_channel(state)

if __name__ == "__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    current_lock = current_lock_client(reactor)
    current_lock.show()
    reactor.run()
