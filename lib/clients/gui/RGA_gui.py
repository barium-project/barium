# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Z:\Group_Share\Barium\Users\Calvin\Dev\GUIs\RGA_gui.ui'
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

class RGA_UI(QtGui.QWidget):
    def setupUi(self):
        Form = self
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(400, 300)
        self.frame = QtGui.QFrame(Form)
        self.frame.setGeometry(QtCore.QRect(10, 10, 381, 281))
        self.frame.setFrameShape(QtGui.QFrame.Box)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.rga_filament_checkbox = QtGui.QCheckBox(self.frame)
        self.rga_filament_checkbox.setGeometry(QtCore.QRect(10, 40, 81, 41))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.rga_filament_checkbox.setFont(font)
        self.rga_filament_checkbox.setTristate(False)
        self.rga_filament_checkbox.setObjectName(_fromUtf8("rga_filament_checkbox"))
        self.label_2 = QtGui.QLabel(self.frame)
        self.label_2.setGeometry(QtCore.QRect(10, 90, 221, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.label_2.setFont(font)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.rga_filament_lcd = QtGui.QLCDNumber(self.frame)
        self.rga_filament_lcd.setGeometry(QtCore.QRect(210, 40, 161, 41))
        self.rga_filament_lcd.setObjectName(_fromUtf8("rga_filament_lcd"))
        self.label_3 = QtGui.QLabel(self.frame)
        self.label_3.setGeometry(QtCore.QRect(10, 170, 131, 16))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.label_3.setFont(font)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.rga_voltage_spinbox = QtGui.QSpinBox(self.frame)
        self.rga_voltage_spinbox.setGeometry(QtCore.QRect(10, 110, 191, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.rga_voltage_spinbox.setFont(font)
        self.rga_voltage_spinbox.setMaximum(2200)
        self.rga_voltage_spinbox.setSingleStep(200)
        self.rga_voltage_spinbox.setObjectName(_fromUtf8("rga_voltage_spinbox"))
        self.label = QtGui.QLabel(self.frame)
        self.label.setGeometry(QtCore.QRect(10, 0, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.rga_voltage_lcd = QtGui.QLCDNumber(self.frame)
        self.rga_voltage_lcd.setGeometry(QtCore.QRect(210, 110, 161, 41))
        self.rga_voltage_lcd.setObjectName(_fromUtf8("rga_voltage_lcd"))
        self.rga_id_text = QtGui.QLineEdit(self.frame)
        self.rga_id_text.setGeometry(QtCore.QRect(10, 250, 361, 20))
        self.rga_id_text.setReadOnly(True)
        self.rga_id_text.setObjectName(_fromUtf8("rga_id_text"))
        self.rga_id_button = QtGui.QPushButton(self.frame)
        self.rga_id_button.setGeometry(QtCore.QRect(274, 190, 91, 51))
        self.rga_id_button.setObjectName(_fromUtf8("rga_id_button"))
        self.rga_mass_lock_spinbox = QtGui.QDoubleSpinBox(self.frame)
        self.rga_mass_lock_spinbox.setGeometry(QtCore.QRect(10, 190, 191, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.rga_mass_lock_spinbox.setFont(font)
        self.rga_mass_lock_spinbox.setMaximum(250.0)
        self.rga_mass_lock_spinbox.setSingleStep(0.5)
        self.rga_mass_lock_spinbox.setProperty("value", 133.0)
        self.rga_mass_lock_spinbox.setObjectName(_fromUtf8("rga_mass_lock_spinbox"))

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self):
        Form = self
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.rga_filament_checkbox.setText(_translate("Form", "Filament", None))
        self.label_2.setText(_translate("Form", "Electronmultiplier Voltage (V)", None))
        self.label_3.setText(_translate("Form", "Mass Lock (AMU)", None))
        self.label.setText(_translate("Form", "RGA Client", None))
        self.rga_id_button.setText(_translate("Form", "ID?", None))

