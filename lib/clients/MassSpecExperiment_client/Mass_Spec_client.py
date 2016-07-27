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
from barium.lib.clients.gui.RGA_gui import RGA_UI
from barium.lib.clients.gui.Scalar_gui import Scalar_UI
from barium.lib.clients.gui.LabRADconnection_gui import LabRADconnection_UI
from barium.lib.clients.gui.MassSpecExperiment_gui import MassSpecExperiment_UI
from barium.lib.clients.gui.SaveDirectory_gui import SaveDirectory_UI
from barium.lib.clients.gui.CommandLine_gui import CommandLine_UI
from barium.lib.clients.gui.Timers_gui import Timers_UI
from barium.lib.clients.gui.DataLog_gui import DataLog_UI

from barium.lib.clients.HP6033A_client.HP6033Aclient import HP6033A_Client
from barium.lib.clients.RGA_client.RGAclient import RGA_Client
from barium.lib.clients.Scalar_client.Scalarclient import SR430_Scalar_Client

from twisted.internet.defer import inlineCallbacks, returnValue
from PyQt4 import QtGui, QtCore
import time
import numpy as np
import ctypes
from datetime import datetime

#Defining functions to be used for GUI manipulation
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)
#


class Mass_Spec_Client(LabRADconnection_UI):
    def __init__(self, reactor, parent = None):
        super(LabRADconnection_UI, self).__init__()
        self.initialize()
        
    @inlineCallbacks
    def initialize(self):
        """Sets up the client GUI object to accept user input for LabRAD connection
        """
        self.setupUi()
        self.signal_connect()
        self.setWindowTitle("Mass Spectrum Experiment Client")
        yield None
        
    @inlineCallbacks    
    def signal_connect(self):
        """Connects the autoconnect_button clicked event to the .connect() slot
        """
        self.autoconnect_button.clicked.connect(lambda :self.connect())
        yield None
        
    @inlineCallbacks
    def connect(self):
        """Creates an HP6033A_Client, SR430_Scalar_Client, RGA_Client and connects each one of them to
        LabRAD and their respective clients, and establishes LabRAD signal connections.  Then instantiates
        miscellaneous GUI objects and calls .setup_experiment()
        """
        from labrad.wrappers import connectAsync
        host_name = str(self.host_name_text.currentText())
        SINGLE_CONNECTION = False   #Single Connection does not work so far

        self.hpui = HP6033A_Client(reactor)         #Instantiates HP6033A Client
        self.scaui = SR430_Scalar_Client(reactor)
        self.rgaui = RGA_Client(reactor)

        if not SINGLE_CONNECTION:
            self.hpui.self_connect(host_name, "Mass Spec HP6033A Client", self.lc_power_supply_id_spinbox.value()) #Tells hpui object to connect to labrad if SINGLE_CONNECTION == False
            self.scaui.self_connect(host_name, "Mass Spec Scalar Client", self.lc_scalar_id_spinbox.value())
            self.rgaui.self_connect(host_name, "Mass Spec RGA Client")


        if SINGLE_CONNECTION:
            self.cxn = yield connectAsync(host=host_name, name="Mass Spectrum Client", password="lab")

            self.hpui.server = self.cxn.hp6033a_server  #Maps HP6033A Server to HP6033A.server attribute if SINGLE_CONNECTION == True
            yield self.hpui.server.select_device(self.lc_power_supply_id_spinbox.value())
            #LabRAD Signal Connections:
            yield self.hpui.server.signal__current_changed(self.hpui.CURRSIGNALID)
            yield self.hpui.server.signal__voltage_changed(self.hpui.VOLTSIGNALID)
            yield self.hpui.server.signal__get_measurements(self.hpui.MEASSIGNALID)
            yield self.hpui.server.signal__output_changed(self.hpui.OUTPSIGNALID)
            yield self.hpui.server.addListener(listener = self.hpui.update_curr, source = None, ID = self.hpui.CURRSIGNALID)
            yield self.hpui.server.addListener(listener = self.hpui.update_volt, source = None, ID = self.hpui.VOLTSIGNALID)
            yield self.hpui.server.addListener(listener = self.hpui.update_meas, source = None, ID = self.hpui.MEASSIGNALID)
            yield self.hpui.server.addListener(listener = self.hpui.update_outp, source = None, ID = self.hpui.OUTPSIGNALID)
            self.hpui.signal_connect()                  #Connects signals between GUI objects and client functions

            self.scaui.server = self.cxn.sr430_scalar_server
            yield self.scaui.server.select_device(self.lc_scalar_id_spinbox.value())
            yield self.scaui.server.signal__bins_per_record_changed(self.scaui.BPRSIGNALID)
            yield self.scaui.server.signal__bin_width_changed(self.scaui.BWSIGNALID)
            yield self.scaui.server.signal__discriminator_level_changed(self.scaui.DLSIGNALID)
            yield self.scaui.server.signal__records_per_scan_changed(self.scaui.RPSSIGNALID)
            yield self.scaui.server.signal__record_signal(self.scaui.RECORDSIGNALID)
            yield self.scaui.server.signal__panel_signal(self.scaui.PANELSIGNALID)
            yield self.scaui.server.addListener(listener = self.scaui.update_bpr, source = None, ID = self.scaui.BPRSIGNALID)
            yield self.scaui.server.addListener(listener = self.scaui.update_bw, source = None, ID = self.scaui.BWSIGNALID)
            yield self.scaui.server.addListener(listener = self.scaui.update_dl, source = None, ID = self.scaui.DLSIGNALID)
            yield self.scaui.server.addListener(listener = self.scaui.update_rps, source = None, ID = self.scaui.RPSSIGNALID)
            yield self.scaui.server.addListener(listener = self.scaui.record_update, source = None, ID = self.scaui.RECORDSIGNALID)
            yield self.scaui.server.addListener(listener = self.scaui.panel_update, source = None, ID = self.scaui.PANELSIGNALID)
            yield self.scaui.server.addListener(listener = self.panel_update_test, source = None, ID = self.scaui.PANELSIGNALID)
            self.scaui.signal_connect()

            self.rgaui.server = self.cxn.rga_server
            yield self.rgaui.server.signal__filament_changed(self.rgaui.FILSIGNALID)
            yield self.rgaui.server.signal__mass_lock_changed(self.rgaui.MLSIGNALID)
            yield self.rgaui.server.signal__high_voltage_changed(self.rgaui.HVSIGNALID)
            yield self.rgaui.server.signal__buffer_read(self.rgaui.BUFSIGNALID)
            yield self.rgaui.server.signal__query_sent(self.rgaui.QUESIGNALID)
            yield self.rgaui.server.addListener(listener = self.rgaui.update_fil, source = None, ID = self.rgaui.FILSIGNALID)
            yield self.rgaui.server.addListener(listener = self.rgaui.update_ml, source = None, ID = self.rgaui.MLSIGNALID)
            yield self.rgaui.server.addListener(listener = self.rgaui.update_hv, source = None, ID = self.rgaui.HVSIGNALID)
            yield self.rgaui.server.addListener(listener = self.rgaui.update_buf, source = None, ID = self.rgaui.BUFSIGNALID)
            yield self.rgaui.server.addListener(listener = self.rgaui.update_que, source = None, ID = self.rgaui.QUESIGNALID)
            self.rgaui.signal_connect()
        
        self.savdirui = SaveDirectory_UI()      #instantiates extra GUI's
        self.massspecui = MassSpecExperiment_UI()
        self.commui = CommandLine_UI()
        self.timeui = Timers_UI()
        self.dataui = DataLog_UI()
        if True:
            self.autoconnect_button.setDisabled(True)
            self.autoconnect_button.setText("Connected")
            self.host_name_text.setDisabled(True)
            self.lc_power_supply_id_spinbox.setDisabled(True)
            self.lc_power_supply_id_spinbox.setDisabled(True)
            self.setup_experiment()
        yield None
    def panel_update_test(self,c,signal):
        if signal == 'scanning':
            self.scaui.frame_1.setDisabled(True)
            self.scaui.frame_2.setDisabled(True)
        elif signal == 'paused':
            self.scaui.frame_1.setDisabled(True)
            self.scaui.frame_2.setEnabled(True)
        elif signal == 'cleared':
            self.scaui.frame_1.setEnabled(True)
            self.scaui.frame_2.setEnabled(True)
            self.scaui.sca_progress_bar.setValue(0)
    @inlineCallbacks
    def setup_experiment(self):
        """Embeds, sets up, and orients the individual widgets into the main window.
        Resizes and centers window, then calls .experiment_signal_connect()
        """
        self.hpui.setParent(self)   #embeds widgets inside window
        self.scaui.setParent(self)
        self.savdirui.setParent(self)
        self.rgaui.setParent(self)
        self.massspecui.setParent(self)
        self.savdirui.setParent(self)
        self.commui.setParent(self)
        self.timeui.setParent(self)
        
        self.massspecui.setupUi()   #setupUi for widgets that do not self-setup on initialize
        self.savdirui.setupUi()
        self.commui.setupUi()
        self.timeui.setupUi()
        self.dataui.setupUi()
        
        #---Widget Orientation---#
        #Row 1#
        self.hpui.move(0,130)       #Column 1
        self.scaui.move(400,130)    #Column 2
        self.savdirui.move(800,130) #Column 3 Half-height
        self.timeui.move(800,130+150) #Column 3 Half-height
        #Row 1#
        
        #Row 2#
        self.rgaui.move(0,130+300)          #Column 1
        self.massspecui.move(400,130+300)   #Column 2
        self.commui.move(800,130+300)       #Column 3 Half-height
        #Row 2#
        #---Widget Orientation---#
        
        self.hpui.show()    #shows the widgets
        self.scaui.show()
        self.rgaui.show()
        self.massspecui.show()
        self.savdirui.show()
        self.timeui.show()
        self.commui.show()

        self.timeui.t_right_button.setText(_translate("Form", "Reset Timer", None))  #Sets up timer widget
        self.timeui.t_right_label.setText(_translate("Form", "User Timer", None))
        self.timeui.t_middle_button.setText(_translate("Form", "Start/Stop Timer", None))
        self.timeui.t_middle_label.setText(_translate("Form", "Experiment Timer", None))
        self.timeui.t_left_label.setText(_translate("Form", "Datapoint Counter", None))
        self.timeui.t_spinbox.hide()
        
        
        self.experiment_signal_connect()

        self.resize(self.width(),130+300*2) #resizes and centers the window
        screensize = [ctypes.windll.user32.GetSystemMetrics(0),ctypes.windll.user32.GetSystemMetrics(1)]
        windowsize = [self.width(),self.height()]
        screencenter = [(screensize[0]-windowsize[0])/2,(screensize[1]-windowsize[1])/2]
        self.move(screencenter[0],screencenter[1])

        dialog = QtGui.QFileDialog()    #Sets up the Save Directory widget
        dialog.setDirectory('Z:\Group_Share\Barium\Data')
        self.savdirui.sd_select_path_button.clicked.connect(lambda : self.savdirui.sd_save_path_select.setEditText(dialog.getExistingDirectory()))
                
        reactor.run()
        yield None
        
    @inlineCallbacks
    def experiment_signal_connect(self):
        """Connects PyQt4 signals to slots.  Sets up timers (currently, the timers run slower compared to real time)
        """
        self.massspecui.ms_calculate_time_button.clicked.connect(lambda :self.calculate_time())
        self.massspecui.ms_begin_experiment_button.clicked.connect(lambda :self.begin_experiment())
        self.massspecui.ms_show_data_log_button.clicked.connect(lambda :self.show_data())

        self.timer= QtCore.QTimer()                             #Required for timed_mass_loop
        self.timer.timeout.connect(lambda :self.timer_tick())   #Required for timed_mass_loop

        self.user_timer_i = 0                                   #User Timer
        self.user_timer=QtCore.QTimer()
        self.user_timer.timeout.connect(lambda :self.user_timer_tick()) 
        self.timeui.t_right_button.clicked.connect(lambda :self.user_timer_reset())
        self.timeui.t_middle_button.setCheckable(True)
        self.timeui.t_middle_button.toggled.connect(lambda state=self.timeui.t_middle_button.isChecked() :self.user_timer_toggle(state))

        self.experiment_timer_i = 0                             #Experiment Timer
        self.experiment_timer = QtCore.QTimer()
        self.experiment_timer.timeout.connect(lambda :self.experiment_timer_tick())

        self.commui.cl_command_button.clicked.connect(lambda :self.send_command())
        yield None
        
    @inlineCallbacks
    def calculate_time(self):
        """Calculates the count times
        """
        records_per_scan = self.scaui.sca_records_per_scan_spinbox.value()  #Gathers input values
        trigger_frequency = self.scaui.sca_trigger_frequency_lcd.value()
        command1 = 'mass_list='+str(self.massspecui.ms_mass_sweep_select.currentText())
        command2 = 'current_list='+str(self.massspecui.ms_current_sweep_select.currentText())
        exec command1
        exec command2
        mass_iterations = len(mass_list)
        current_iterations = len(current_list)
        sweep_iterations = self.massspecui.ms_iterations_spinbox.value()

        count_time_per_point = records_per_scan/trigger_frequency+1   #Performs calculations
        count_time_per_sweep = count_time_per_point*mass_iterations*current_iterations
        total_count_time = count_time_per_sweep*sweep_iterations

        self.massspecui.ms_count_time_per_point_lcd.display(count_time_per_point)   #Updates LCD screens
        self.massspecui.ms_count_time_per_sweep_lcd.display(count_time_per_sweep)
        self.massspecui.ms_total_count_time_lcd.display(total_count_time)
        time_list = [count_time_per_point, total_count_time]
        yield None
        returnValue(time_list)
                              
    @inlineCallbacks
    def prepare_experiment(self):#Called in the beginning of begin_experiment
        """Sets up the initial conditions for a data run.
        """
        command1 = 'self.mass_list = '+str(self.massspecui.ms_mass_sweep_select.currentText())
        command2 = 'self.current_list = '+str(self.massspecui.ms_current_sweep_select.currentText())
        exec str(command1)
        exec str(command2)
        self.experiment_time = 0 #For timer display
        self.datapoint = 0
        self.scaui.stop_scan()
        self.scaui.clear_scan()
        yield None
                              
    @inlineCallbacks
    def begin_experiment(self):
        """Executes the beginning of the datarun and disables frames
        """
        if self.hpui.ps_pulse_mode_checkbox.isChecked == True:
            print 'Turn off pulse mode before beginning experiment.'
            returnValue(None)
        self.prepare_experiment()
        self.hpui.set_voltage(20)
        
        time_list = yield self.calculate_time() #Obtains relevant values
        self.count_time_per_point = time_list[0]
        self.total_count_time = time_list[1]
        self.sweep_iterations = self.massspecui.ms_iterations_spinbox.value()

        self.results = np.array([[0,0,0,0,0,0,0,0,0]])
        self.experiment_timer.start(100)
        print 'Beginning experiment.  Avoid changing any parameters unless necessary!  (You can change the discriminator level)'
        self.dataui.ms_data_text.appendPlainText('Start of experiment.')
        self.experiment_iteration_loop(0) #Starts the top experimental loop
        self.show_data()

        self.hpui.frame.setDisabled(True)
        self.scaui.frame.setDisabled(True)
        self.rgaui.frame.setDisabled(True)
        self.massspecui.ms_begin_experiment_button.setDisabled(True)
        yield None
                              
    @inlineCallbacks
    def timed_mass_loop(self,i):                    #--This is the bottom experimental loop--#
        """This is called first in a mass sweep, starting the timer and the initial mass_loop_tasks() call
        """
        self.i=i
        self.timer.start(self.count_time_per_point*1000) #starts timer (timeout in miliseconds)
        self.mass_loop_tasks()
        yield None                              
    @inlineCallbacks
    def timer_tick(self):                           #--This is part of timed_mass_loop--#
        """This calls subsequent mass_loop_tasks() and checks when the mass list has been completely swept through
        """
        if self.i<len(self.mass_list):
            self.update_data()
            self.mass_loop_tasks()
        else:
            print 'Mass loop finished'
            self.update_data()
            self.timer.stop()
            self.current_loop(self.j) #calls next current_loop iteration
        yield None
    @inlineCallbacks
    def mass_loop_tasks(self):                      #--This is part of timed_mass_loop--#
        """This changes the mass on the RGA and begins a scan on the Scalar
        """
        mass = self.mass_list[self.i]
        print 'Setting mass to '+str(mass),'Mass list index: '+str(self.i)
        self.mass_data = mass
        self.hpui.update_indicators()
        self.rgaui.set_mass_lock(mass)
        self.scaui.clear_scan()
        self.scaui.start_scan()
        self.i += 1
        yield None
                              
    @inlineCallbacks
    def current_loop(self,j):                       #--This is the middle experimental loop--#
        """This sets the next current and initiates a new mass sweep.  Or it calls the next experiment iteration
        when the current list has been swept through
        """
        self.j=j
        if self.j<len(self.current_list):
            current = self.current_list[self.j]
            print 'Setting current to '+str(current),'Current list index: '+str(self.j)
            self.hpui.set_current(current)
            self.current_data = current
            self.timed_mass_loop(0) #calls new timed_mass_loop
            self.j+=1
        else:
            print 'Current loop finished'
            self.experiment_iteration_loop(self.k) #calls next experimental_iteration_loop iteration
        yield None
                              
    @inlineCallbacks
    def experiment_iteration_loop(self,k):          #--This is the top experimental loop--#
        """This calls new current loops and repeats depending on the number of iterations set by the user.
        """
        self.k = k
        if self.k < self.sweep_iterations:
            print 'Loop iteration: '+str(self.k)
            self.iteration_data = self.k
            self.current_loop(0) #calls new current_loop
            self.k+=1
        else:
            self.hpui.set_current(0)
            print 'Experiment Finished'
            self.scaui.stop_scan()
            self.experiment_timer.stop()
            self.hpui.frame.setDisabled(False)
            self.scaui.frame.setDisabled(False)
            self.rgaui.frame.setDisabled(False)
            self.massspecui.ms_begin_experiment_button.setDisabled(False)
        yield None
                              
    @inlineCallbacks
    def update_data(self):  #Updates and saves data
        """Reads the counts from the Scalar and saves it into a text file.
        """
        print 'Generating data...'

        self.timeui.t_left_lcd.display(self.datapoint)
        
        filepath = self.savdirui.sd_save_path_select.currentText()
        filename = self.savdirui.sd_filename_text.text()

        mass = self.mass_data
        current = self.current_data
        iteration = self.iteration_data
        integration_time = self.scaui.integration_time
        
        yield self.scaui.get_counts()
        counts = self.scaui.sca_counts_lcd.value()
        t = datetime.now().timetuple()
        voltage = yield self.hpui.get_voltage()
        current = yield self.hpui.get_current()
        new_data = np.array([[mass,counts,t[2],t[3],t[4],t[5],voltage,current,integration_time]])
        self.dataui.ms_data_text.appendPlainText(str(self.datapoint)+","+str(new_data))
        self.results = np.concatenate((self.results,new_data),axis=0)
        np.savetxt(str(filepath+'\\'+filename),self.results,fmt="%0.5e")
        self.datapoint+=1
        
    @inlineCallbacks
    def experiment_timer_tick(self):    #Experiment Timer Function
        self.experiment_time += 1
        self.timeui.t_middle_lcd.display(float(self.experiment_time)/10)
        yield None
    @inlineCallbacks
    def show_data(self):
        """Shows the data log GUI with the experimental data that has been logged.
        """
        screensize = [ctypes.windll.user32.GetSystemMetrics(0),ctypes.windll.user32.GetSystemMetrics(1)]
        windowsize = [self.dataui.width(),self.dataui.height()]
        screencenter = [(screensize[0]-windowsize[0])/2,(screensize[1]-windowsize[1])/2]
        self.dataui.move(screencenter[0],screencenter[1])
        self.dataui.show()
        yield None
        
    @inlineCallbacks
    def user_timer_toggle(self, state): #User Timer Functions
        if state == True:
            self.user_timer.start(100)
        elif state == False:
            self.user_timer.stop()
        yield None
    @inlineCallbacks
    def user_timer_tick(self):
        self.user_timer_i += 1
        self.timeui.t_right_lcd.display(float(self.user_timer_i)/10)
        yield None
    @inlineCallbacks
    def user_timer_reset(self):
        self.user_timer_i = 0
        self.timeui.t_right_lcd.display(0)
        yield None
        
    @inlineCallbacks
    def send_command(self):             #Command Line Functions
        """Sends command from the Command Line GUI.
        """
        command = str(self.commui.cl_command_text.toPlainText())
        exec command
        yield None

    #Close Event:
    @inlineCallbacks
    def closeEvent(self, x):
        self.hpui.set_current(0)
        self.hpui.set_voltage(0)
        self.scaui.stop_scan()
        self.rgaui.set_filament_state(False)
        self.rgaui.set_voltage(0)
        yield None
        reactor.stop()

import sys

if __name__ == "__main__":
    a = QtGui.QApplication ([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    client = Mass_Spec_Client(reactor)
    client.show()
    
    sys.exit(a.exec_())
