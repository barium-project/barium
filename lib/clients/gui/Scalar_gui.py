# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Z:\Group_Share\Barium\Users\Calvin\Dev\GUIs\Scalar_gui.ui'
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

class Scalar_UI(QtGui.QWidget):
    def setupUi(self):
        Form = self
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(400, 300)
        self.frame = QtGui.QFrame(Form)
        self.frame.setGeometry(QtCore.QRect(10, 10, 381, 281))
        self.frame.setFrameShape(QtGui.QFrame.Box)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.label = QtGui.QLabel(self.frame)
        self.label.setGeometry(QtCore.QRect(20, 0, 231, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.sca_stop_scan_button = QtGui.QPushButton(self.frame)
        self.sca_stop_scan_button.setEnabled(True)
        self.sca_stop_scan_button.setGeometry(QtCore.QRect(290, 160, 81, 31))
        self.sca_stop_scan_button.setObjectName(_fromUtf8("sca_stop_scan_button"))
        self.sca_get_counts_button = QtGui.QPushButton(self.frame)
        self.sca_get_counts_button.setGeometry(QtCore.QRect(20, 210, 81, 61))
        self.sca_get_counts_button.setObjectName(_fromUtf8("sca_get_counts_button"))
        self.sca_counts_lcd = QtGui.QLCDNumber(self.frame)
        self.sca_counts_lcd.setGeometry(QtCore.QRect(110, 210, 261, 61))
        self.sca_counts_lcd.setObjectName(_fromUtf8("sca_counts_lcd"))
        self.frame_2 = QtGui.QFrame(self.frame)
        self.frame_2.setGeometry(QtCore.QRect(10, 150, 271, 51))
        self.frame_2.setFrameShape(QtGui.QFrame.Panel)
        self.frame_2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_2.setObjectName(_fromUtf8("frame_2"))
        self.sca_clear_scan_button = QtGui.QPushButton(self.frame_2)
        self.sca_clear_scan_button.setGeometry(QtCore.QRect(190, 10, 71, 31))
        self.sca_clear_scan_button.setObjectName(_fromUtf8("sca_clear_scan_button"))
        self.sca_start_scan_button = QtGui.QPushButton(self.frame_2)
        self.sca_start_scan_button.setGeometry(QtCore.QRect(110, 10, 71, 31))
        self.sca_start_scan_button.setCheckable(False)
        self.sca_start_scan_button.setObjectName(_fromUtf8("sca_start_scan_button"))
        self.sca_start_new_scan_button = QtGui.QPushButton(self.frame_2)
        self.sca_start_new_scan_button.setGeometry(QtCore.QRect(10, 10, 91, 31))
        self.sca_start_new_scan_button.setCheckable(False)
        self.sca_start_new_scan_button.setObjectName(_fromUtf8("sca_start_new_scan_button"))
        self.frame_1 = QtGui.QFrame(self.frame)
        self.frame_1.setGeometry(QtCore.QRect(10, 40, 361, 101))
        self.frame_1.setFrameShape(QtGui.QFrame.Panel)
        self.frame_1.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_1.setObjectName(_fromUtf8("frame_1"))
        self.label_2 = QtGui.QLabel(self.frame_1)
        self.label_2.setGeometry(QtCore.QRect(10, 0, 131, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_5 = QtGui.QLabel(self.frame_1)
        self.label_5.setGeometry(QtCore.QRect(180, 50, 91, 16))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.label_3 = QtGui.QLabel(self.frame_1)
        self.label_3.setGeometry(QtCore.QRect(10, 50, 71, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.sca_discriminator_level_spinbox = QtGui.QSpinBox(self.frame_1)
        self.sca_discriminator_level_spinbox.setGeometry(QtCore.QRect(180, 20, 71, 22))
        self.sca_discriminator_level_spinbox.setMaximum(300)
        self.sca_discriminator_level_spinbox.setProperty("value", 220)
        self.sca_discriminator_level_spinbox.setObjectName(_fromUtf8("sca_discriminator_level_spinbox"))
        self.sca_bins_per_record_lcd = QtGui.QLCDNumber(self.frame_1)
        self.sca_bins_per_record_lcd.setGeometry(QtCore.QRect(83, 20, 71, 23))
        self.sca_bins_per_record_lcd.setObjectName(_fromUtf8("sca_bins_per_record_lcd"))
        self.sca_bin_width_lcd = QtGui.QLCDNumber(self.frame_1)
        self.sca_bin_width_lcd.setGeometry(QtCore.QRect(83, 70, 71, 23))
        self.sca_bin_width_lcd.setObjectName(_fromUtf8("sca_bin_width_lcd"))
        self.sca_records_per_scan_spinbox = QtGui.QSpinBox(self.frame_1)
        self.sca_records_per_scan_spinbox.setGeometry(QtCore.QRect(180, 70, 71, 22))
        self.sca_records_per_scan_spinbox.setMaximum(2000)
        self.sca_records_per_scan_spinbox.setSingleStep(50)
        self.sca_records_per_scan_spinbox.setProperty("value", 500)
        self.sca_records_per_scan_spinbox.setObjectName(_fromUtf8("sca_records_per_scan_spinbox"))
        self.label_4 = QtGui.QLabel(self.frame_1)
        self.label_4.setGeometry(QtCore.QRect(180, 0, 121, 20))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.sca_bin_width_select = QtGui.QComboBox(self.frame_1)
        self.sca_bin_width_select.setGeometry(QtCore.QRect(10, 70, 71, 22))
        self.sca_bin_width_select.setMaxVisibleItems(20)
        self.sca_bin_width_select.setObjectName(_fromUtf8("sca_bin_width_select"))
        self.sca_bin_width_select.addItem(_fromUtf8(""))
        self.sca_bin_width_select.addItem(_fromUtf8(""))
        self.sca_bin_width_select.addItem(_fromUtf8(""))
        self.sca_bin_width_select.addItem(_fromUtf8(""))
        self.sca_bin_width_select.addItem(_fromUtf8(""))
        self.sca_bin_width_select.addItem(_fromUtf8(""))
        self.sca_bin_width_select.addItem(_fromUtf8(""))
        self.sca_bin_width_select.addItem(_fromUtf8(""))
        self.sca_bin_width_select.addItem(_fromUtf8(""))
        self.sca_bin_width_select.addItem(_fromUtf8(""))
        self.sca_bin_width_select.addItem(_fromUtf8(""))
        self.sca_bin_width_select.addItem(_fromUtf8(""))
        self.sca_bin_width_select.addItem(_fromUtf8(""))
        self.sca_bin_width_select.addItem(_fromUtf8(""))
        self.sca_bin_width_select.addItem(_fromUtf8(""))
        self.sca_bin_width_select.addItem(_fromUtf8(""))
        self.sca_bin_width_select.addItem(_fromUtf8(""))
        self.sca_bin_width_select.addItem(_fromUtf8(""))
        self.sca_bin_width_select.addItem(_fromUtf8(""))
        self.sca_bin_width_select.addItem(_fromUtf8(""))
        self.sca_bins_per_record_select = QtGui.QComboBox(self.frame_1)
        self.sca_bins_per_record_select.setGeometry(QtCore.QRect(10, 20, 71, 22))
        self.sca_bins_per_record_select.setEditable(False)
        self.sca_bins_per_record_select.setMaxVisibleItems(16)
        self.sca_bins_per_record_select.setObjectName(_fromUtf8("sca_bins_per_record_select"))
        self.sca_bins_per_record_select.addItem(_fromUtf8(""))
        self.sca_bins_per_record_select.addItem(_fromUtf8(""))
        self.sca_bins_per_record_select.addItem(_fromUtf8(""))
        self.sca_bins_per_record_select.addItem(_fromUtf8(""))
        self.sca_bins_per_record_select.addItem(_fromUtf8(""))
        self.sca_bins_per_record_select.addItem(_fromUtf8(""))
        self.sca_bins_per_record_select.addItem(_fromUtf8(""))
        self.sca_bins_per_record_select.addItem(_fromUtf8(""))
        self.sca_bins_per_record_select.addItem(_fromUtf8(""))
        self.sca_bins_per_record_select.addItem(_fromUtf8(""))
        self.sca_bins_per_record_select.addItem(_fromUtf8(""))
        self.sca_bins_per_record_select.addItem(_fromUtf8(""))
        self.sca_bins_per_record_select.addItem(_fromUtf8(""))
        self.sca_bins_per_record_select.addItem(_fromUtf8(""))
        self.sca_bins_per_record_select.addItem(_fromUtf8(""))
        self.sca_bins_per_record_select.addItem(_fromUtf8(""))
        self.label_6 = QtGui.QLabel(self.frame)
        self.label_6.setGeometry(QtCore.QRect(30, 160, 131, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.label_6.raise_()
        self.frame_1.raise_()
        self.frame_2.raise_()
        self.label.raise_()
        self.sca_stop_scan_button.raise_()
        self.sca_get_counts_button.raise_()
        self.sca_counts_lcd.raise_()

        self.retranslateUi()
        self.sca_bin_width_select.setCurrentIndex(13)
        QtCore.QObject.connect(self.sca_start_new_scan_button, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.frame_2.setEnabled)
        QtCore.QObject.connect(self.sca_start_scan_button, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.frame_2.setEnabled)
        QtCore.QObject.connect(self.sca_stop_scan_button, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.frame_2.setDisabled)
        QtCore.QObject.connect(self.sca_start_new_scan_button, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.frame_1.setEnabled)
        QtCore.QObject.connect(self.sca_start_scan_button, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.frame_1.setEnabled)
        QtCore.QObject.connect(self.sca_stop_scan_button, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.frame_1.setDisabled)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self):
        Form = self
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.label.setText(_translate("Form", "SR430 Multichannel Scalar", None))
        self.sca_stop_scan_button.setText(_translate("Form", "Stop Scan", None))
        self.sca_get_counts_button.setText(_translate("Form", "Get Counts", None))
        self.sca_clear_scan_button.setText(_translate("Form", "Clear Scan", None))
        self.sca_start_scan_button.setText(_translate("Form", "Start Scan", None))
        self.sca_start_new_scan_button.setText(_translate("Form", "Start New Scan", None))
        self.label_2.setText(_translate("Form", "Bins Per Record", None))
        self.label_5.setText(_translate("Form", "Records Per Scan", None))
        self.label_3.setText(_translate("Form", "Bin Width (ns)", None))
        self.label_4.setText(_translate("Form", "Discriminator Level (mV)", None))
        self.sca_bin_width_select.setItemText(0, _translate("Form", "5", None))
        self.sca_bin_width_select.setItemText(1, _translate("Form", "40", None))
        self.sca_bin_width_select.setItemText(2, _translate("Form", "80", None))
        self.sca_bin_width_select.setItemText(3, _translate("Form", "160", None))
        self.sca_bin_width_select.setItemText(4, _translate("Form", "320", None))
        self.sca_bin_width_select.setItemText(5, _translate("Form", "640", None))
        self.sca_bin_width_select.setItemText(6, _translate("Form", "1280", None))
        self.sca_bin_width_select.setItemText(7, _translate("Form", "2560", None))
        self.sca_bin_width_select.setItemText(8, _translate("Form", "5120", None))
        self.sca_bin_width_select.setItemText(9, _translate("Form", "10240", None))
        self.sca_bin_width_select.setItemText(10, _translate("Form", "20480", None))
        self.sca_bin_width_select.setItemText(11, _translate("Form", "40960", None))
        self.sca_bin_width_select.setItemText(12, _translate("Form", "81920", None))
        self.sca_bin_width_select.setItemText(13, _translate("Form", "163840", None))
        self.sca_bin_width_select.setItemText(14, _translate("Form", "327680", None))
        self.sca_bin_width_select.setItemText(15, _translate("Form", "655360", None))
        self.sca_bin_width_select.setItemText(16, _translate("Form", "1310700", None))
        self.sca_bin_width_select.setItemText(17, _translate("Form", "2621400", None))
        self.sca_bin_width_select.setItemText(18, _translate("Form", "5242900", None))
        self.sca_bin_width_select.setItemText(19, _translate("Form", "10486000", None))
        self.sca_bins_per_record_select.setItemText(0, _translate("Form", "1024", None))
        self.sca_bins_per_record_select.setItemText(1, _translate("Form", "2048", None))
        self.sca_bins_per_record_select.setItemText(2, _translate("Form", "3072", None))
        self.sca_bins_per_record_select.setItemText(3, _translate("Form", "4096", None))
        self.sca_bins_per_record_select.setItemText(4, _translate("Form", "5120", None))
        self.sca_bins_per_record_select.setItemText(5, _translate("Form", "6144", None))
        self.sca_bins_per_record_select.setItemText(6, _translate("Form", "7168", None))
        self.sca_bins_per_record_select.setItemText(7, _translate("Form", "8192", None))
        self.sca_bins_per_record_select.setItemText(8, _translate("Form", "9216", None))
        self.sca_bins_per_record_select.setItemText(9, _translate("Form", "10240", None))
        self.sca_bins_per_record_select.setItemText(10, _translate("Form", "11264", None))
        self.sca_bins_per_record_select.setItemText(11, _translate("Form", "12288", None))
        self.sca_bins_per_record_select.setItemText(12, _translate("Form", "13312", None))
        self.sca_bins_per_record_select.setItemText(13, _translate("Form", "14336", None))
        self.sca_bins_per_record_select.setItemText(14, _translate("Form", "15360", None))
        self.sca_bins_per_record_select.setItemText(15, _translate("Form", "16384", None))
        self.label_6.setText(_translate("Form", "Scanning...", None))

