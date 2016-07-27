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

from barium.lib.clients.gui.Scalar_gui import Scalar_UI
from twisted.internet.defer import inlineCallbacks, returnValue
from PyQt4 import QtGui, QtCore

class SR430_Scalar_Client(Scalar_UI):
    BPRSIGNALID = 275309
    BWSIGNALID = 275311
    RPSSIGNALID = 275312
    DLSIGNALID = 275313
    RECORDSIGNALID = 275317
    PANELSIGNALID = 275318
    def __init__(self, reactor, parent = None):
        from labrad.units import WithUnit
        self.U = WithUnit
        super(SR430_Scalar_Client, self).__init__()
        self.reactor = reactor
        self.initialize()
    @inlineCallbacks
    def initialize(self):
        """Initializes the client by setting up the GUI objects
        """
        self.setupUi()
        yield None
    @inlineCallbacks
    def self_connect(self, host_name, client_name, device_id):
        """Connects to LabRAD, the SR430 Scalar Server, and establishes LabRAD signal connections
        """
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync(host=host_name, name=client_name, password="lab")
        #try:
        self.server = yield self.cxn.sr430_scalar_server
        print 'Connected to SR430 Scalar Server.'
        self.device_id = device_id
        yield self.server.select_device(device_id)
        
        yield self.server.signal__bins_per_record_changed(self.BPRSIGNALID)
        yield self.server.signal__bin_width_changed(self.BWSIGNALID)
        yield self.server.signal__discriminator_level_changed(self.DLSIGNALID)
        yield self.server.signal__records_per_scan_changed(self.RPSSIGNALID)
        yield self.server.signal__record_signal(self.RECORDSIGNALID)
        yield self.server.signal__panel_signal(self.PANELSIGNALID)
        yield self.server.addListener(listener = self.update_bpr, source = None, ID = self.BPRSIGNALID)
        yield self.server.addListener(listener = self.update_bw, source = None, ID = self.BWSIGNALID)
        yield self.server.addListener(listener = self.update_dl, source = None, ID = self.DLSIGNALID)
        yield self.server.addListener(listener = self.update_rps, source = None, ID = self.RPSSIGNALID)
        yield self.server.addListener(listener = self.record_update, source = None, ID = self.RECORDSIGNALID)
        yield self.server.addListener(listener = self.panel_update, source = None, ID = self.PANELSIGNALID)
        
        self.signal_connect()
        #yield self.server.update_settings()
        #except:
        #    print 'SR430 Scalar Server Unavailable. Client is not connected.'
    @inlineCallbacks
    def signal_connect(self):
        """Connects PyQt4 signals to slots
        """
        self.sca_discriminator_level_spinbox.valueChanged.connect(lambda :self.set_discriminator_level())
        self.sca_records_per_scan_spinbox.valueChanged.connect(lambda :self.set_records_per_scan())
        self.sca_bins_per_record_select.currentIndexChanged.connect(lambda :self.set_bins_per_record())
        self.sca_bin_width_select.currentIndexChanged.connect(lambda :self.set_bin_width())

        self.sca_start_scan_button.clicked.connect(lambda :self.start_scan())
        self.sca_stop_scan_button.clicked.connect(lambda :self.stop_scan())
        self.sca_clear_scan_button.clicked.connect(lambda :self.clear_scan())
        self.sca_get_counts_button.clicked.connect(lambda :self.get_counts())

        self.set_trigger_frequency()
        yield None
    #The following updates the client GUI via LabRAD signals whenever settings are changed:
    def update_bpr(self, c, signal):
        if c.ID[0] == self.device_id:
            argument_dictionary = {1024: 1, 2*1024: 2, 3*1024: 3, 4*1024: 4, 5*1024: 5,
                                    6*1024: 6, 7*1024: 7, 8*1024: 8, 9*1024: 9, 10*1024: 10,
                                    11*1024: 11, 12*1024: 12, 13*1024: 13, 14*1024: 14,
                                    15*1024: 15, 16*1024: 16}
            self.sca_bins_per_record_select.setCurrentIndex(signal-1)
    def update_bw(self, c, signal):
        if c.ID[0] == self.device_id:
            argument_dictionary = {5: 0,40: 1,80: 2,160: 3,320: 4,640: 5,1280: 6,2560: 7, 5120: 8,
                                   10240: 9, 20480: 10, 40960: 11, 81920: 12, 163840: 13, 327680: 14,
                                   655360: 15, 1310720: 16, 2621400: 17, 5242900: 18, 10486000: 19}
            self.sca_bin_width_select.setCurrentIndex(signal)
    def update_rps(self, c, signal):
        if c.ID[0] == self.device_id:
            self.sca_records_per_scan_spinbox.setValue(signal)
    def update_dl(self, c, signal):
        if c.ID[0] == self.device_id:
            self.sca_discriminator_level_spinbox.setValue(int(signal))
    def record_update(self, c, signal):
        if c.ID[0] == self.device_id:
            self.sca_progress_bar.setValue(signal)
    def panel_update(self, c, signal):
        if c.ID[0] == self.device_id:
            if signal == 'scanning':
                self.frame_1.setDisabled(True)
                self.frame_2.setDisabled(True)
            elif signal == 'paused':
                self.frame_1.setDisabled(True)
                self.frame_2.setEnabled(True)
            elif signal == 'cleared':
                self.frame_1.setEnabled(True)
                self.frame_2.setEnabled(True)
                self.sca_progress_bar.setValue(0)

    #Scalar Functions:
    @inlineCallbacks
    def set_discriminator_level(self):
        discriminator_level = self.sca_discriminator_level_spinbox.value()
        voltage = self.U(discriminator_level,'mV')
        yield self.server.discriminator_level(voltage)
    @inlineCallbacks
    def set_records_per_scan(self):
        records_per_scan = self.sca_records_per_scan_spinbox.value()
        yield self.server.records_per_scan(records_per_scan)
        self.sca_progress_bar.setMaximum(self.sca_records_per_scan_spinbox.value())
    @inlineCallbacks
    def set_bins_per_record(self):
        bins_per_record = int(self.sca_bins_per_record_select.currentText())
        yield self.server.bins_per_record(bins_per_record)
        self.set_trigger_frequency()
    @inlineCallbacks
    def set_bin_width(self):
        bin_width = int(self.sca_bin_width_select.currentText())
        yield self.server.bin_width(bin_width)
        self.set_trigger_frequency()
    @inlineCallbacks
    def set_trigger_frequency(self):
        discriminator_level = self.sca_discriminator_level_spinbox.value()
        records_per_scan = self.sca_records_per_scan_spinbox.value()
        bins_per_record = str(self.sca_bins_per_record_select.currentText())
        bin_width = str(self.sca_bin_width_select.currentText())
        bins_per_record = int(bins_per_record)
        bin_width = int(bin_width)

        self.integration_time = bins_per_record*bin_width*records_per_scan*10**(-9)
        self.trigger_period = (bins_per_record*bin_width + bins_per_record*250 + 150*(10**3))*10**(-6)+1
        #trigger_period(ms) = (bpr*bw(ns) + bpr*250ns + 150us) + 1ms
        self.trigger_frequency = round(1/(self.trigger_period*10**(-3)),3)
        
        self.sca_integration_time_lcd.display(self.integration_time)
        self.sca_trigger_frequency_lcd.display(self.trigger_frequency)
        yield None
    @inlineCallbacks
    def start_scan(self):
        self.set_bins_per_record()
        self.set_records_per_scan()
        self.set_bin_width()
        self.set_trigger_frequency
        self.set_discriminator_level()
        yield self.server.start_scan()
    @inlineCallbacks
    def stop_scan(self):
        yield self.server.stop_scan()
    @inlineCallbacks
    def clear_scan(self):
        yield self.server.clear_scan()
    @inlineCallbacks
    def get_counts(self):
        self.sca_counts_lcd.display('...')
        counts = yield self.server.get_counts()
        self.sca_counts_lcd.display(counts)
        returnValue(counts)

    #Close event:
    @inlineCallbacks
    def closeEvent(self, x):
        yield None
        self.reactor.stop()

import sys

if __name__ == "__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor

    client = SR430_Scalar_Client(reactor)
    client.self_connect('planetexpress',"SR430 Scalar Client",0)  #.self_connect(host_name, client_name, device_id)
    client.show()

    reactor.run()
