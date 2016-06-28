from barium.lib.clients.gui.HP6033A_gui import HP6033A_UI
from twisted.internet.defer import inlineCallbacks, returnValue
from PyQt4 import QtGui, QtCore


class HP6033A_Client(HP6033A_UI):
    def __init__(self, reactor, host_ip, host_name, parent = None):
        from labrad.units import WithUnit
        self.U = WithUnit
        super(HP6033A_Client, self).__init__()
        self.reactor = reactor
        self.initialize(host_ip, host_name)
    @inlineCallbacks
    def initialize(self, host_ip, host_name):
        self.connect(host_ip, host_name)
        self.setupUi()
        self.signal_connect()
        yield None
    @inlineCallbacks
    def connect(self, host_ip, host_name):
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync(host=host_ip, name="HP6033A Client")
        try:
            self.hp = self.cxn.hp6033a_server
            print 'Connected to HP6033A Server'
            self.hp.select_device(0)
        except:
            print 'HP6033A Server Unavailable. Client is not connected.'
    @inlineCallbacks
    def signal_connect(self):
        ps_voltage = self.ps_voltage_spinbox.value()
        ps_current = self.ps_current_spinbox.value()
        ps_output = self.ps_output_button.isChecked()
        self.ps_voltage_spinbox.valueChanged.connect(lambda value=ps_voltage :self.set_voltage(value))
        self.ps_current_spinbox.valueChanged.connect(lambda value=ps_current :self.set_current(value))
        self.ps_output_button.toggled.connect(lambda state=ps_output:self.output(state))
        self.ps_pulse_voltage_button.clicked.connect(lambda :self.pulse_voltage())
        self.ps_pulse_current_button.clicked.connect(lambda :self.pulse_current())
        self.destroyed.connect(lambda :self.closeEvent())
        yield None
    @inlineCallbacks
    def set_voltage(self, value):
        value = self.U(value,'V')
        yield self.hp.set_voltage(value)
        self.update_indicators()
    @inlineCallbacks
    def set_current(self, value):
        value = self.U(value,'A')
        yield self.hp.set_current(value)
        self.update_indicators()
    @inlineCallbacks
    def output(self, state):
        yield self.hp.output_state(state)
        self.update_indicators()
    @inlineCallbacks
    def update_indicators(self):
        voltage = yield self.hp.get_voltage()
        self.ps_voltage_lcd.display(voltage['V'])
        current = yield self.hp.get_current()
        self.ps_current_lcd.display(current['A'])
    @inlineCallbacks
    def get_voltage(self):
        voltage = yield self.hp.get_voltage()['V']
        returnValue(voltage)
    @inlineCallbacks
    def get_current(self):
        current = yield self.hp.get_current()['A']
        returnValue(current)
    @inlineCallbacks
    def pulse_current(self):
        current = self.U(self.ps_pulse_current_spinbox.value(),'A')
        time = self.U(self.ps_pulse_time_spinbox.value(), 's')
        yield self.hp.pulse_current(current, time)
    @inlineCallbacks
    def pulse_voltage(self):
        voltage = self.U(self.ps_pulse_voltage_spinbox.value(),'V')
        time = self.U(self.ps_pulse_time_spinbox.value(), 's')
        yield self.hp.pulse_current(current, time)
    @inlineCallbacks
    def closeEvent(self, x):
        yield None
        reactor.stop()

import sys

if __name__ == "__main__":
    a = QtGui.QApplication( [] )
    from common.lib.clients import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    from socket import gethostname

    client = HP6033A_Client(reactor,'127.0.0.1',gethostname())
    client.show()

    reactor.run()
