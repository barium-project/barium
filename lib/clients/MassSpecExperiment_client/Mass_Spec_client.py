from barium.lib.clients.gui.HP6033A_gui import HP6033A_UI
from barium.lib.clients.gui.RGA_gui import RGA_UI
from barium.lib.clients.gui.Scalar_gui import Scalar_UI
from barium.lib.clients.gui.LabRADconnection_gui import LabRADconnection_UI
from barium.lib.clients.gui.MassSpecExperiment_gui import MassSpecExperiment_UI
from barium.lib.clients.gui.SaveDirectory_gui import SaveDirectory_UI

from barium.lib.clients.HP6033A_client.HP6033Aclient import HP6033A_Client
from barium.lib.clients.RGA_client.RGAclient import RGA_Client
from barium.lib.clients.Scalar_client.Scalarclient import SR430_Scalar_Client

from twisted.internet.defer import inlineCallbacks, returnValue
from PyQt4 import QtGui, QtCore
import time
import numpy as np
from datetime import datetime

class LabRADconnection_Client(LabRADconnection_UI):
    def __init__(self, reactor, parent = None):
        super(LabRADconnection_Client, self).__init__()
        self.initialize()
    @inlineCallbacks
    def initialize(self):
        self.setupUi()
        self.signal_connect()
        self.setWindowTitle("Mass Spectrum Experiment Client")
        yield None
    @inlineCallbacks    
    def signal_connect(self):
        self.autoconnect_button.clicked.connect(lambda :self.connect())
        yield None
    @inlineCallbacks
    def connect(self):
        host_ip = str(self.host_ip_text.currentText())
        host_name = str(self.host_name_text.currentText())
        
        self.hpui = HP6033A_Client(reactor, host_ip, host_name)
        self.scaui = SR430_Scalar_Client(reactor, host_ip, host_name)
        self.rgaui = RGA_Client(reactor, host_ip, host_name)
        self.savdirui = SaveDirectory_UI()
        self.massspecui = MassSpecExperiment_UI()
        if True:
            self.autoconnect_button.setDisabled(True)
            self.autoconnect_button.setText("Connected")
            self.setup_experiment()
        yield None
    @inlineCallbacks
    def setup_experiment(self):
        self.hpui.setParent(self)
        self.scaui.setParent(self)
        self.savdirui.setParent(self)
        self.rgaui.setParent(self)
        
        self.massspecui.setParent(self)
        self.savdirui.setParent(self)
        
        self.massspecui.setupUi()
        self.savdirui.setupUi()
        #Widget Orientation#
        #Row 1#
        self.hpui.move(0,115)       #Column 1
        self.scaui.move(400,115)    #Column 2
        self.savdirui.move(800,115) #Column 3
        #Row 1#
        
        #Row 2#
        self.rgaui.move(0,115+300)          #Column 1
        self.massspecui.move(400,115+300)   #Column 2
        #Row 2#
        #Widget Orientation#
        self.hpui.show()
        self.scaui.show()
        self.rgaui.show()
        self.massspecui.show()
        self.savdirui.show()
        
        self.experiment_signal_connect()

        self.resize(self.width(),115+300*2)
        import ctypes
        screensize = [ctypes.windll.user32.GetSystemMetrics(0),ctypes.windll.user32.GetSystemMetrics(1)]
        windowsize = [self.width(),self.height()]
        screencenter = [(screensize[0]-windowsize[0])/2,(screensize[1]-windowsize[1])/2]
        self.move(screencenter[0],screencenter[1])
                
        reactor.run()
        yield None
    @inlineCallbacks
    def experiment_signal_connect(self):
        self.massspecui.ms_calculate_time_button.clicked.connect(lambda :self.calculate_time())
        self.massspecui.ms_begin_experiment_button.clicked.connect(lambda :self.begin_experiment())
        yield None
    @inlineCallbacks
    def calculate_time(self):
        records_per_scan = self.scaui.sca_records_per_scan_spinbox.value()
        trigger_frequency = self.massspecui.ms_trigger_frequency_spinbox.value()
        mass_list = self.massspecui.ms_mass_sweep_select.currentText()
        current_list = self.massspecui.ms_current_sweep_select.currentText()

        mass_iterations = len(mass_list)
        current_iterations = len(current_list)
        sweep_iterations = self.massspecui.ms_iterations_spinbox.value()
        wait_time = self.massspecui.ms_wait_time_spinbox.value()

        count_time_per_point = records_per_scan/trigger_frequency+wait_time+3
        count_time_per_sweep = count_time_per_point*mass_iterations*current_iterations
        total_count_time = count_time_per_sweep*sweep_iterations

        self.massspecui.ms_count_time_per_point_lcd.display(count_time_per_point)
        self.massspecui.ms_count_time_per_sweep_lcd.display(count_time_per_sweep)
        self.massspecui.ms_total_count_time_lcd.display(total_count_time)
        time_list = [count_time_per_point, total_count_time]
        yield None
        returnValue(time_list)
    @inlineCallbacks
    def begin_experiment(self):
        if self.hpui.ps_pulse_mode_checkbox.isChecked == True:
            print 'Turn of pulse mode before beginning experiment.'
            returnValue(None)
        #Setting the experimental parameters:
        time_list = self.calculate_time()
        count_time_per_point = time_list[0]
        total_count_time = time_list[1]
        
        mass_list = self.massspecui.ms_mass_sweep_select.currentText()
        current_list = self.massspecui.ms_current_sweep_select.currentText()
        sweep_iterations = self.massspecui.ms_iterations_spinbox.value()
        wait_time = self.massspecui.ms_wait_time_spinbox.value()

        filepath = self.savedirui.sd_save_path_select.currentText()
        filename = self.savedirui.sd_filename_text.text()

        results = np.array([[0,0,0,0,0,0,0,0]])
        #The actual loop (All settings should have been set on the other widgets)
        for i in range(sweep_iterations):
            for current in current_list:
                self.hpui.set_current(current)
                for mass in mass_list:
                    self.hpui.update_values()
                    self.rgaui.set_mass_lock(mass)
                    self.scaui.clear_scan()
                    self.scaui.start_scan()
                    time.sleep(count_time_per_point)
                    counts = float(self.scaui.get_counts())
                    time.sleep(3)
                    t = datetime.now().timetuple()
                    voltage = self.hpui.get_voltage()
                    current = self.hpui.get_current()
                    new_data = np.array([[mass,counts,t[2],t[3],t[4],t[5],voltage,current]])
                    print iteration, new_data
                    results = np.concatenate((results,new_data),axis=0)
                    np.savetxt(filepath+filename,results,fmt="%0.5e")
                    time.sleep(wait_time)        
        yield None
    @inlineCallbacks
    def closeEvent(self, x):
        yield None
        reactor.stop()

import sys

if __name__ == "__main__":
    a = QtGui.QApplication ([])
    from common.lib.clients import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    client = LabRADconnection_Client(reactor)
    client.show()
    
    sys.exit(a.exec_())
