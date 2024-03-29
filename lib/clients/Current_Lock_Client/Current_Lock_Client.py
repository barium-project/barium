from barium.lib.clients.gui.current_lock_gui import QCustomCurrentGui

from twisted.internet.defer import inlineCallbacks, returnValue
from PyQt4 import QtGui
import time
import os
import socket



class CurrentLockClient(QtGui.QWidget):

    def __init__(self, reactor, parent=None):
        """initializels the GUI creates the reactor

        """
        super(CurrentLockClient, self).__init__()
        self.password = os.environ['LABRADPASSWORD']
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.reactor = reactor
        self.name = socket.gethostname() + ' Current Lock'
        self.connect()

    @inlineCallbacks
    def connect(self):
        """Creates an Asynchronous connection to the trap control computer and
        connects incoming signals to relevant functions
        """
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync('localhost',
                                      name=self.name,
                                      password=self.password)
        self.cc = yield self.cxn.current_controller
        self.cl = yield self.cxn.current_lock_server
        
        self.initializeGUI()

    @inlineCallbacks
    def initializeGUI(self):

        self.layout = QtGui.QGridLayout()
        self.qBox = QtGui.QGroupBox()
        self.subLayout = QtGui.QGridLayout()
        self.qBox.setLayout(self.subLayout)
        self.layout.addWidget(self.qBox, 0, 0)

        # initialize main Gui
        self.gui = QCustomCurrentGui()

        init_current = yield self.cc.get_current()
        self.gui.current_spin.setValue(init_current['mA'])
        self.gui.current_spin.valueChanged.connect(lambda current = self.gui.current_spin.value() : self.current_changed(current))

        init_state = yield self.cc.get_output_state()
        self.gui.output.setChecked(init_state)

        self.gui.output.toggled.connect(self.change_output)

        init_gain = yield self.cl.get_gain()
        self.gui.spinGain.setValue(init_gain)
        self.gui.spinGain.valueChanged.connect(lambda gain = self.gui.spinGain.value() : self.gainChanged(gain))

        self.gui.lock.toggled.connect(self.change_lock)

        self.subLayout.addWidget(self.gui, 1, 0)
        self.setLayout(self.layout)


    @inlineCallbacks
    def current_changed(self, current):
        from labrad.units import WithUnit
        yield self.cc.set_current(WithUnit(current,'mA'))

    @inlineCallbacks
    def gainChanged(self, gain):
        yield self.cl.set_gain(gain)
                                               
    @inlineCallbacks
    def change_output(self, state):
        yield self.cc.set_output_state(state)

    @inlineCallbacks
    def change_lock(self, state):
        yield self.cl.set_lock_state(state)





if __name__ == "__main__":
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    current_lock = CurrentLockClient(reactor)
    current_lock.show()
    reactor.run()
