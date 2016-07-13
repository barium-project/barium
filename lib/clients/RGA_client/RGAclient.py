from barium.lib.clients.gui.RGA_gui import RGA_UI
from twisted.internet.defer import inlineCallbacks, returnValue
from PyQt4 import QtGui, QtCore

class RGA_Client(RGA_UI):
    FILSIGNALID = 315039
    MLSIGNALID = 315040
    HVSIGNALID = 315041
    BUFSIGNALID = 315042
    QUESIGNALID = 315043
    def __init__(self, reactor, parent = None):
        from labrad.units import WithUnit
        self.U = WithUnit
        super(RGA_Client, self).__init__()
        self.reactor = reactor
        self.initialize()
    @inlineCallbacks
    def initialize(self):
        self.setupUi()
        yield None
    @inlineCallbacks
    def self_connect(self, host_ip, host_name):
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync(host=host_ip, name="RGA Client", password="lab")
        try:
            self.server = self.cxn.rga_server
            print 'Connected to RGA Server.'
            yield self.server.signal__filament_changed(self.FILSIGNALID)
            yield self.server.signal__mass_lock_changed(self.MLSIGNALID)
            yield self.server.signal__high_voltage_changed(self.HVSIGNALID)
            yield self.server.signal__buffer_read(self.BUFSIGNALID)
            yield self.server.signal__query_sent(self.QUESIGNALID)
            yield self.server.addListener(listener = self.update_fil, source = None, ID = self.FILSIGNALID)
            yield self.server.addListener(listener = self.update_ml, source = None, ID = self.MLSIGNALID)
            yield self.server.addListener(listener = self.update_hv, source = None, ID = self.HVSIGNALID)
            yield self.server.addListener(listener = self.update_buf, source = None, ID = self.BUFSIGNALID)
            yield self.server.addListener(listener = self.update_que, source = None, ID = self.QUESIGNALID)

            self.signal_connect()
        except:
            print 'RGA Server Unavailable. Client is not connected.'
    @inlineCallbacks
    def signal_connect(self):        
        filament_state = self.rga_filament_checkbox.isChecked()
        voltage = self.rga_voltage_spinbox.value()
        mass = self.rga_mass_lock_spinbox.value()
        self.rga_filament_checkbox.toggled.connect(lambda state=filament_state :self.set_filament_state(state))
        self.rga_voltage_spinbox.valueChanged.connect(lambda value=voltage :self.set_voltage(value))
        self.rga_mass_lock_spinbox.valueChanged.connect(lambda value=mass :self.set_mass_lock(value))
        self.rga_id_button.clicked.connect(lambda :self.get_id())
        self.rga_fl_button.clicked.connect(lambda :self.get_filament_status())
        self.rga_hv_button.clicked.connect(lambda :self.get_voltage())
        self.rga_read_buffer_button.clicked.connect(lambda :self.read_buffer())
        self.rga_clear_button.clicked.connect(lambda :self.clear_buffer())
        yield None
    def update_fil(self, c, signal):
        if signal == 1:
            self.rga_filament_checkbox.setChecked(True)
        elif signal == 0:
            self.rga_filament_checkbox.setChecked(False)
    def update_ml(self, c, signal):
        self.rga_mass_lock_spinbox.setValue(signal)
    def update_hv(self, c, signal):
        self.rga_voltage_spinbox.setValue(signal)
    def update_buf(self, c, signal):
        self.rga_buffer_text.appendPlainText(signal)
    def update_que(self, c, signal):
        self.rga_buffer_text.appendPlainText(signal)
        
    @inlineCallbacks
    def set_filament_state(self,state):
        if state==True:
            bit = 1
        else:
            bit = 0
        yield self.server.filament(bit)
    @inlineCallbacks
    def set_voltage(self,value):
        yield self.server.high_voltage(value)
    @inlineCallbacks
    def set_mass_lock(self,value):
        yield self.server.mass_lock(value)
    @inlineCallbacks
    def get_id(self):
        yield self.server.identify()
    @inlineCallbacks
    def get_filament_status(self):
        yield self.server.filament()
    @inlineCallbacks
    def get_voltage(self):
        yield self.server.high_voltage()
    @inlineCallbacks
    def read_buffer(self):
        message = yield self.server.read_buffer()
        self.rga_buffer_text.appendPlainText(message)
    @inlineCallbacks
    def clear_buffer(self):
        self.rga_buffer_text.clear()
        yield None
    @inlineCallbacks
    def closeEvent(self,x):
        self.reactor.stop()
        yield None

import sys

if __name__ == "__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    from socket import gethostname

    client = RGA_Client(reactor)
    client.self_connect('127.0.0.1',gethostname())
    client.show()

    reactor.run()
