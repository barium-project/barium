# Copyright (C) 2016 Calvin He
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from barium.lib.clients.gui.HP6033A_gui import HP6033A_UI
from barium.lib.clients.gui.HP6033A_safety_gui import HP6033A_Safety_UI
from twisted.internet.defer import inlineCallbacks, returnValue
from PyQt4 import QtGui, QtCore


class HP6033A_Client(HP6033A_UI):
    CURRSIGNALID = 147901
    VOLTSIGNALID = 147902
    MEASSIGNALID = 147903
    OUTPSIGNALID = 147904
    PULMSIGNALID = 147905
    def __init__(self, reactor, parent = None):
        from labrad.units import WithUnit
        self.U = WithUnit
        super(HP6033A_Client, self).__init__()
        self.reactor = reactor
        self.initialize()
    @inlineCallbacks
    def initialize(self):
        """Initializes the client by setting up its GUI objects
        """
        self.setupUi()
        yield None
    @inlineCallbacks
    def self_connect(self, host_name, client_name, device_id):
        """Connects to LabRAD, HP6033A Server, and establishes LabRAD signal connections
        """
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync(host=host_name, name=client_name, password="lab")
        try:
            self.server = self.cxn.hp6033a_server
            print 'Connected to HP6033A Server'
            self.device_id = device_id
            self.server.select_device(self.device_id)

            yield self.server.signal__current_changed(self.CURRSIGNALID)
            yield self.server.signal__voltage_changed(self.VOLTSIGNALID)
            yield self.server.signal__get_measurements(self.MEASSIGNALID)
            yield self.server.signal__output_changed(self.OUTPSIGNALID)
            yield self.server.signal__pulse_mode_changed(self.PULMSIGNALID)
            yield self.server.addListener(listener = self.update_curr, source = None, ID = self.CURRSIGNALID)
            yield self.server.addListener(listener = self.update_volt, source = None, ID = self.VOLTSIGNALID)
            yield self.server.addListener(listener = self.update_meas, source = None, ID = self.MEASSIGNALID)
            yield self.server.addListener(listener = self.update_outp, source = None, ID = self.OUTPSIGNALID)
            yield self.server.addListener(listener = self.update_pulm, source = None, ID = self.PULMSIGNALID)

            self.signal_connect()
        except:
            print 'HP6033A Server Unavailable. Client is not connected.'
    @inlineCallbacks
    def signal_connect(self):
        """Connects the PyQt4 signals to slots
        """
        self.ps_apply_settings_button.clicked.connect(lambda :self.apply_settings())
        self.ps_pulse_voltage_button.clicked.connect(lambda :self.pulse_voltage())
        self.ps_pulse_current_button.clicked.connect(lambda :self.pulse_current())
        self.destroyed.connect(lambda :self.closeEvent())

        self.safety_limits = HP6033A_Safety_UI()    #Safety Limits Window
        self.safety_limits.setupUi()
        self.max_voltage = 2                       #Initialize Variables
        self.min_voltage = 0
        self.max_current = 7
        self.min_current = 0
        self.safety_limits.ps_max_voltage_spinbox.valueChanged.connect(lambda :self.update_safety())
        self.safety_limits.ps_min_voltage_spinbox.valueChanged.connect(lambda :self.update_safety())
        self.safety_limits.ps_max_current_spinbox.valueChanged.connect(lambda :self.update_safety())
        self.safety_limits.ps_min_current_spinbox.valueChanged.connect(lambda :self.update_safety())
        self.ps_set_safety_limits_button.clicked.connect(lambda :self.show_safety_limits())

        yield None
    #The following updates the client via LabRAD signals whenever settings are changed:
    def update_curr(self,c,signal):
        if c.ID[0] == self.device_id:
            self.ps_current_spinbox.setValue(signal['A'])
    def update_volt(self,c,signal):
        if c.ID[0] == self.device_id:
            self.ps_voltage_spinbox.setValue(signal['V'])
    def update_meas(self,c,signal):
        if c.ID[0] == self.device_id:
            voltage = signal[0]['V']
            current = signal[1]['A']
            self.ps_voltage_lcd.display(voltage)
            self.ps_current_lcd.display(current)
    def update_outp(self,c,signal):
        if c.ID[0] == self.device_id:
            self.ps_output_checkbox.setChecked(signal)
    def update_pulm(self,c,signal):
        if c.ID[0] == self.device_id:
            self.ps_pulse_mode_checkbox.setChecked(signal)

    #HP6033A Functions:
    @inlineCallbacks
    def update_safety(self):
        self.max_voltage = self.safety_limits.ps_max_voltage_spinbox.value()
        self.min_voltage = self.safety_limits.ps_min_voltage_spinbox.value()
        self.max_current = self.safety_limits.ps_max_current_spinbox.value()
        self.min_current = self.safety_limits.ps_min_current_spinbox.value()
        self.ps_voltage_spinbox.setRange(self.min_voltage,self.max_voltage)
        self.ps_current_spinbox.setRange(self.min_current,self.max_current)
        yield None
    @inlineCallbacks
    def show_safety_limits(self):
        import ctypes
        screensize = [ctypes.windll.user32.GetSystemMetrics(0),ctypes.windll.user32.GetSystemMetrics(1)]
        windowsize = [self.safety_limits.width(),self.safety_limits.height()]
        screencenter = [(screensize[0]-windowsize[0])/2,(screensize[1]-windowsize[1])/2]
        self.safety_limits.move(screencenter[0],screencenter[1])
        self.safety_limits.show()
        yield None
    @inlineCallbacks
    def set_voltage(self, value):
        value = self.U(value,'V')
        yield self.server.set_voltage(value)
        #self.update_indicators()
    @inlineCallbacks
    def set_current(self, value):
        value = self.U(value,'A')
        yield self.server.set_current(value)
        #self.update_indicators()
    @inlineCallbacks
    def output(self, state):
        yield self.server.output_state(state)
        #self.update_indicators()
    @inlineCallbacks
    def apply_settings(self):
        voltage = self.ps_voltage_spinbox.value()
        current = self.ps_current_spinbox.value()
        state = self.ps_output_checkbox.isChecked()
        self.set_voltage(voltage)
        self.set_current(current)
        self.output(state)
        self.update_indicators()
        yield None
    @inlineCallbacks
    def update_indicators(self):
        voltage = yield self.server.get_voltage()
        self.ps_voltage_lcd.display(voltage['V'])
        current = yield self.server.get_current()
        self.ps_current_lcd.display(current['A'])
        mode = yield self.server.cc_mode()
        if mode == True:
            self.ps_mode_text.setText('CC')
        else:
            self.ps_mode_text.setText('CV')
    @inlineCallbacks
    def get_voltage(self):
        voltage = yield self.server.get_voltage()
        returnValue(voltage['V'])
    @inlineCallbacks
    def get_current(self):
        current = yield self.server.get_current()
        returnValue(current['A'])
    @inlineCallbacks
    def pulse_current(self):
        current = self.U(self.ps_pulse_current_spinbox.value(),'A')
        voltage = self.U(self.ps_pulse_voltage_spinbox.value(),'V')
        time = self.U(self.ps_pulse_time_spinbox.value(), 's')
        yield self.server.pulse_current(current, voltage, time)
    @inlineCallbacks
    def pulse_voltage(self):
        voltage = self.U(self.ps_pulse_voltage_spinbox.value(),'V')
        current = self.U(self.ps_pulse_current_spinbox.value(),'A')
        time = self.U(self.ps_pulse_time_spinbox.value(), 's')
        yield self.server.pulse_current(current, voltage, time)

    #Close event:
    @inlineCallbacks
    def closeEvent(self, x):
        self.reactor.stop()
        yield None

import sys

if __name__ == "__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor

    client = HP6033A_Client(reactor)
    client.self_connect('bender',"HP6033A Client",0)  #.self_connect(host_name, client_name, device_id)
    client.show()

    reactor.run()
