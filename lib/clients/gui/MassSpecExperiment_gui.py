# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\barium133\Code\barium\lib\clients\gui\MassSpecExperiment_gui.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

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

class MassSpecExperiment_UI(QtGui.QWidget):
    def setupUi(self):
        Form = self
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(400, 300)
        self.frame = QtGui.QFrame(Form)
        self.frame.setGeometry(QtCore.QRect(10, 10, 381, 281))
        self.frame.setToolTip(_fromUtf8(""))
        self.frame.setFrameShape(QtGui.QFrame.Box)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.label = QtGui.QLabel(self.frame)
        self.label.setGeometry(QtCore.QRect(10, 10, 261, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.ms_count_time_per_point_lcd = QtGui.QLCDNumber(self.frame)
        self.ms_count_time_per_point_lcd.setGeometry(QtCore.QRect(20, 210, 101, 23))
        self.ms_count_time_per_point_lcd.setObjectName(_fromUtf8("ms_count_time_per_point_lcd"))
        self.ms_iterations_spinbox = QtGui.QSpinBox(self.frame)
        self.ms_iterations_spinbox.setGeometry(QtCore.QRect(10, 160, 101, 22))
        self.ms_iterations_spinbox.setProperty("value", 1)
        self.ms_iterations_spinbox.setObjectName(_fromUtf8("ms_iterations_spinbox"))
        self.label_20 = QtGui.QLabel(self.frame)
        self.label_20.setGeometry(QtCore.QRect(260, 190, 91, 16))
        self.label_20.setObjectName(_fromUtf8("label_20"))
        self.ms_mass_sweep_select = QtGui.QComboBox(self.frame)
        self.ms_mass_sweep_select.setGeometry(QtCore.QRect(10, 60, 361, 22))
        self.ms_mass_sweep_select.setEditable(True)
        self.ms_mass_sweep_select.setObjectName(_fromUtf8("ms_mass_sweep_select"))
        self.ms_mass_sweep_select.addItem(_fromUtf8(""))
        self.ms_mass_sweep_select.addItem(_fromUtf8(""))
        self.ms_mass_sweep_select.addItem(_fromUtf8(""))
        self.label_18 = QtGui.QLabel(self.frame)
        self.label_18.setGeometry(QtCore.QRect(20, 190, 111, 16))
        self.label_18.setObjectName(_fromUtf8("label_18"))
        self.ms_begin_experiment_button = QtGui.QPushButton(self.frame)
        self.ms_begin_experiment_button.setGeometry(QtCore.QRect(200, 240, 171, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.ms_begin_experiment_button.setFont(font)
        self.ms_begin_experiment_button.setCheckable(True)
        self.ms_begin_experiment_button.setObjectName(_fromUtf8("ms_begin_experiment_button"))
        self.ms_calculate_time_button = QtGui.QPushButton(self.frame)
        self.ms_calculate_time_button.setGeometry(QtCore.QRect(260, 150, 101, 31))
        self.ms_calculate_time_button.setObjectName(_fromUtf8("ms_calculate_time_button"))
        self.ms_total_count_time_lcd = QtGui.QLCDNumber(self.frame)
        self.ms_total_count_time_lcd.setGeometry(QtCore.QRect(260, 210, 101, 23))
        self.ms_total_count_time_lcd.setObjectName(_fromUtf8("ms_total_count_time_lcd"))
        self.label_15 = QtGui.QLabel(self.frame)
        self.label_15.setGeometry(QtCore.QRect(10, 40, 121, 16))
        self.label_15.setObjectName(_fromUtf8("label_15"))
        self.label_21 = QtGui.QLabel(self.frame)
        self.label_21.setGeometry(QtCore.QRect(10, 140, 91, 16))
        self.label_21.setObjectName(_fromUtf8("label_21"))
        self.ms_count_time_per_sweep_lcd = QtGui.QLCDNumber(self.frame)
        self.ms_count_time_per_sweep_lcd.setGeometry(QtCore.QRect(140, 210, 101, 23))
        self.ms_count_time_per_sweep_lcd.setObjectName(_fromUtf8("ms_count_time_per_sweep_lcd"))
        self.label_22 = QtGui.QLabel(self.frame)
        self.label_22.setGeometry(QtCore.QRect(140, 190, 121, 16))
        self.label_22.setObjectName(_fromUtf8("label_22"))
        self.ms_current_sweep_select = QtGui.QComboBox(self.frame)
        self.ms_current_sweep_select.setGeometry(QtCore.QRect(10, 110, 361, 22))
        self.ms_current_sweep_select.setEditable(True)
        self.ms_current_sweep_select.setObjectName(_fromUtf8("ms_current_sweep_select"))
        self.ms_current_sweep_select.addItem(_fromUtf8(""))
        self.ms_current_sweep_select.addItem(_fromUtf8(""))
        self.label_2 = QtGui.QLabel(self.frame)
        self.label_2.setGeometry(QtCore.QRect(10, 90, 151, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.ms_show_data_log_button = QtGui.QPushButton(self.frame)
        self.ms_show_data_log_button.setGeometry(QtCore.QRect(10, 240, 171, 31))
        self.ms_show_data_log_button.setObjectName(_fromUtf8("ms_show_data_log_button"))

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self):
        Form = self
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.label.setToolTip(_translate("Form", "<html><head/><body><p>The Mass Spectrum Experiment takes a mass spectrum of the ions emitted by the ion</p><p>source using the RGA as a detector, the Scalar as a counter, and a power supply as the</p><p>power source for heating the ion source (a platinum filament).</p><p><br/></p><p>The data collected are of the following format:</p><p>[[Mass, Counts, Day, Hour, Minute, Second, Power Supply Voltage, Power Supply Current]]</p><p><br/></p><p>Sweeping through a list of masses allows a mass spectrum to be created.</p><p>Sweeping through a list of masses over multiple iterations allows the spectrum\'s time</p><p>dependence to be observed.</p></body></html>", None))
        self.label.setText(_translate("Form", "Mass Spectrum Experiment", None))
        self.ms_count_time_per_point_lcd.setToolTip(_translate("Form", "<html><head/><body><p>Time it takes to take counts for one mass</p><p>(=records_per_scan/trigger_frequency+wait_time)</p></body></html>", None))
        self.label_20.setText(_translate("Form", "Total Count Time", None))
        self.ms_mass_sweep_select.setItemText(0, _translate("Form", "[23,39,133,138]", None))
        self.ms_mass_sweep_select.setItemText(1, _translate("Form", "[130,131,132,133,134,135,136,137,138,139,140]", None))
        self.ms_mass_sweep_select.setItemText(2, _translate("Form", "[130,130.5,131,131,5,132,132.5,133,133.5,134,134.5,135,135.5,136,136.5,137,137.5,138,138.5,139,139.5,140]", None))
        self.label_18.setText(_translate("Form", "Count Time Per Point", None))
        self.ms_begin_experiment_button.setToolTip(_translate("Form", "<html><head/><body><p>Begin Mass Spectrum Experiment</p></body></html>", None))
        self.ms_begin_experiment_button.setText(_translate("Form", "Begin Experiment", None))
        self.ms_calculate_time_button.setToolTip(_translate("Form", "<html><head/><body><p>Calculates the time values and displays them above</p></body></html>", None))
        self.ms_calculate_time_button.setText(_translate("Form", "Calculate Time", None))
        self.ms_total_count_time_lcd.setToolTip(_translate("Form", "<html><head/><body><p>Total time to complete data run</p><p>(=iterations*count_time_per_sweep)</p></body></html>", None))
        self.label_15.setText(_translate("Form", "Mass Sweep List (AMU)", None))
        self.label_21.setText(_translate("Form", "Sweep Iterations", None))
        self.ms_count_time_per_sweep_lcd.setToolTip(_translate("Form", "<html><head/><body><p>Time it takes to sweep through the mass list</p><p>(=len(mass_sweep_list)*count_time_per_point)</p></body></html>", None))
        self.label_22.setText(_translate("Form", "Count Time Per Sweep", None))
        self.ms_current_sweep_select.setToolTip(_translate("Form", "List of current values to sweep over (or single value for a constant current)", None))
        self.ms_current_sweep_select.setItemText(0, _translate("Form", "[12]", None))
        self.ms_current_sweep_select.setItemText(1, _translate("Form", "[10,10.25,10.50,10.75,11,11.25,11.50,11.75,12.00,12.25,12.50,12.75,13,13.25,13.50]", None))
        self.label_2.setText(_translate("Form", "Currrent Sweep List (A)", None))
        self.ms_show_data_log_button.setText(_translate("Form", "Show Data Log ...", None))

