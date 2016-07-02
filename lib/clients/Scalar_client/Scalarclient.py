from barium.lib.clients.gui.Scalar_gui import Scalar_UI
from twisted.internet.defer import inlineCallbacks, returnValue
from PyQt4 import QtGui, QtCore

class SR430_Scalar_Client(Scalar_UI):
    def __init__(self, reactor, host_ip, host_name, parent = None):
        from labrad.units import WithUnit
        self.U = WithUnit
        super(SR430_Scalar_Client, self).__init__()
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
        self.cxn = yield connectAsync(host=host_ip, name="SR430 Scalar Client")
        try:
            self.sca = self.cxn.sr430_scalar_server
            print 'Connected to SR430 Scalar Server.'
            self.sca.select_device(0)
        except:
            print 'SR430 Scalar Server Unavailable. Client is not connected.'
    @inlineCallbacks
    def signal_connect(self):
        discriminator_level = self.sca_discriminator_level_spinbox.value()
        records_per_scan = self.sca_records_per_scan_spinbox.value()
        bins_per_record = int(self.sca_bins_per_record_select.currentText())
        bin_width = int(self.sca_bin_width_select.currentText())
        #count_time
        self.sca_discriminator_level_spinbox.valueChanged.connect(lambda value=discriminator_level :self.set_discriminator_level(value))
        self.sca_records_per_scan_spinbox.valueChanged.connect(lambda value=records_per_scan :self.set_records_per_scan(value))
        self.sca_bins_per_record_select.currentIndexChanged.connect(lambda value=bins_per_record :self.set_bins_per_record(value))
        self.sca_bin_width_select.currentIndexChanged.connect(lambda value=bin_width :self.set_bin_width(value))

        #self.sca_start_new_scan_button.clicked.connect(lambda :self.start_new_scan(COUNT_TIME?))
        self.sca_start_scan_button.clicked.connect(lambda :self.start_scan())
        self.sca_stop_scan_button.clicked.connect(lambda :self.stop_scan())
        self.sca_clear_scan_button.clicked.connect(lambda :self.clear_scan())
        self.sca_get_counts_button.clicked.connect(lambda :self.get_counts())
        yield None

    @inlineCallbacks
    def set_discriminator_level(self, value):
        voltage = self.U(value,'V')
        yield self.sca.discriminator_level(voltage)
    @inlineCallbacks
    def set_records_per_scan(self, value):
        yield self.sca.records_per_scan(value)
    @inlineCallbacks
    def set_bins_per_record(self, value):
        yield self.sca.bins_per_record(value)
    @inlineCallbacks
    def set_bin_width(self, value):
        yield self.sca.bin_width(value)
    #@inlineCallbacks
    #def start_new_scan:
    #    yield self.sca.start_new_scan()
    @inlineCallbacks
    def start_scan(self):
        yield self.sca.start_scan()
    @inlineCallbacks
    def stop_scan(self):
        yield self.sca.stop_scan()
    @inlineCallbacks
    def clear_scan(self):
        yield self.sca.clear_scan()
    @inlineCallbacks
    def get_counts(self):
        counts = yield self.sca.get_counts()
        self.sca_counts_lcd.display(counts)
        returnValue(counts)
    
        
    @inlineCallbacks
    def closeEvent(self, x):
        self.stop_scan()
        yield None
        reactor.stop()

import sys

if __name__ == "__main__":
    a = QtGui.QApplication( [] )
    from common.lib.clients import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    from socket import gethostname

    client = SR430_Scalar_Client(reactor,'127.0.0.1',gethostname())
    client.show()

    reactor.run()
